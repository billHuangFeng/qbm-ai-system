"""
BMOS系统分析查询API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from app.clickhouse import get_clickhouse_client
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/vpt-performance")
async def get_vpt_performance(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    vpt_ids: Optional[List[str]] = Query(None, description="价值主张ID列表")
):
    """获取价值主张的投入-口碑-销售表现"""
    try:
        client = get_clickhouse_client()
        
        vpt_filter = ""
        if vpt_ids:
            vpt_list = "','".join(vpt_ids)
            vpt_filter = f"AND vpt_id IN ('{vpt_list}')"
        
        query = f"""
            SELECT
                vpt_id,
                sumMerge(cost_amt) as total_cost,
                avgMerge(avg_cvrs) as avg_cvrs_score,
                sumMerge(attrib_sales) as total_sales,
                CASE 
                    WHEN sumMerge(cost_amt) > 0 
                    THEN (sumMerge(attrib_sales) - sumMerge(cost_amt)) / sumMerge(cost_amt)
                    ELSE 0 
                END as roi
            FROM v_vpt_performance
            WHERE date_key BETWEEN '{start_date}' AND '{end_date}'
            {vpt_filter}
            GROUP BY vpt_id
            ORDER BY total_sales DESC
        """
        
        results = client.execute(query)
        performance_data = []
        
        for row in results:
            performance_data.append({
                "vpt_id": row[0],
                "total_cost": float(row[1]) if row[1] else 0.0,
                "avg_cvrs_score": float(row[2]) if row[2] else 0.0,
                "total_sales": float(row[3]) if row[3] else 0.0,
                "roi": float(row[4]) if row[4] else 0.0
            })
        
        logger.info(f"VPT性能查询完成，返回 {len(performance_data)} 条记录")
        return performance_data
        
    except Exception as e:
        logger.error(f"VPT性能查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/marginal-alerts")
async def get_marginal_alerts(
    threshold: float = Query(-0.1, description="弹性阈值"),
    days: int = Query(30, description="分析天数")
):
    """获取边际优化警报"""
    try:
        client = get_clickhouse_client()
        
        query = f"""
            WITH weekly_metrics AS (
                SELECT
                    vpt_id,
                    toStartOfWeek(date_key) as week,
                    sumMerge(cost_amt) as cost,
                    avgMerge(avg_cvrs) as cvrs,
                    sumMerge(attrib_sales) as sales
                FROM v_vpt_performance
                WHERE date_key >= today() - INTERVAL {days} DAY
                GROUP BY vpt_id, week
                HAVING cost > 0
            ),
            elasticity AS (
                SELECT
                    vpt_id,
                    week,
                    cost,
                    cvrs,
                    sales,
                    (cvrs - lagInFrame(cvrs) OVER (PARTITION BY vpt_id ORDER BY week)) /
                    (cost - lagInFrame(cost) OVER (PARTITION BY vpt_id ORDER BY week)) as cvrs_elasticity,
                    (sales - lagInFrame(sales) OVER (PARTITION BY vpt_id ORDER BY week)) /
                    (cost - lagInFrame(cost) OVER (PARTITION BY vpt_id ORDER BY week)) as sales_elasticity
                FROM weekly_metrics
            )
            SELECT 
                vpt_id,
                week,
                cost,
                cvrs,
                sales,
                cvrs_elasticity,
                sales_elasticity
            FROM elasticity
            WHERE cvrs_elasticity < {threshold}
            ORDER BY cvrs_elasticity ASC
        """
        
        results = client.execute(query)
        alerts = []
        
        for row in results:
            alerts.append({
                "vpt_id": row[0],
                "week": row[1].strftime('%Y-%m-%d') if row[1] else None,
                "cost": float(row[2]) if row[2] else 0.0,
                "cvrs": float(row[3]) if row[3] else 0.0,
                "sales": float(row[4]) if row[4] else 0.0,
                "cvrs_elasticity": float(row[5]) if row[5] else 0.0,
                "sales_elasticity": float(row[6]) if row[6] else 0.0,
                "severity": "HIGH" if row[5] and row[5] < -0.2 else "MEDIUM"
            })
        
        logger.info(f"边际警报查询完成，返回 {len(alerts)} 条警报")
        return alerts
        
    except Exception as e:
        logger.error(f"边际警报查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/customer-journey/{customer_id}")
async def get_customer_journey(
    customer_id: str,
    days: int = Query(90, description="查询天数")
):
    """获取客户旅程"""
    try:
        client = get_clickhouse_client()
        
        query = f"""
            SELECT
                media_id,
                conv_id,
                touchpoint_time,
                weight,
                seq
            FROM v_customer_journey
            WHERE customer_id = '{customer_id}'
            AND touchpoint_time >= today() - INTERVAL {days} DAY
            ORDER BY touchpoint_time
        """
        
        results = client.execute(query)
        journey = []
        
        for row in results:
            journey.append({
                "media_id": row[0],
                "conv_id": row[1],
                "touchpoint_time": row[2].strftime('%Y-%m-%d %H:%M:%S') if row[2] else None,
                "weight": float(row[3]) if row[3] else 0.0,
                "seq": int(row[4]) if row[4] else 0
            })
        
        logger.info(f"客户旅程查询完成，客户: {customer_id}, 触点数量: {len(journey)}")
        return journey
        
    except Exception as e:
        logger.error(f"客户旅程查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vpt-lifecycle")
async def get_vpt_lifecycle(
    vpt_id: Optional[str] = Query(None, description="价值主张ID"),
    days: int = Query(30, description="查询天数")
):
    """获取价值主张生命周期分析"""
    try:
        client = get_clickhouse_client()
        
        vpt_filter = f"AND vpt_id = '{vpt_id}'" if vpt_id else ""
        
        query = f"""
            SELECT
                vpt_id,
                customer_id,
                lifecycle_stage,
                avgMerge(avg_awareness) as avg_awareness,
                avgMerge(avg_acceptance) as avg_acceptance,
                avgMerge(avg_experience) as avg_experience,
                countMerge(stage_count) as stage_count,
                publish_time
            FROM v_vpt_lifecycle
            WHERE publish_time >= today() - INTERVAL {days} DAY
            {vpt_filter}
            GROUP BY vpt_id, customer_id, lifecycle_stage, publish_time
            ORDER BY vpt_id, publish_time
        """
        
        results = client.execute(query)
        lifecycle_data = []
        
        for row in results:
            lifecycle_data.append({
                "vpt_id": row[0],
                "customer_id": row[1],
                "lifecycle_stage": row[2],
                "avg_awareness": float(row[3]) if row[3] else 0.0,
                "avg_acceptance": float(row[4]) if row[4] else 0.0,
                "avg_experience": float(row[5]) if row[5] else 0.0,
                "stage_count": int(row[6]) if row[6] else 0,
                "publish_time": row[7].strftime('%Y-%m-%d %H:%M:%S') if row[7] else None
            })
        
        logger.info(f"生命周期分析查询完成，返回 {len(lifecycle_data)} 条记录")
        return lifecycle_data
        
    except Exception as e:
        logger.error(f"生命周期分析查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/causal-graph")
async def get_causal_graph():
    """获取价值主张-产品特性因果图谱"""
    try:
        client = get_clickhouse_client()
        
        # 获取节点数据
        nodes_query = """
            SELECT 'vpt' as type, vpt_id as id, vpt_name as name, 1.0 as importance
            FROM dim_vpt
            UNION ALL
            SELECT 'pft' as type, pft_id as id, pft_name as name, 1.0 as importance
            FROM dim_pft
        """
        
        nodes_results = client.execute(nodes_query)
        nodes = []
        for row in nodes_results:
            nodes.append({
                "id": row[1],
                "name": row[2],
                "type": row[0],
                "importance": float(row[3])
            })
        
        # 获取边数据
        edges_query = """
            SELECT
                vpt_id as from_node,
                pft_id as to_node,
                causal_score,
                causal_score - 0.5 as delta
            FROM bridge_vpt_pft
            WHERE causal_score > 0.3
        """
        
        edges_results = client.execute(edges_query)
        edges = []
        for row in edges_results:
            edges.append({
                "from": row[0],
                "to": row[1],
                "causal_score": float(row[2]) if row[2] else 0.0,
                "delta": float(row[3]) if row[3] else 0.0
            })
        
        logger.info(f"因果图谱查询完成，节点: {len(nodes)}, 边: {len(edges)}")
        return {
            "nodes": nodes,
            "edges": edges
        }
        
    except Exception as e:
        logger.error(f"因果图谱查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations")
async def get_recommendations(
    limit: int = Query(10, description="推荐数量")
):
    """获取优化建议"""
    try:
        client = get_clickhouse_client()
        
        # 基于边际分析生成建议
        query = f"""
            WITH vpt_performance AS (
                SELECT
                    vpt_id,
                    sumMerge(cost_amt) as total_cost,
                    avgMerge(avg_cvrs) as avg_cvrs,
                    sumMerge(attrib_sales) as total_sales,
                    CASE 
                        WHEN sumMerge(cost_amt) > 0 
                        THEN (sumMerge(attrib_sales) - sumMerge(cost_amt)) / sumMerge(cost_amt)
                        ELSE 0 
                    END as roi
                FROM v_vpt_performance
                WHERE date_key >= today() - INTERVAL 30 DAY
                GROUP BY vpt_id
            )
            SELECT
                vpt_id,
                total_cost,
                avg_cvrs,
                total_sales,
                roi,
                CASE 
                    WHEN roi < 0.1 THEN 'reduce_investment'
                    WHEN avg_cvrs < 3.0 THEN 'improve_quality'
                    WHEN total_cost > total_sales * 0.5 THEN 'optimize_cost'
                    ELSE 'maintain'
                END as action,
                CASE 
                    WHEN roi < 0.1 THEN 'HIGH'
                    WHEN avg_cvrs < 3.0 THEN 'HIGH'
                    WHEN total_cost > total_sales * 0.5 THEN 'MEDIUM'
                    ELSE 'LOW'
                END as priority
            FROM vpt_performance
            WHERE roi < 0.2 OR avg_cvrs < 3.5
            ORDER BY 
                CASE 
                    WHEN roi < 0.1 THEN 1
                    WHEN avg_cvrs < 3.0 THEN 2
                    WHEN total_cost > total_sales * 0.5 THEN 3
                    ELSE 4
                END,
                roi ASC
            LIMIT {limit}
        """
        
        results = client.execute(query)
        recommendations = []
        
        for row in results:
            # 计算预期收益
            expected_benefit = 0.0
            if row[5] == 'reduce_investment':
                expected_benefit = row[1] * 0.2  # 减少20%投入
            elif row[5] == 'improve_quality':
                expected_benefit = row[3] * 0.1  # 提升10%销售
            elif row[5] == 'optimize_cost':
                expected_benefit = row[1] * 0.15  # 优化15%成本
            
            recommendations.append({
                "vpt_id": row[0],
                "title": f"优化{row[0]}的{row[5]}",
                "action": row[5],
                "priority": row[6],
                "current_cost": float(row[1]) if row[1] else 0.0,
                "current_cvrs": float(row[2]) if row[2] else 0.0,
                "current_sales": float(row[3]) if row[3] else 0.0,
                "current_roi": float(row[4]) if row[4] else 0.0,
                "expected_benefit": expected_benefit,
                "dept": "marketing" if row[5] in ['reduce_investment', 'optimize_cost'] else "product"
            })
        
        logger.info(f"优化建议查询完成，返回 {len(recommendations)} 条建议")
        return recommendations
        
    except Exception as e:
        logger.error(f"优化建议查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/attribution/calculate")
async def calculate_attribution(
    order_ids: List[str]
):
    """手动触发归因计算"""
    try:
        from app.tasks.attribution_task import batch_compute_attribution
        
        # 异步执行归因计算
        task = batch_compute_attribution.delay(order_ids)
        
        logger.info(f"归因计算任务已提交，订单数量: {len(order_ids)}, 任务ID: {task.id}")
        return {
            "message": "归因计算任务已提交",
            "task_id": task.id,
            "order_count": len(order_ids)
        }
        
    except Exception as e:
        logger.error(f"归因计算任务提交失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


