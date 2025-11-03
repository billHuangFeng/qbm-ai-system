"""
数据增强服务 - 智能补值
智能填充缺失值

功能：
- KNN补值（数值型字段，sklearn.impute.KNNImputer）
- 迭代补值（sklearn.impute.IterativeImputer，类似MICE）
- 随机森林补值（分类型字段）
- 业务规则补值（例如：默认税率、默认币种）
- 自动策略选择器（根据字段类型和缺失比例选择最佳策略）
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime

try:
    from sklearn.impute import KNNImputer, IterativeImputer
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
except ImportError:
    raise ImportError("请安装依赖: pip install scikit-learn")

from ...security.database import SecureDatabaseService
from ...error_handling.unified import BMOSError, BusinessError
from ...services.base import BaseService, ServiceConfig

logger = logging.getLogger(__name__)


class ImputationError(BMOSError):
    """补值错误"""
    pass


class SmartValueImputer(BaseService):
    """智能补值服务"""
    
    def __init__(
        self,
        db_service: SecureDatabaseService,
        config: Optional[ServiceConfig] = None
    ):
        super().__init__(db_service, config=config)
        self.knn_n_neighbors = 5
        self.iterative_max_iter = 10
        
        # 默认业务规则（用于快速补值的常见字段）
        self.default_rules = {
            "tax_rate": 0.13,      # 默认税率13%
            "currency": "CNY",     # 默认币种人民币
            "unit": "件",           # 默认单位
            "status": "active",     # 默认状态
            "region": "CN",         # 默认地区
        }
        
        # 自动补值价值说明：
        # 1. 效率提升：人工补值10000条数据需要100+小时，自动补值仅需数分钟
        # 2. 成本降低：减少人工成本，提升ROI
        # 3. 数据完整性：提升非关键字段的完整性（从60%到95%）
        # 4. 一致性：规则一致，减少人为错误
        # 
        # 适用场景：
        # - 辅助字段（备注、标签、分类等）
        # - 有明确业务规则的字段（默认税率、默认币种等）
        # - 非关键统计字段（温度、湿度等环境参数）
        # 
        # 不适用场景：
        # - 财务数据（订单金额、付款金额等）
        # - 主键/外键（订单号、客户ID等）
        # - 业务关键时间戳（订单日期、发货日期等）
        # 
        # 关键原则：精确的数据精确处理，辅助的数据智能补值
    
    def detect_missing_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        检测缺失值
        
        Args:
            df: DataFrame
            
        Returns:
            缺失值统计信息
        """
        missing_count = df.isnull().sum()
        missing_ratio = missing_count / len(df)
        
        return {
            "missing_count": missing_count.to_dict(),
            "missing_ratio": missing_ratio.to_dict(),
            "total_missing": missing_count.sum(),
            "columns_with_missing": [
                col for col in df.columns if missing_count[col] > 0
            ]
        }
    
    def should_allow_imputation(
        self,
        field_name: str,
        field_config: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        判断是否允许补值
        
        Args:
            field_name: 字段名
            field_config: 字段配置
            
        Returns:
            (是否允许, 原因)
        """
        # 检查是否明确禁止补值
        if field_config.get("allow_imputation") is False:
            return False, "字段配置不允许补值"
        
        # 检查是否为关键业务字段
        if field_config.get("business_critical") is True:
            return False, "关键业务字段，不允许自动补值"
        
        # 检查风险等级
        risk_level = field_config.get("imputation_risk", "medium")
        if risk_level == "high":
            return False, "高风险字段，需要人工审核"
        
        # 检查是否为必填字段（必填字段不建议自动补值）
        if field_config.get("required") is True and risk_level != "low":
            return False, "必填字段，建议人工输入而非自动补值"
        
        return True, "允许补值"
    
    def select_imputation_strategy(
        self,
        field_config: Dict[str, Any],
        missing_ratio: float,
        field_type: str
    ) -> str:
        """
        自动选择补值策略
        
        Args:
            field_config: 字段配置
            missing_ratio: 缺失比例
            field_type: 字段类型（numeric/categorical/date/text）
            
        Returns:
            推荐策略（auto/knn/iterative/random_forest/rule_based）
        """
        # 如果有业务规则，优先使用规则补值（最安全）
        if field_config.get("default_value") is not None:
            return "rule_based"
        
        # 如果有业务规则名称，使用规则补值
        if field_config.get("rule_name") in self.default_rules:
            return "rule_based"
        
        # 检查是否允许使用机器学习方法
        use_ml = field_config.get("allow_ml_imputation", True)
        
        # 数值型字段
        if field_type == "numeric":
            if not use_ml:
                # 不允许机器学习，只能使用规则补值
                return "rule_based"
            
            if missing_ratio < 0.1:
                # 缺失率低，使用KNN
                return "knn"
            elif missing_ratio < 0.3:
                # 缺失率中等，使用迭代补值
                return "iterative"
            else:
                # 缺失率高，使用迭代补值（更稳定）
                return "iterative"
        
        # 分类型字段
        elif field_type == "categorical":
            if missing_ratio < 0.2 or not use_ml:
                # 缺失率低或不允许ML，使用众数（规则补值）
                return "rule_based"
            else:
                # 缺失率高，使用随机森林
                return "random_forest"
        
        # 其他类型，使用规则补值
        else:
            return "rule_based"
    
    def impute_with_knn(
        self,
        df: pd.DataFrame,
        columns: List[str],
        n_neighbors: int = 5
    ) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
        """
        使用KNN补值
        
        Args:
            df: DataFrame
            columns: 需要补值的列
            n_neighbors: KNN邻居数量
            
        Returns:
            (补值后的DataFrame, 补值日志)
        """
        imputation_log = []
        df_imputed = df.copy()
        
        try:
            # 只处理数值型列
            numeric_columns = df[columns].select_dtypes(include=[np.number]).columns.tolist()
            
            if not numeric_columns:
                logger.warning("没有数值型列可以KNN补值")
                return df_imputed, imputation_log
            
            # 创建KNN补值器
            imputer = KNNImputer(n_neighbors=n_neighbors)
            
            # 补值
            imputed_values = imputer.fit_transform(df[numeric_columns])
            
            # 更新DataFrame
            for i, col in enumerate(numeric_columns):
                original_values = df[col].values
                imputed_values_col = imputed_values[:, i]
                
                # 记录补值操作
                for row_idx in range(len(df)):
                    if pd.isna(original_values[row_idx]):
                        imputation_log.append({
                            "row_index": row_idx,
                            "field": col,
                            "original_value": None,
                            "imputed_value": float(imputed_values_col[row_idx]),
                            "method": "knn",
                            "confidence": 0.85  # KNN补值的置信度
                        })
                
                df_imputed[col] = imputed_values_col
            
            logger.info(f"KNN补值完成: {len(imputation_log)}个值")
            
        except Exception as e:
            logger.error(f"KNN补值失败: {e}")
            raise ImputationError(f"KNN补值失败: {e}")
        
        return df_imputed, imputation_log
    
    def impute_with_iterative(
        self,
        df: pd.DataFrame,
        columns: List[str],
        max_iter: int = 10
    ) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
        """
        使用迭代补值（MICE方法）
        
        Args:
            df: DataFrame
            columns: 需要补值的列
            max_iter: 最大迭代次数
            
        Returns:
            (补值后的DataFrame, 补值日志)
        """
        imputation_log = []
        df_imputed = df.copy()
        
        try:
            # 只处理数值型列
            numeric_columns = df[columns].select_dtypes(include=[np.number]).columns.tolist()
            
            if not numeric_columns:
                logger.warning("没有数值型列可以迭代补值")
                return df_imputed, imputation_log
            
            # 创建迭代补值器
            imputer = IterativeImputer(
                max_iter=max_iter,
                random_state=42,
                imputation_order='ascending'
            )
            
            # 补值
            imputed_values = imputer.fit_transform(df[numeric_columns])
            
            # 更新DataFrame
            for i, col in enumerate(numeric_columns):
                original_values = df[col].values
                imputed_values_col = imputed_values[:, i]
                
                # 记录补值操作
                for row_idx in range(len(df)):
                    if pd.isna(original_values[row_idx]):
                        imputation_log.append({
                            "row_index": row_idx,
                            "field": col,
                            "original_value": None,
                            "imputed_value": float(imputed_values_col[row_idx]),
                            "method": "iterative",
                            "confidence": 0.80  # 迭代补值的置信度
                        })
                
                df_imputed[col] = imputed_values_col
            
            logger.info(f"迭代补值完成: {len(imputation_log)}个值")
            
        except Exception as e:
            logger.error(f"迭代补值失败: {e}")
            raise ImputationError(f"迭代补值失败: {e}")
        
        return df_imputed, imputation_log
    
    def impute_with_random_forest(
        self,
        df: pd.DataFrame,
        columns: List[str]
    ) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
        """
        使用随机森林补值（分类型字段）
        
        Args:
            df: DataFrame
            columns: 需要补值的列
            
        Returns:
            (补值后的DataFrame, 补值日志)
        """
        imputation_log = []
        df_imputed = df.copy()
        
        try:
            for col in columns:
                # 检查列是否有缺失值
                if df[col].isnull().sum() == 0:
                    continue
                
                # 分离有值和缺失的行
                known_mask = df[col].notna()
                missing_mask = df[col].isna()
                
                if known_mask.sum() < 2:
                    # 已知值太少，无法训练模型
                    logger.warning(f"列 {col} 已知值太少，跳过随机森林补值")
                    continue
                
                # 准备训练数据
                X_known = df.loc[known_mask, df.columns.difference([col])].select_dtypes(include=[np.number])
                y_known = df.loc[known_mask, col]
                
                if X_known.empty or len(X_known.columns) == 0:
                    # 没有可用的特征列
                    logger.warning(f"列 {col} 没有可用特征，跳过随机森林补值")
                    continue
                
                X_missing = df.loc[missing_mask, df.columns.difference([col])].select_dtypes(include=[np.number])
                
                # 判断是回归还是分类
                if y_known.dtype == 'object' or y_known.dtype.name == 'category':
                    # 分类任务
                    model = RandomForestClassifier(n_estimators=100, random_state=42)
                else:
                    # 回归任务
                    model = RandomForestRegressor(n_estimators=100, random_state=42)
                
                # 训练模型
                model.fit(X_known, y_known)
                
                # 预测缺失值
                predicted_values = model.predict(X_missing)
                
                # 更新DataFrame
                df_imputed.loc[missing_mask, col] = predicted_values
                
                # 记录补值操作
                for idx, row_idx in enumerate(df.loc[missing_mask].index):
                    imputation_log.append({
                        "row_index": int(row_idx),
                        "field": col,
                        "original_value": None,
                        "imputed_value": str(predicted_values[idx]) if isinstance(predicted_values[idx], (str, object)) else float(predicted_values[idx]),
                        "method": "random_forest",
                        "confidence": 0.75  # 随机森林补值的置信度
                    })
            
            logger.info(f"随机森林补值完成: {len(imputation_log)}个值")
            
        except Exception as e:
            logger.error(f"随机森林补值失败: {e}")
            raise ImputationError(f"随机森林补值失败: {e}")
        
        return df_imputed, imputation_log
    
    def impute_with_rule(
        self,
        df: pd.DataFrame,
        field_configs: Dict[str, Dict[str, Any]]
    ) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
        """
        使用业务规则补值
        
        Args:
            df: DataFrame
            field_configs: 字段配置字典
            
        Returns:
            (补值后的DataFrame, 补值日志)
        """
        imputation_log = []
        df_imputed = df.copy()
        
        try:
            for field_name, field_config in field_configs.items():
                if field_name not in df.columns:
                    continue
                
                # 检查是否有缺失值
                if df[field_name].isnull().sum() == 0:
                    continue
                
                # 获取默认值
                default_value = None
                
                # 优先使用配置中的默认值
                if field_config.get("default_value") is not None:
                    default_value = field_config["default_value"]
                
                # 其次使用规则名称对应的默认值
                elif field_config.get("rule_name") in self.default_rules:
                    default_value = self.default_rules[field_config["rule_name"]]
                
                # 如果没有默认值，使用众数（对于分类型字段）
                elif field_config.get("field_type") == "categorical":
                    mode_value = df[field_name].mode()
                    if not mode_value.empty:
                        default_value = mode_value.iloc[0]
                
                if default_value is None:
                    continue
                
                # 补值
                missing_mask = df[field_name].isnull()
                df_imputed.loc[missing_mask, field_name] = default_value
                
                # 记录补值操作
                for row_idx in df.loc[missing_mask].index:
                    imputation_log.append({
                        "row_index": int(row_idx),
                        "field": field_name,
                        "original_value": None,
                        "imputed_value": default_value,
                        "method": "rule_based",
                        "confidence": 0.90  # 规则补值的置信度
                    })
            
            logger.info(f"规则补值完成: {len(imputation_log)}个值")
            
        except Exception as e:
            logger.error(f"规则补值失败: {e}")
            raise ImputationError(f"规则补值失败: {e}")
        
        return df_imputed, imputation_log
    
    def assess_imputation_risk(
        self,
        field_configs: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        评估补值风险
        
        Args:
            field_configs: 字段配置字典
            
        Returns:
            风险评估结果
        """
        risk_assessment = {
            "high_risk_fields": [],
            "medium_risk_fields": [],
            "low_risk_fields": [],
            "blocked_fields": [],
            "requires_approval": False
        }
        
        for field_name, field_config in field_configs.items():
            allow, reason = self.should_allow_imputation(field_name, field_config)
            
            if not allow:
                risk_assessment["blocked_fields"].append({
                    "field": field_name,
                    "reason": reason
                })
                continue
            
            risk_level = field_config.get("imputation_risk", "medium")
            
            if risk_level == "high":
                risk_assessment["high_risk_fields"].append(field_name)
                risk_assessment["requires_approval"] = True
            elif risk_level == "medium":
                risk_assessment["medium_risk_fields"].append(field_name)
            else:
                risk_assessment["low_risk_fields"].append(field_name)
        
        return risk_assessment
    
    async def impute_values(
        self,
        data_type: str,
        records: List[Dict[str, Any]],
        field_configs: Dict[str, Dict[str, Any]],
        strategy: str = "auto",
        tenant_id: Optional[str] = None,
        skip_blocked_fields: bool = True
    ) -> Dict[str, Any]:
        """
        智能补值
        
        Args:
            data_type: 数据类型（order/production/expense）
            records: 数据记录列表（DataFrame格式或字典列表）
            field_configs: 字段配置（类型、默认值、业务规则）
            strategy: 补值策略（"auto", "knn", "iterative", "random_forest", "rule_based"）
            tenant_id: 租户ID（可选）
            
        Returns:
            补值结果
        """
        try:
            # 转换records为DataFrame
            if isinstance(records, pd.DataFrame):
                df = records.copy()
            else:
                df = pd.DataFrame(records)
            
            # 检测缺失值
            missing_info = self.detect_missing_values(df)
            
            if missing_info["total_missing"] == 0:
                return {
                    "imputed_records": df.to_dict('records'),
                    "imputation_log": [],
                    "statistics": {
                        "total_records": len(df),
                        "missing_count": 0,
                        "imputed_count": 0,
                        "imputation_rate": 0.0
                    }
                }
            
            df_imputed = df.copy()
            all_imputation_log = []
            
            # 根据策略补值
            # 风险评估
            risk_assessment = self.assess_imputation_risk(field_configs)
            
            # 检查是否有被阻止的字段
            if risk_assessment["blocked_fields"] and skip_blocked_fields:
                logger.warning(f"以下字段被阻止补值: {[f['field'] for f in risk_assessment['blocked_fields']]}")
                # 从配置中移除被阻止的字段
                for blocked in risk_assessment["blocked_fields"]:
                    field_name = blocked["field"]
                    if field_name in field_configs:
                        del field_configs[field_name]
            
            if strategy == "auto":
                # 自动选择策略
                for field_name, field_config in field_configs.items():
                    if field_name not in df.columns:
                        continue
                    
                    # 检查是否允许补值
                    allow, reason = self.should_allow_imputation(field_name, field_config)
                    if not allow:
                        logger.warning(f"字段 {field_name} 不允许补值: {reason}")
                        continue
                    
                    missing_ratio = missing_info["missing_ratio"].get(field_name, 0.0)
                    field_type = field_config.get("field_type", "numeric")
                    
                    selected_strategy = self.select_imputation_strategy(
                        field_config,
                        missing_ratio,
                        field_type
                    )
                    
                    if selected_strategy == "knn":
                        df_imputed, log = self.impute_with_knn(df_imputed, [field_name])
                        all_imputation_log.extend(log)
                    elif selected_strategy == "iterative":
                        df_imputed, log = self.impute_with_iterative(df_imputed, [field_name])
                        all_imputation_log.extend(log)
                    elif selected_strategy == "random_forest":
                        df_imputed, log = self.impute_with_random_forest(df_imputed, [field_name])
                        all_imputation_log.extend(log)
                    elif selected_strategy == "rule_based":
                        df_imputed, log = self.impute_with_rule(df_imputed, {field_name: field_config})
                        all_imputation_log.extend(log)
            
            elif strategy == "knn":
                columns_with_missing = missing_info["columns_with_missing"]
                df_imputed, all_imputation_log = self.impute_with_knn(df_imputed, columns_with_missing)
            
            elif strategy == "iterative":
                columns_with_missing = missing_info["columns_with_missing"]
                df_imputed, all_imputation_log = self.impute_with_iterative(df_imputed, columns_with_missing)
            
            elif strategy == "random_forest":
                columns_with_missing = missing_info["columns_with_missing"]
                df_imputed, all_imputation_log = self.impute_with_random_forest(df_imputed, columns_with_missing)
            
            elif strategy == "rule_based":
                df_imputed, all_imputation_log = self.impute_with_rule(df_imputed, field_configs)
            
            else:
                raise ImputationError(f"未知的补值策略: {strategy}")
            
            # 统计信息
            imputed_count = len(all_imputation_log)
            imputation_rate = imputed_count / missing_info["total_missing"] if missing_info["total_missing"] > 0 else 0.0
            
            statistics = {
                "total_records": len(df),
                "missing_count": missing_info["total_missing"],
                "imputed_count": imputed_count,
                "imputation_rate": imputation_rate,
                "strategy_used": strategy,
                "fields_imputed": list(set([log["field"] for log in all_imputation_log])),
                "risk_assessment": risk_assessment,
                "blocked_fields_count": len(risk_assessment["blocked_fields"]),
                "requires_approval": risk_assessment["requires_approval"]
            }
            
            # 在补值日志中标记风险等级
            for log in all_imputation_log:
                field_name = log["field"]
                if field_name in field_configs:
                    field_config = field_configs[field_name]
                    log["risk_level"] = field_config.get("imputation_risk", "medium")
                    log["business_critical"] = field_config.get("business_critical", False)
                    log["can_revert"] = True  # 标记为可回滚
            
            return {
                "imputed_records": df_imputed.to_dict('records'),
                "imputation_log": all_imputation_log,
                "statistics": statistics
            }
            
        except Exception as e:
            logger.error(f"智能补值失败: {e}")
            raise ImputationError(f"智能补值失败: {e}")

