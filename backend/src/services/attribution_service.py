"""
Shapley归因服务
实现多触点归因的Shapley值计算
"""

import numpy as np
from typing import List, Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ShapleyAttributionService:
    """Shapley值归因服务"""

    def __init__(self, n_samples: int = 10000, random_seed: Optional[int] = None):
        """
        初始化Shapley归因服务

        Args:
            n_samples: 蒙特卡洛采样次数，默认10000次
            random_seed: 随机种子，用于结果可重现
        """
        self.n_samples = n_samples
        if random_seed is not None:
            np.random.seed(random_seed)
        logger.info(f"Shapley归因服务初始化完成，采样次数: {n_samples}")

    def calculate_shapley_attribution(
        self,
        touchpoints: List[Dict],
        conversion_value: float,
        method: str = "monte_carlo",
    ) -> Dict[str, float]:
        """
        计算Shapley归因权重

        Args:
            touchpoints: 触点列表，格式: [
                {'id': 'touchpoint1', 'type': 'media', 'timestamp': '2024-01-01', 'cost': 100},
                ...
            ]
            conversion_value: 转化金额
            method: 计算方法 ('exact' 完全枚举 或 'monte_carlo' 蒙特卡洛采样)

        Returns:
            归因权重字典: {'touchpoint_id': weight}
        """
        if not touchpoints:
            return {}

        n = len(touchpoints)
        if n == 1:
            # 单触点直接返回100%
            return {touchpoints[0]["id"]: 1.0}

        # 如果触点数量较少，使用完全枚举；否则使用蒙特卡洛
        if method == "exact" and n <= 10:
            return self._calculate_exact_shapley(touchpoints, conversion_value)
        else:
            return self._calculate_monte_carlo_shapley(touchpoints, conversion_value)

    def _calculate_exact_shapley(
        self, touchpoints: List[Dict], conversion_value: float
    ) -> Dict[str, float]:
        """
        使用完全枚举方法计算Shapley值（适用于n <= 10）

        时间复杂度: O(n! * n)
        """
        from itertools import permutations

        n = len(touchpoints)
        contributions = {tp["id"]: 0.0 for tp in touchpoints}

        logger.debug(f"使用完全枚举方法计算Shapley值，触点数量: {n}")

        # 生成所有可能的排列
        for perm in permutations(range(n)):
            # 计算每个触点的边际贡献
            for i, idx in enumerate(perm):
                coalition_before = set(perm[:i])
                coalition_after = coalition_before | {idx}

                # 计算边际价值
                marginal_value = self._coalition_value(
                    coalition_after, touchpoints, conversion_value
                ) - self._coalition_value(
                    coalition_before, touchpoints, conversion_value
                )

                contributions[touchpoints[idx]["id"]] += marginal_value

        # 归一化
        total = sum(contributions.values())
        if total > 0:
            contributions = {k: v / total for k, v in contributions.items()}

        return contributions

    def _calculate_monte_carlo_shapley(
        self, touchpoints: List[Dict], conversion_value: float
    ) -> Dict[str, float]:
        """
        使用蒙特卡洛采样方法计算Shapley值（适用于n > 10）

        时间复杂度: O(k * n)，k为采样次数
        """
        n = len(touchpoints)
        contributions = {tp["id"]: 0.0 for tp in touchpoints}

        logger.debug(
            f"使用蒙特卡洛方法计算Shapley值，触点数量: {n}，采样次数: {self.n_samples}"
        )

        # 蒙特卡洛采样
        for _ in range(self.n_samples):
            # 随机排列触点顺序
            perm = np.random.permutation(n)

            # 计算每个触点的边际贡献
            for i, idx in enumerate(perm):
                coalition_before = set(perm[:i])
                coalition_after = coalition_before | {idx}

                # 计算边际价值
                marginal_value = self._coalition_value(
                    coalition_after, touchpoints, conversion_value
                ) - self._coalition_value(
                    coalition_before, touchpoints, conversion_value
                )

                contributions[touchpoints[idx]["id"]] += marginal_value

        # 归一化
        total = sum(contributions.values())
        if total > 0:
            contributions = {k: v / total for k, v in contributions.items()}

        return contributions

    def _coalition_value(
        self, coalition: set, touchpoints: List[Dict], conversion_value: float
    ) -> float:
        """
        计算联盟（coalition）的价值

        Args:
            coalition: 联盟中触点的索引集合
            touchpoints: 所有触点列表
            conversion_value: 转化金额

        Returns:
            联盟价值
        """
        if not coalition:
            return 0.0

        # 简化版本：使用成本加权
        # 实际应用中可能需要更复杂的价值函数
        total_cost = sum(touchpoints[i].get("cost", 0) for i in coalition)
        total_cost_all = sum(tp.get("cost", 0) for tp in touchpoints)

        if total_cost_all == 0:
            # 如果没有成本信息，按触点数量平均分配
            return conversion_value * (len(coalition) / len(touchpoints))

        # 按成本比例分配
        return conversion_value * (total_cost / total_cost_all)

    def batch_calculate_attribution(
        self, orders: List[Dict], touchpoint_journey: Dict[str, List[Dict]]
    ) -> Dict[str, Dict[str, float]]:
        """
        批量计算订单归因

        Args:
            orders: 订单列表，格式: [
                {'order_id': 'order1', 'customer_id': 'cust1', 'amount': 1000},
                ...
            ]
            touchpoint_journey: 触点旅程数据，格式: {
                'order1': [{'id': 'tp1', 'type': 'media', ...}, ...],
                ...
            }

        Returns:
            批量归因结果: {'order_id': {'touchpoint_id': weight}}
        """
        results = {}

        for order in orders:
            order_id = order["order_id"]
            touchpoints = touchpoint_journey.get(order_id, [])
            conversion_value = order.get("amount", 0)

            if touchpoints:
                attribution = self.calculate_shapley_attribution(
                    touchpoints, conversion_value
                )
                results[order_id] = attribution
            else:
                results[order_id] = {}

        return results
