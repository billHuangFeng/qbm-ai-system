"""
BMOS Shapley归因引擎
实现多触点归因的Shapley值采样计算
"""
import numpy as np
import random
from itertools import combinations, permutations
from typing import List, Dict, Tuple, Optional
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class ShapleyAttribution:
    """Shapley值采样归因引擎"""
    
    def __init__(self, n_samples: int = 10000, random_seed: Optional[int] = None):
        """
        初始化Shapley归因引擎
        
        Args:
            n_samples: 采样次数，默认10000次
            random_seed: 随机种子，用于结果可重现
        """
        self.n_samples = n_samples
        if random_seed is not None:
            np.random.seed(random_seed)
            random.seed(random_seed)
        
        logger.info(f"Shapley归因引擎初始化完成，采样次数: {n_samples}")
    
    def calculate_attribution(
        self,
        touchpoints: List[Dict],
        conversion_value: float,
        use_ml_model: bool = False
    ) -> Dict[str, float]:
        """
        计算Shapley归因权重
        
        Args:
            touchpoints: 触点列表，格式: [{'media_id': 'douyin', 'time': '2024-01-01', 'quality_score': 0.8}, ...]
            conversion_value: 转化金额
            use_ml_model: 是否使用机器学习模型（暂未实现）
        
        Returns:
            归因权重字典: {'media_id': weight}
        """
        if not touchpoints:
            return {}
        
        n = len(touchpoints)
        if n == 1:
            # 单触点直接返回100%
            return {touchpoints[0]['media_id']: 1.0}
        
        # 初始化贡献度
        contributions = {tp['media_id']: 0.0 for tp in touchpoints}
        
        logger.debug(f"开始计算Shapley归因，触点数量: {n}, 采样次数: {self.n_samples}")
        
        # 蒙特卡洛采样
        for i in range(self.n_samples):
            # 随机排列触点顺序
            perm = np.random.permutation(n)
            
            # 计算每个触点的边际贡献
            for j, idx in enumerate(perm):
                coalition_before = set(perm[:j])
                coalition_after = coalition_before | {idx}
                
                # 计算边际价值
                marginal_value = self._coalition_value(
                    coalition_after, touchpoints, conversion_value
                ) - self._coalition_value(
                    coalition_before, touchpoints, conversion_value
                )
                
                contributions[touchpoints[idx]['media_id']] += marginal_value
        
        # 归一化权重
        total_contribution = sum(contributions.values())
        if total_contribution > 0:
            attribution = {k: v / total_contribution for k, v in contributions.items()}
        else:
            # 如果总贡献为0，平均分配
            attribution = {k: 1.0 / n for k in contributions.keys()}
        
        logger.debug(f"Shapley归因计算完成: {attribution}")
        return attribution
    
    def _coalition_value(
        self,
        coalition: set,
        touchpoints: List[Dict],
        conversion_value: float
    ) -> float:
        """
        计算联盟的转化概率
        
        Args:
            coalition: 触点联盟（索引集合）
            touchpoints: 触点列表
            conversion_value: 转化金额
        
        Returns:
            联盟转化概率
        """
        if not coalition:
            return 0.0
        
        # 基础转化率
        base_conversion_rate = 0.05  # 5%基础转化率
        
        # 计算覆盖度（触点数量影响）
        coverage_factor = min(len(coalition) / len(touchpoints), 1.0)
        
        # 计算质量得分（触点质量影响）
        quality_scores = [touchpoints[i].get('quality_score', 1.0) for i in coalition]
        avg_quality = np.mean(quality_scores)
        
        # 计算时序权重（触点时序影响）
        time_weight = self._calculate_time_weight(coalition, touchpoints)
        
        # 计算多样性权重（触点类型多样性影响）
        diversity_weight = self._calculate_diversity_weight(coalition, touchpoints)
        
        # 综合计算转化概率
        conversion_probability = (
            base_conversion_rate * 
            coverage_factor * 
            avg_quality * 
            time_weight * 
            diversity_weight
        )
        
        # 确保概率在合理范围内
        return min(max(conversion_probability, 0.0), 1.0)
    
    def _calculate_time_weight(self, coalition: set, touchpoints: List[Dict]) -> float:
        """计算时序权重"""
        if len(coalition) <= 1:
            return 1.0
        
        # 获取联盟中的触点时间
        times = []
        for idx in coalition:
            time_str = touchpoints[idx].get('time', '')
            if time_str:
                try:
                    # 解析时间字符串
                    if isinstance(time_str, str):
                        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    else:
                        dt = time_str
                    times.append(dt)
                except:
                    times.append(datetime.now())
        
        if len(times) < 2:
            return 1.0
        
        # 计算时间跨度
        times.sort()
        time_span = (times[-1] - times[0]).total_seconds() / 3600  # 小时
        
        # 时间跨度权重：适中的时间跨度效果最好
        if time_span < 1:  # 1小时内
            return 0.8
        elif time_span < 24:  # 1天内
            return 1.0
        elif time_span < 168:  # 1周内
            return 0.9
        else:  # 超过1周
            return 0.7
    
    def _calculate_diversity_weight(self, coalition: set, touchpoints: List[Dict]) -> float:
        """计算多样性权重"""
        if len(coalition) <= 1:
            return 1.0
        
        # 获取联盟中的媒体类型
        media_types = set()
        for idx in coalition:
            media_id = touchpoints[idx].get('media_id', '')
            # 根据媒体ID推断类型
            if 'douyin' in media_id.lower() or 'tiktok' in media_id.lower():
                media_types.add('video')
            elif 'xiaohongshu' in media_id.lower() or 'instagram' in media_id.lower():
                media_types.add('social')
            elif 'tmall' in media_id.lower() or 'taobao' in media_id.lower():
                media_types.add('ecommerce')
            elif 'baidu' in media_id.lower() or 'google' in media_id.lower():
                media_types.add('search')
            else:
                media_types.add('other')
        
        # 多样性权重：类型越多效果越好
        diversity_score = len(media_types) / 4.0  # 假设最多4种类型
        return min(diversity_score, 1.0)
    
    def calculate_attribution_with_decay(
        self,
        touchpoints: List[Dict],
        conversion_value: float,
        decay_factor: float = 0.5
    ) -> Dict[str, float]:
        """
        带衰减的Shapley归因计算
        
        Args:
            touchpoints: 触点列表
            conversion_value: 转化金额
            decay_factor: 衰减因子，默认0.5
        
        Returns:
            归因权重字典
        """
        if not touchpoints:
            return {}
        
        # 按时间排序触点
        sorted_touchpoints = sorted(
            touchpoints, 
            key=lambda x: x.get('time', datetime.now())
        )
        
        # 计算时间衰减权重
        conversion_time = sorted_touchpoints[-1].get('time', datetime.now())
        if isinstance(conversion_time, str):
            conversion_time = datetime.fromisoformat(conversion_time.replace('Z', '+00:00'))
        
        for tp in sorted_touchpoints:
            tp_time = tp.get('time', conversion_time)
            if isinstance(tp_time, str):
                tp_time = datetime.fromisoformat(tp_time.replace('Z', '+00:00'))
            
            # 计算时间差（小时）
            time_diff = (conversion_time - tp_time).total_seconds() / 3600
            
            # 应用衰减
            decay_weight = np.exp(-decay_factor * time_diff / 24)  # 按天衰减
            tp['decay_weight'] = decay_weight
        
        # 使用带衰减的触点计算Shapley值
        return self.calculate_attribution(sorted_touchpoints, conversion_value)
    
    def batch_calculate_attribution(
        self,
        orders: List[Dict],
        touchpoint_journey: Dict[str, List[Dict]]
    ) -> Dict[str, Dict[str, float]]:
        """
        批量计算归因
        
        Args:
            orders: 订单列表，格式: [{'order_id': 'ORD001', 'customer_id': 'CUST001', 'amt': 1000}, ...]
            touchpoint_journey: 客户触点旅程，格式: {'CUST001': [{'media_id': 'douyin', 'time': '...'}, ...]}
        
        Returns:
            订单归因结果: {'order_id': {'media_id': weight}}
        """
        results = {}
        
        logger.info(f"开始批量计算归因，订单数量: {len(orders)}")
        
        for order in orders:
            order_id = order['order_id']
            customer_id = order['customer_id']
            amt = order['amt']
            
            # 获取该客户的触点旅程
            customer_touchpoints = touchpoint_journey.get(customer_id, [])
            
            if not customer_touchpoints:
                # 没有触点数据，跳过
                continue
            
            # 计算归因
            attribution = self.calculate_attribution(customer_touchpoints, amt)
            results[order_id] = attribution
            
            logger.debug(f"订单 {order_id} 归因计算完成: {attribution}")
        
        logger.info(f"批量归因计算完成，处理订单数量: {len(results)}")
        return results
    
    def get_attribution_summary(self, attribution_results: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        获取归因汇总统计
        
        Args:
            attribution_results: 归因结果
        
        Returns:
            媒体渠道汇总权重
        """
        media_totals = {}
        total_orders = len(attribution_results)
        
        for order_id, attribution in attribution_results.items():
            for media_id, weight in attribution.items():
                if media_id not in media_totals:
                    media_totals[media_id] = 0.0
                media_totals[media_id] += weight
        
        # 计算平均权重
        media_averages = {
            media_id: total_weight / total_orders 
            for media_id, total_weight in media_totals.items()
        }
        
        return media_averages

class AttributionEngine:
    """归因引擎主类"""
    
    def __init__(self, n_samples: int = 10000):
        self.shapley_engine = ShapleyAttribution(n_samples=n_samples)
        logger.info("归因引擎初始化完成")
    
    def process_order_attribution(
        self,
        order_id: str,
        customer_id: str,
        order_amount: float,
        touchpoints: List[Dict]
    ) -> Dict[str, float]:
        """
        处理单个订单的归因
        
        Args:
            order_id: 订单ID
            customer_id: 客户ID
            order_amount: 订单金额
            touchpoints: 触点列表
        
        Returns:
            归因权重
        """
        logger.info(f"处理订单归因: {order_id}")
        
        # 使用Shapley引擎计算归因
        attribution = self.shapley_engine.calculate_attribution(
            touchpoints, order_amount
        )
        
        logger.info(f"订单 {order_id} 归因完成: {attribution}")
        return attribution
    
    def process_batch_attribution(
        self,
        orders: List[Dict],
        touchpoint_journey: Dict[str, List[Dict]]
    ) -> Dict[str, Dict[str, float]]:
        """
        批量处理订单归因
        
        Args:
            orders: 订单列表
            touchpoint_journey: 触点旅程数据
        
        Returns:
            批量归因结果
        """
        logger.info(f"开始批量归因处理，订单数量: {len(orders)}")
        
        return self.shapley_engine.batch_calculate_attribution(
            orders, touchpoint_journey
        )

# 全局归因引擎实例
attribution_engine = AttributionEngine()

def get_attribution_engine() -> AttributionEngine:
    """获取归因引擎实例"""
    return attribution_engine