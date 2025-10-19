"""
归因计算批处理任务
"""
from celery import Celery
from app.engines.attribution_engine import ShapleyAttribution, AttributionOptimizer
from app.clickhouse import get_clickhouse_client
import logging
from typing import List, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# 创建Celery应用
app = Celery('bmos', broker='redis://localhost:6379/0')

@app.task
def compute_order_attribution(order_id: str) -> Dict:
    """计算单个订单的归因权重"""
    try:
        client = get_clickhouse_client()
        
        # 1. 获取订单触点旅程
        query = f"""
            SELECT 
                media_id, 
                touchpoint_time, 
                cvrs_score,
                cost
            FROM bridge_attribution ba
            JOIN fact_voice fv ON ba.media_id = fv.vpt_id
            WHERE ba.order_id = '{order_id}'
            ORDER BY ba.touchpoint_time
        """
        touchpoints_data = client.execute(query)
        
        if not touchpoints_data:
            logger.warning(f"订单 {order_id} 没有找到触点数据")
            return {'order_id': order_id, 'attribution': {}}
        
        # 2. 获取订单金额
        order_query = f"SELECT amt FROM fact_order WHERE order_id = '{order_id}'"
        order_data = client.execute(order_query)
        
        if not order_data:
            logger.warning(f"订单 {order_id} 没有找到金额数据")
            return {'order_id': order_id, 'attribution': {}}
        
        conversion_value = float(order_data[0][0])
        
        # 3. 构建触点数据
        touchpoints = []
        for row in touchpoints_data:
            touchpoints.append({
                'media_id': row[0],
                'touchpoint_time': row[1],
                'cvrs_score': float(row[2]) if row[2] else 3.0,
                'cost': float(row[3]) if row[3] else 0.0
            })
        
        # 4. 计算Shapley归因
        optimizer = AttributionOptimizer()
        n_samples = optimizer.optimize_sampling_size(len(touchpoints))
        
        engine = ShapleyAttribution(n_samples=n_samples)
        attribution = engine.calculate_attribution(touchpoints, conversion_value)
        
        # 5. 验证结果
        if not optimizer.validate_attribution(attribution):
            logger.error(f"订单 {order_id} 归因结果验证失败")
            return {'order_id': order_id, 'attribution': {}}
        
        # 6. 更新bridge_attribution表
        for seq, (media_id, weight) in enumerate(attribution.items()):
            update_query = f"""
                INSERT INTO bridge_attribution VALUES
                ('{order_id}', '{media_id}', '', {weight}, {seq}, now(), now())
            """
            client.execute(update_query)
        
        logger.info(f"订单 {order_id} 归因计算完成，触点数量: {len(touchpoints)}")
        return {
            'order_id': order_id,
            'attribution': attribution,
            'touchpoint_count': len(touchpoints),
            'conversion_value': conversion_value
        }
        
    except Exception as e:
        logger.error(f"订单 {order_id} 归因计算失败: {e}")
        return {'order_id': order_id, 'error': str(e)}

@app.task
def batch_compute_attribution(order_ids: List[str]) -> List[Dict]:
    """批量计算订单归因"""
    results = []
    
    for order_id in order_ids:
        result = compute_order_attribution.delay(order_id)
        results.append(result.get())
    
    logger.info(f"批量归因计算完成，处理订单数: {len(order_ids)}")
    return results

@app.task
def daily_attribution_recalculation():
    """每日归因重计算任务（凌晨2点运行）"""
    try:
        client = get_clickhouse_client()
        
        # 获取过去7天的新订单
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        query = f"""
            SELECT order_id
            FROM fact_order
            WHERE date_key >= '{seven_days_ago}'
            AND order_id NOT IN (
                SELECT DISTINCT order_id 
                FROM bridge_attribution 
                WHERE update_time >= '{seven_days_ago}'
            )
        """
        
        new_orders = client.execute(query)
        order_ids = [row[0] for row in new_orders]
        
        if order_ids:
            logger.info(f"发现 {len(order_ids)} 个新订单需要计算归因")
            
            # 分批处理，每批100个订单
            batch_size = 100
            for i in range(0, len(order_ids), batch_size):
                batch = order_ids[i:i + batch_size]
                batch_compute_attribution.delay(batch)
            
            logger.info(f"已提交 {len(order_ids)} 个订单的归因计算任务")
        else:
            logger.info("没有新订单需要计算归因")
            
    except Exception as e:
        logger.error(f"每日归因重计算任务失败: {e}")

@app.task
def retrain_conversion_model():
    """重训练转化预测模型（每周日凌晨3点运行）"""
    try:
        from sklearn.ensemble import GradientBoostingClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score
        import pandas as pd
        import os
        
        client = get_clickhouse_client()
        
        # 获取训练数据
        query = """
            SELECT 
                len(coalition) / total_touchpoints as coverage,
                avg(cvrs_score) as avg_cvrs,
                max(cost) as max_cost,
                has(media_list, 'organic') as has_organic,
                sequence_weight,
                CASE WHEN conversion_happened THEN 1 ELSE 0 END as label
            FROM (
                SELECT 
                    order_id,
                    groupArray(media_id) as media_list,
                    groupArray(cvrs_score) as cvrs_score,
                    groupArray(cost) as cost,
                    count() as total_touchpoints,
                    max(touchpoint_time) - min(touchpoint_time) as sequence_weight,
                    countIf(conversion_happened) > 0 as conversion_happened
                FROM bridge_attribution ba
                JOIN fact_order fo ON ba.order_id = fo.order_id
                WHERE ba.update_time >= today() - INTERVAL 30 DAY
                GROUP BY order_id
            )
        """
        
        data = client.execute(query)
        
        if len(data) < 1000:  # 数据不足，跳过训练
            logger.warning("训练数据不足，跳过模型重训练")
            return
        
        # 转换为DataFrame
        df = pd.DataFrame(data, columns=[
            'coverage', 'avg_cvrs', 'max_cost', 'has_organic', 'sequence_weight', 'label'
        ])
        
        # 准备特征和标签
        X = df[['coverage', 'avg_cvrs', 'max_cost', 'has_organic', 'sequence_weight']]
        y = df['label']
        
        # 分割训练和测试集
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 训练模型
        model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            random_state=42
        )
        model.fit(X_train, y_train)
        
        # 评估模型
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # 保存模型
        os.makedirs('models', exist_ok=True)
        model_path = 'models/conversion_predictor_v1.pkl'
        
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        logger.info(f"转化预测模型重训练完成，准确率: {accuracy:.3f}")
        
    except Exception as e:
        logger.error(f"模型重训练失败: {e}")

# Celery Beat 定时任务配置
app.conf.beat_schedule = {
    'daily-attribution-recalculation': {
        'task': 'app.tasks.attribution_task.daily_attribution_recalculation',
        'schedule': crontab(hour=2, minute=0),  # 每日凌晨2点
    },
    'weekly-model-retrain': {
        'task': 'app.tasks.attribution_task.retrain_conversion_model',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),  # 每周日凌晨3点
    }
}


