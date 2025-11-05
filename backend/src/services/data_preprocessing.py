"""
数据预处理服务
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.impute import SimpleImputer, KNNImputer, IterativeImputer
from sklearn.ensemble import IsolationForest
from scipy import stats
import logging
from ..exceptions import DataQualityError, ValidationError
from ..logging_config import get_logger

logger = get_logger("data_preprocessing")


class DataPreprocessingService:
    """数据预处理服务"""

    def __init__(self):
        self.scalers = {}
        self.imputers = {}
        self.outlier_detectors = {}

    def detect_outliers_iqr(
        self, data: pd.DataFrame, column: str, factor: float = 1.5
    ) -> pd.Index:
        """使用IQR方法检测异常值"""
        try:
            Q1 = data[column].quantile(0.25)
            Q3 = data[column].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - factor * IQR
            upper_bound = Q3 + factor * IQR

            outliers = data[
                (data[column] < lower_bound) | (data[column] > upper_bound)
            ].index

            logger.info(f"检测到 {len(outliers)} 个异常值在列 {column}")
            return outliers

        except Exception as e:
            logger.error(f"IQR异常值检测失败: {e}")
            raise DataQualityError(f"IQR异常值检测失败: {e}")

    def detect_outliers_zscore(
        self, data: pd.DataFrame, column: str, threshold: float = 3
    ) -> pd.Index:
        """使用Z-score方法检测异常值"""
        try:
            z_scores = np.abs(stats.zscore(data[column].dropna()))
            outliers = data[column].dropna().index[z_scores > threshold]

            logger.info(f"检测到 {len(outliers)} 个异常值在列 {column}")
            return outliers

        except Exception as e:
            logger.error(f"Z-score异常值检测失败: {e}")
            raise DataQualityError(f"Z-score异常值检测失败: {e}")

    def detect_outliers_isolation_forest(
        self, data: pd.DataFrame, columns: List[str], contamination: float = 0.1
    ) -> pd.Index:
        """使用Isolation Forest检测异常值"""
        try:
            # 检查列是否存在
            missing_columns = [col for col in columns if col not in data.columns]
            if missing_columns:
                raise ValidationError(f"列 {missing_columns} 不存在于数据中")

            iso_forest = IsolationForest(contamination=contamination, random_state=42)
            outlier_labels = iso_forest.fit_predict(data[columns])

            outliers = data.index[outlier_labels == -1]

            logger.info(f"检测到 {len(outliers)} 个异常值")
            return outliers

        except Exception as e:
            logger.error(f"Isolation Forest异常值检测失败: {e}")
            raise DataQualityError(f"Isolation Forest异常值检测失败: {e}")

    def handle_missing_values(
        self, data: pd.DataFrame, column: str, method: str = "mean"
    ) -> pd.DataFrame:
        """处理缺失值"""
        try:
            if column not in data.columns:
                raise ValidationError(f"列 {column} 不存在于数据中")

            if method == "mean":
                imputer = SimpleImputer(strategy="mean")
            elif method == "median":
                imputer = SimpleImputer(strategy="median")
            elif method == "mode":
                imputer = SimpleImputer(strategy="most_frequent")
            elif method == "forward_fill":
                data[column] = data[column].fillna(method="ffill")
                return data
            elif method == "backward_fill":
                data[column] = data[column].fillna(method="bfill")
                return data
            elif method == "knn":
                imputer = KNNImputer(n_neighbors=5)
            elif method == "iterative":
                imputer = IterativeImputer(random_state=42)
            else:
                raise ValidationError(f"不支持的缺失值处理方法: {method}")

            data[column] = imputer.fit_transform(data[[column]])

            logger.info(f"使用 {method} 方法处理列 {column} 的缺失值")
            return data

        except Exception as e:
            logger.error(f"缺失值处理失败: {e}")
            raise DataQualityError(f"缺失值处理失败: {e}")

    def standardize_data(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """标准化数据"""
        try:
            if not all(col in data.columns for col in columns):
                raise ValidationError("指定的列不存在于数据中")

            scaler = StandardScaler()
            data[columns] = scaler.fit_transform(data[columns])

            # 保存标准化器
            self.scalers["standard"] = scaler

            logger.info(f"标准化列: {columns}")
            return data

        except Exception as e:
            logger.error(f"数据标准化失败: {e}")
            raise DataQualityError(f"数据标准化失败: {e}")

    def normalize_data(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """归一化数据"""
        try:
            if not all(col in data.columns for col in columns):
                raise ValidationError("指定的列不存在于数据中")

            scaler = MinMaxScaler()
            data[columns] = scaler.fit_transform(data[columns])

            # 保存归一化器
            self.scalers["minmax"] = scaler

            logger.info(f"归一化列: {columns}")
            return data

        except Exception as e:
            logger.error(f"数据归一化失败: {e}")
            raise DataQualityError(f"数据归一化失败: {e}")

    def robust_scale_data(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """鲁棒标准化数据"""
        try:
            if not all(col in data.columns for col in columns):
                raise ValidationError("指定的列不存在于数据中")

            scaler = RobustScaler()
            data[columns] = scaler.fit_transform(data[columns])

            # 保存鲁棒标准化器
            self.scalers["robust"] = scaler

            logger.info(f"鲁棒标准化列: {columns}")
            return data

        except Exception as e:
            logger.error(f"鲁棒标准化失败: {e}")
            raise DataQualityError(f"鲁棒标准化失败: {e}")

    def validate_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """验证数据质量"""
        try:
            quality_report = {
                "completeness": self._calculate_completeness(data),
                "consistency": self._calculate_consistency(data),
                "accuracy": self._calculate_accuracy(data),
                "timeliness": self._calculate_timeliness(data),
                "validity": self._calculate_validity(data),
            }

            # 计算总体质量分数
            quality_report["overall_score"] = np.mean(list(quality_report.values()))

            logger.info(f"数据质量报告: {quality_report}")
            return quality_report

        except Exception as e:
            logger.error(f"数据质量验证失败: {e}")
            raise DataQualityError(f"数据质量验证失败: {e}")

    def _calculate_completeness(self, data: pd.DataFrame) -> float:
        """计算数据完整性"""
        total_cells = data.size
        missing_cells = data.isnull().sum().sum()
        return 1 - (missing_cells / total_cells)

    def _calculate_consistency(self, data: pd.DataFrame) -> float:
        """计算数据一致性"""
        # 检查数据类型一致性
        type_consistency = 1.0
        for column in data.columns:
            if data[column].dtype == "object":
                # 检查字符串格式一致性
                unique_formats = data[column].dropna().str.len().nunique()
                if unique_formats > 1:
                    type_consistency -= 0.1

        return max(0, type_consistency)

    def _calculate_accuracy(self, data: pd.DataFrame) -> float:
        """计算数据准确性"""
        # 检查数值范围合理性
        accuracy_score = 1.0
        for column in data.select_dtypes(include=[np.number]).columns:
            if data[column].min() < 0 and column in [
                "rd_asset",
                "design_asset",
                "production_asset",
            ]:
                accuracy_score -= 0.1  # 资产值不应为负

        return max(0, accuracy_score)

    def _calculate_timeliness(self, data: pd.DataFrame) -> float:
        """计算数据时效性"""
        # 如果有时间列，检查数据的新鲜度
        if "data_date" in data.columns:
            latest_date = pd.to_datetime(data["data_date"]).max()
            current_date = pd.Timestamp.now()
            days_old = (current_date - latest_date).days

            # 数据越新，时效性越高
            timeliness = max(0, 1 - (days_old / 365))  # 一年内的数据
            return timeliness

        return 1.0  # 没有时间列时，假设数据是及时的

    def _calculate_validity(self, data: pd.DataFrame) -> float:
        """计算数据有效性"""
        validity_score = 1.0

        # 检查必填字段
        required_fields = ["tenant_id", "data_type", "data_date"]
        for field in required_fields:
            if field in data.columns and data[field].isnull().any():
                validity_score -= 0.2

        return max(0, validity_score)

    def feature_engineering(self, data: pd.DataFrame) -> pd.DataFrame:
        """特征工程"""
        try:
            engineered_data = data.copy()

            # 创建趋势特征
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            for column in numeric_columns:
                if column not in ["id", "tenant_id"]:
                    # 计算移动平均
                    engineered_data[f"{column}_ma_3"] = (
                        data[column].rolling(window=3).mean()
                    )
                    engineered_data[f"{column}_ma_5"] = (
                        data[column].rolling(window=5).mean()
                    )

                    # 计算趋势
                    engineered_data[f"{column}_trend"] = data[column].diff()

                    # 计算变化率
                    engineered_data[f"{column}_pct_change"] = data[column].pct_change()

            # 创建组合特征
            if "rd_asset" in data.columns and "design_asset" in data.columns:
                engineered_data["total_assets"] = (
                    data["rd_asset"] + data["design_asset"]
                )
                engineered_data["asset_ratio"] = data["rd_asset"] / (
                    data["design_asset"] + 1e-8
                )

            # 创建时间特征
            if "data_date" in data.columns:
                data["data_date"] = pd.to_datetime(data["data_date"])
                engineered_data["year"] = data["data_date"].dt.year
                engineered_data["month"] = data["data_date"].dt.month
                engineered_data["quarter"] = data["data_date"].dt.quarter
                engineered_data["day_of_year"] = data["data_date"].dt.dayofyear

            logger.info(
                f"特征工程完成，新增 {len(engineered_data.columns) - len(data.columns)} 个特征"
            )
            return engineered_data

        except Exception as e:
            logger.error(f"特征工程失败: {e}")
            raise DataQualityError(f"特征工程失败: {e}")

    def validate_data_rules(self, data: pd.DataFrame) -> Dict[str, Any]:
        """验证数据规则"""
        try:
            validation_result = {"is_valid": True, "errors": [], "warnings": []}

            # 检查必填字段
            required_fields = ["tenant_id", "data_type", "data_date"]
            for field in required_fields:
                if field in data.columns and data[field].isnull().any():
                    validation_result["errors"].append(f"必填字段 {field} 存在空值")
                    validation_result["is_valid"] = False

            # 检查数值字段范围
            numeric_fields = [
                "rd_asset",
                "design_asset",
                "production_asset",
                "marketing_asset",
                "delivery_asset",
                "channel_asset",
            ]
            for field in numeric_fields:
                if field in data.columns:
                    if (data[field] < 0).any():
                        validation_result["errors"].append(f"字段 {field} 存在负值")
                        validation_result["is_valid"] = False

                    if (data[field] > 1000000).any():
                        validation_result["warnings"].append(
                            f"字段 {field} 存在异常大的值"
                        )

            # 检查能力字段范围
            capability_fields = [
                "rd_capability",
                "design_capability",
                "production_capability",
                "marketing_capability",
                "delivery_capability",
                "channel_capability",
            ]
            for field in capability_fields:
                if field in data.columns:
                    if (data[field] < 0).any() or (data[field] > 1).any():
                        validation_result["errors"].append(
                            f"字段 {field} 超出范围 [0, 1]"
                        )
                        validation_result["is_valid"] = False

            logger.info(f"数据规则验证完成: {validation_result}")
            return validation_result

        except Exception as e:
            logger.error(f"数据规则验证失败: {e}")
            raise DataQualityError(f"数据规则验证失败: {e}")

    def calculate_data_quality_score(self, data: pd.DataFrame) -> float:
        """计算数据质量分数"""
        try:
            quality_metrics = self.validate_data_quality(data)
            return quality_metrics["overall_score"]

        except Exception as e:
            logger.error(f"数据质量分数计算失败: {e}")
            raise DataQualityError(f"数据质量分数计算失败: {e}")

    def treat_outliers(
        self, data: pd.DataFrame, column: str, method: str = "remove"
    ) -> pd.DataFrame:
        """处理异常值"""
        try:
            if column not in data.columns:
                raise ValidationError(f"列 {column} 不存在于数据中")

            if method == "remove":
                outliers = self.detect_outliers_iqr(data, column)
                return data.drop(outliers)

            elif method == "replace":
                outliers = self.detect_outliers_iqr(data, column)
                data_copy = data.copy()
                # 用中位数替换异常值
                median_value = data[column].median()
                data_copy.loc[outliers, column] = median_value
                return data_copy

            elif method == "cap":
                outliers = self.detect_outliers_iqr(data, column)
                data_copy = data.copy()
                # 用分位数限制异常值
                Q1 = data[column].quantile(0.25)
                Q3 = data[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                data_copy[column] = data_copy[column].clip(lower_bound, upper_bound)
                return data_copy

            else:
                raise ValidationError(f"不支持的异常值处理方法: {method}")

        except Exception as e:
            logger.error(f"异常值处理失败: {e}")
            raise DataQualityError(f"异常值处理失败: {e}")

    def transform_data(
        self, data: pd.DataFrame, column: str, method: str
    ) -> pd.DataFrame:
        """数据转换"""
        try:
            if column not in data.columns:
                raise ValidationError(f"列 {column} 不存在于数据中")

            data_copy = data.copy()

            if method == "log":
                data_copy[f"{column}_log"] = np.log1p(data[column])
            elif method == "sqrt":
                data_copy[f"{column}_sqrt"] = np.sqrt(data[column])
            elif method == "square":
                data_copy[f"{column}_square"] = data[column] ** 2
            elif method == "reciprocal":
                data_copy[f"{column}_reciprocal"] = 1 / (data[column] + 1e-8)
            else:
                raise ValidationError(f"不支持的转换方法: {method}")

            logger.info(f"数据转换完成: {column} -> {method}")
            return data_copy

        except Exception as e:
            logger.error(f"数据转换失败: {e}")
            raise DataQualityError(f"数据转换失败: {e}")

    def split_data(
        self, data: pd.DataFrame, test_size: float = 0.2, random_state: int = 42
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """数据分割"""
        try:
            from sklearn.model_selection import train_test_split

            train_data, test_data = train_test_split(
                data, test_size=test_size, random_state=random_state
            )

            logger.info(
                f"数据分割完成: 训练集 {len(train_data)} 条，测试集 {len(test_data)} 条"
            )
            return train_data, test_data

        except Exception as e:
            logger.error(f"数据分割失败: {e}")
            raise DataQualityError(f"数据分割失败: {e}")

    def cross_validation_split(
        self, data: pd.DataFrame, n_splits: int = 5
    ) -> List[Tuple[np.ndarray, np.ndarray]]:
        """交叉验证分割"""
        try:
            from sklearn.model_selection import KFold

            kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
            splits = list(kf.split(data))

            logger.info(f"交叉验证分割完成: {n_splits} 折")
            return splits

        except Exception as e:
            logger.error(f"交叉验证分割失败: {e}")
            raise DataQualityError(f"交叉验证分割失败: {e}")

    def impute_missing_values(
        self, data: pd.DataFrame, column: str, method: str = "knn"
    ) -> pd.DataFrame:
        """插补缺失值"""
        try:
            if column not in data.columns:
                raise ValidationError(f"列 {column} 不存在于数据中")

            data_copy = data.copy()

            if method == "knn":
                imputer = KNNImputer(n_neighbors=5)
            elif method == "iterative":
                imputer = IterativeImputer(random_state=42)
            else:
                raise ValidationError(f"不支持的插补方法: {method}")

            data_copy[column] = imputer.fit_transform(data[[column]])

            logger.info(f"缺失值插补完成: {column} -> {method}")
            return data_copy

        except Exception as e:
            logger.error(f"缺失值插补失败: {e}")
            raise DataQualityError(f"缺失值插补失败: {e}")

    def calculate_quality_metrics(self, data: pd.DataFrame) -> Dict[str, float]:
        """计算质量指标"""
        try:
            metrics = {
                "completeness": self._calculate_completeness(data),
                "consistency": self._calculate_consistency(data),
                "accuracy": self._calculate_accuracy(data),
                "timeliness": self._calculate_timeliness(data),
                "validity": self._calculate_validity(data),
            }

            return metrics

        except Exception as e:
            logger.error(f"质量指标计算失败: {e}")
            raise DataQualityError(f"质量指标计算失败: {e}")

    def preprocess_pipeline(
        self,
        data: pd.DataFrame,
        target_columns: List[str],
        handle_outliers: bool = True,
        handle_missing: bool = True,
        standardize: bool = True,
    ) -> pd.DataFrame:
        """完整的数据预处理流水线"""
        try:
            processed_data = data.copy()

            # 处理缺失值
            if handle_missing:
                for column in target_columns:
                    if (
                        column in processed_data.columns
                        and processed_data[column].isnull().any()
                    ):
                        processed_data = self.handle_missing_values(
                            processed_data, column, method="mean"
                        )

            # 处理异常值
            if handle_outliers:
                for column in target_columns:
                    if column in processed_data.columns:
                        processed_data = self.treat_outliers(
                            processed_data, column, method="cap"
                        )

            # 标准化
            if standardize:
                processed_data = self.standardize_data(processed_data, target_columns)

            logger.info("数据预处理流水线完成")
            return processed_data

        except Exception as e:
            logger.error(f"数据预处理流水线失败: {e}")
            raise DataQualityError(f"数据预处理流水线失败: {e}")

    # 新增核心方法
    def comprehensive_data_quality_check(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        综合数据质量检查

        Args:
            data: 待检查的数据

        Returns:
            数据质量报告
        """
        try:
            quality_report = {
                "basic_info": self._get_basic_data_info(data),
                "missing_values": self._analyze_missing_values(data),
                "outliers": self._analyze_outliers(data),
                "data_types": self._analyze_data_types(data),
                "duplicates": self._analyze_duplicates(data),
                "consistency": self._analyze_data_consistency(data),
                "quality_score": 0.0,
            }

            # 计算综合质量分数
            quality_score = self._calculate_quality_score(quality_report)
            quality_report["quality_score"] = quality_score

            return quality_report

        except Exception as e:
            logger.error(f"数据质量检查失败: {e}")
            raise DataQualityError(f"数据质量检查失败: {e}")

    def _get_basic_data_info(self, data: pd.DataFrame) -> Dict[str, Any]:
        """获取基本数据信息"""
        try:
            return {
                "shape": data.shape,
                "memory_usage": data.memory_usage(deep=True).sum(),
                "columns": list(data.columns),
                "dtypes": data.dtypes.to_dict(),
                "sample_data": data.head(3).to_dict(),
            }
        except Exception as e:
            logger.error(f"基本数据信息获取失败: {e}")
            return {}

    def _analyze_missing_values(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析缺失值"""
        try:
            missing_analysis = {}

            for column in data.columns:
                missing_count = data[column].isnull().sum()
                missing_percentage = (missing_count / len(data)) * 100

                missing_analysis[column] = {
                    "count": int(missing_count),
                    "percentage": float(missing_percentage),
                    "severity": self._classify_missing_severity(missing_percentage),
                }

            return missing_analysis

        except Exception as e:
            logger.error(f"缺失值分析失败: {e}")
            return {}

    def _analyze_outliers(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析异常值"""
        try:
            outlier_analysis = {}

            numeric_columns = data.select_dtypes(include=[np.number]).columns

            for column in numeric_columns:
                # IQR方法
                iqr_outliers = self.detect_outliers_iqr(data, column)

                # Z-score方法
                zscore_outliers = self.detect_outliers_zscore(data, column)

                outlier_analysis[column] = {
                    "iqr_count": len(iqr_outliers),
                    "iqr_percentage": (len(iqr_outliers) / len(data)) * 100,
                    "zscore_count": len(zscore_outliers),
                    "zscore_percentage": (len(zscore_outliers) / len(data)) * 100,
                    "severity": self._classify_outlier_severity(
                        len(iqr_outliers), len(data)
                    ),
                }

            return outlier_analysis

        except Exception as e:
            logger.error(f"异常值分析失败: {e}")
            return {}

    def _analyze_data_types(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析数据类型"""
        try:
            type_analysis = {}

            for column in data.columns:
                dtype = str(data[column].dtype)
                unique_count = data[column].nunique()

                type_analysis[column] = {
                    "dtype": dtype,
                    "unique_count": unique_count,
                    "unique_percentage": (unique_count / len(data)) * 100,
                    "is_categorical": self._is_categorical(data[column]),
                    "is_numeric": pd.api.types.is_numeric_dtype(data[column]),
                }

            return type_analysis

        except Exception as e:
            logger.error(f"数据类型分析失败: {e}")
            return {}

    def _analyze_duplicates(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析重复数据"""
        try:
            duplicate_analysis = {
                "row_duplicates": {
                    "count": int(data.duplicated().sum()),
                    "percentage": float((data.duplicated().sum() / len(data)) * 100),
                },
                "column_duplicates": [],
            }

            # 检查重复列
            for i, col1 in enumerate(data.columns):
                for j, col2 in enumerate(data.columns[i + 1 :], i + 1):
                    if data[col1].equals(data[col2]):
                        duplicate_analysis["column_duplicates"].append([col1, col2])

            return duplicate_analysis

        except Exception as e:
            logger.error(f"重复数据分析失败: {e}")
            return {}

    def _analyze_data_consistency(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析数据一致性"""
        try:
            consistency_analysis = {}

            for column in data.columns:
                if pd.api.types.is_numeric_dtype(data[column]):
                    # 数值列的一致性检查
                    consistency_analysis[column] = {
                        "range": [float(data[column].min()), float(data[column].max())],
                        "mean": float(data[column].mean()),
                        "std": float(data[column].std()),
                        "has_negative": bool((data[column] < 0).any()),
                        "has_zero": bool((data[column] == 0).any()),
                    }
                else:
                    # 分类列的一致性检查
                    value_counts = data[column].value_counts()
                    consistency_analysis[column] = {
                        "unique_values": int(data[column].nunique()),
                        "most_frequent": (
                            str(value_counts.index[0])
                            if len(value_counts) > 0
                            else None
                        ),
                        "most_frequent_count": (
                            int(value_counts.iloc[0]) if len(value_counts) > 0 else 0
                        ),
                        "has_empty_strings": bool((data[column] == "").any()),
                        "has_whitespace": bool(
                            data[column].astype(str).str.contains(r"^\s+|\s+$").any()
                        ),
                    }

            return consistency_analysis

        except Exception as e:
            logger.error(f"数据一致性分析失败: {e}")
            return {}

    def _classify_missing_severity(self, missing_percentage: float) -> str:
        """分类缺失值严重程度"""
        if missing_percentage == 0:
            return "无缺失"
        elif missing_percentage < 5:
            return "轻微"
        elif missing_percentage < 20:
            return "中等"
        elif missing_percentage < 50:
            return "严重"
        else:
            return "极严重"

    def _classify_outlier_severity(self, outlier_count: int, total_count: int) -> str:
        """分类异常值严重程度"""
        outlier_percentage = (outlier_count / total_count) * 100

        if outlier_percentage < 1:
            return "轻微"
        elif outlier_percentage < 5:
            return "中等"
        elif outlier_percentage < 15:
            return "严重"
        else:
            return "极严重"

    def _is_categorical(self, series: pd.Series) -> bool:
        """判断是否为分类变量"""
        try:
            # 检查唯一值比例
            unique_ratio = series.nunique() / len(series)

            # 检查数据类型
            is_object = series.dtype == "object"

            # 检查是否包含重复的字符串
            has_repeated_strings = is_object and unique_ratio < 0.5

            return has_repeated_strings or unique_ratio < 0.1

        except Exception:
            return False

    def _calculate_quality_score(self, quality_report: Dict[str, Any]) -> float:
        """计算数据质量分数"""
        try:
            score = 100.0

            # 缺失值扣分
            missing_values = quality_report.get("missing_values", {})
            for column, info in missing_values.items():
                missing_percentage = info.get("percentage", 0)
                if missing_percentage > 50:
                    score -= 20
                elif missing_percentage > 20:
                    score -= 10
                elif missing_percentage > 5:
                    score -= 5

            # 异常值扣分
            outliers = quality_report.get("outliers", {})
            for column, info in outliers.items():
                outlier_percentage = info.get("iqr_percentage", 0)
                if outlier_percentage > 15:
                    score -= 10
                elif outlier_percentage > 5:
                    score -= 5

            # 重复数据扣分
            duplicates = quality_report.get("duplicates", {})
            duplicate_percentage = duplicates.get("row_duplicates", {}).get(
                "percentage", 0
            )
            if duplicate_percentage > 10:
                score -= 10
            elif duplicate_percentage > 5:
                score -= 5

            return max(0.0, score)

        except Exception as e:
            logger.error(f"质量分数计算失败: {e}")
            return 0.0

    def smart_data_cleaning(
        self, data: pd.DataFrame, cleaning_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        智能数据清洗

        Args:
            data: 待清洗的数据
            cleaning_config: 清洗配置

        Returns:
            清洗结果
        """
        try:
            if cleaning_config is None:
                cleaning_config = self._get_default_cleaning_config()

            cleaned_data = data.copy()
            cleaning_log = []

            # 1. 处理缺失值
            if cleaning_config.get("handle_missing", True):
                missing_strategy = cleaning_config.get("missing_strategy", "auto")
                cleaned_data, missing_log = self._smart_handle_missing_values(
                    cleaned_data, missing_strategy
                )
                cleaning_log.extend(missing_log)

            # 2. 处理异常值
            if cleaning_config.get("handle_outliers", True):
                outlier_strategy = cleaning_config.get("outlier_strategy", "auto")
                cleaned_data, outlier_log = self._smart_handle_outliers(
                    cleaned_data, outlier_strategy
                )
                cleaning_log.extend(outlier_log)

            # 3. 数据类型优化
            if cleaning_config.get("optimize_types", True):
                cleaned_data, type_log = self._optimize_data_types(cleaned_data)
                cleaning_log.extend(type_log)

            # 4. 处理重复数据
            if cleaning_config.get("handle_duplicates", True):
                cleaned_data, duplicate_log = self._smart_handle_duplicates(
                    cleaned_data
                )
                cleaning_log.extend(duplicate_log)

            # 5. 数据标准化
            if cleaning_config.get("normalize", False):
                cleaned_data, normalize_log = self._normalize_data(cleaned_data)
                cleaning_log.extend(normalize_log)

            return {
                "cleaned_data": cleaned_data,
                "cleaning_log": cleaning_log,
                "original_shape": data.shape,
                "cleaned_shape": cleaned_data.shape,
                "improvement_score": self._calculate_cleaning_improvement(
                    data, cleaned_data
                ),
            }

        except Exception as e:
            logger.error(f"智能数据清洗失败: {e}")
            raise DataQualityError(f"智能数据清洗失败: {e}")

    def _get_default_cleaning_config(self) -> Dict[str, Any]:
        """获取默认清洗配置"""
        return {
            "handle_missing": True,
            "missing_strategy": "auto",
            "handle_outliers": True,
            "outlier_strategy": "auto",
            "optimize_types": True,
            "handle_duplicates": True,
            "normalize": False,
        }

    def _smart_handle_missing_values(
        self, data: pd.DataFrame, strategy: str
    ) -> Tuple[pd.DataFrame, List[str]]:
        """智能处理缺失值"""
        try:
            cleaned_data = data.copy()
            log = []

            for column in data.columns:
                missing_count = data[column].isnull().sum()
                if missing_count == 0:
                    continue

                missing_percentage = (missing_count / len(data)) * 100

                if strategy == "auto":
                    if missing_percentage > 50:
                        # 缺失超过50%，删除列
                        cleaned_data = cleaned_data.drop(columns=[column])
                        log.append(f"删除列 {column}：缺失率 {missing_percentage:.1f}%")
                    elif missing_percentage > 20:
                        # 缺失20-50%，使用中位数填充
                        if pd.api.types.is_numeric_dtype(data[column]):
                            cleaned_data[column] = cleaned_data[column].fillna(
                                cleaned_data[column].median()
                            )
                            log.append(
                                f"列 {column}：使用中位数填充 {missing_count} 个缺失值"
                            )
                        else:
                            cleaned_data[column] = cleaned_data[column].fillna(
                                cleaned_data[column].mode()[0]
                            )
                            log.append(
                                f"列 {column}：使用众数填充 {missing_count} 个缺失值"
                            )
                    else:
                        # 缺失少于20%，使用均值填充
                        if pd.api.types.is_numeric_dtype(data[column]):
                            cleaned_data[column] = cleaned_data[column].fillna(
                                cleaned_data[column].mean()
                            )
                            log.append(
                                f"列 {column}：使用均值填充 {missing_count} 个缺失值"
                            )
                        else:
                            cleaned_data[column] = cleaned_data[column].fillna(
                                cleaned_data[column].mode()[0]
                            )
                            log.append(
                                f"列 {column}：使用众数填充 {missing_count} 个缺失值"
                            )

            return cleaned_data, log

        except Exception as e:
            logger.error(f"智能缺失值处理失败: {e}")
            return data, [f"缺失值处理失败: {e}"]

    def _smart_handle_outliers(
        self, data: pd.DataFrame, strategy: str
    ) -> Tuple[pd.DataFrame, List[str]]:
        """智能处理异常值"""
        try:
            cleaned_data = data.copy()
            log = []

            numeric_columns = data.select_dtypes(include=[np.number]).columns

            for column in numeric_columns:
                outliers = self.detect_outliers_iqr(data, column)
                outlier_percentage = (len(outliers) / len(data)) * 100

                if outlier_percentage > 5:  # 异常值超过5%
                    if strategy == "auto":
                        # 使用IQR方法处理异常值
                        Q1 = data[column].quantile(0.25)
                        Q3 = data[column].quantile(0.75)
                        IQR = Q3 - Q1

                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR

                        # 将异常值限制在边界内
                        cleaned_data[column] = cleaned_data[column].clip(
                            lower_bound, upper_bound
                        )
                        log.append(
                            f"列 {column}：限制 {len(outliers)} 个异常值在 [{lower_bound:.2f}, {upper_bound:.2f}] 范围内"
                        )

            return cleaned_data, log

        except Exception as e:
            logger.error(f"智能异常值处理失败: {e}")
            return data, [f"异常值处理失败: {e}"]

    def _optimize_data_types(
        self, data: pd.DataFrame
    ) -> Tuple[pd.DataFrame, List[str]]:
        """优化数据类型"""
        try:
            optimized_data = data.copy()
            log = []

            for column in data.columns:
                original_dtype = str(data[column].dtype)

                # 尝试转换为更合适的数据类型
                if pd.api.types.is_object_dtype(data[column]):
                    # 尝试转换为数值类型
                    try:
                        numeric_data = pd.to_numeric(data[column], errors="coerce")
                        if not numeric_data.isnull().all():
                            optimized_data[column] = numeric_data
                            log.append(
                                f"列 {column}：从 {original_dtype} 转换为数值类型"
                            )
                            continue
                    except:
                        pass

                    # 尝试转换为日期类型
                    try:
                        date_data = pd.to_datetime(data[column], errors="coerce")
                        if not date_data.isnull().all():
                            optimized_data[column] = date_data
                            log.append(
                                f"列 {column}：从 {original_dtype} 转换为日期类型"
                            )
                            continue
                    except:
                        pass

                # 尝试转换为分类类型
                if data[column].nunique() / len(data) < 0.5:  # 唯一值比例小于50%
                    try:
                        optimized_data[column] = optimized_data[column].astype(
                            "category"
                        )
                        log.append(f"列 {column}：从 {original_dtype} 转换为分类类型")
                    except:
                        pass

            return optimized_data, log

        except Exception as e:
            logger.error(f"数据类型优化失败: {e}")
            return data, [f"数据类型优化失败: {e}"]

    def _smart_handle_duplicates(
        self, data: pd.DataFrame
    ) -> Tuple[pd.DataFrame, List[str]]:
        """智能处理重复数据"""
        try:
            cleaned_data = data.copy()
            log = []

            # 处理行重复
            duplicate_rows = data.duplicated().sum()
            if duplicate_rows > 0:
                cleaned_data = cleaned_data.drop_duplicates()
                log.append(f"删除 {duplicate_rows} 个重复行")

            # 处理列重复
            duplicate_columns = []
            for i, col1 in enumerate(data.columns):
                for j, col2 in enumerate(data.columns[i + 1 :], i + 1):
                    if data[col1].equals(data[col2]):
                        duplicate_columns.append(col2)

            if duplicate_columns:
                cleaned_data = cleaned_data.drop(columns=duplicate_columns)
                log.append(f"删除重复列: {duplicate_columns}")

            return cleaned_data, log

        except Exception as e:
            logger.error(f"重复数据处理失败: {e}")
            return data, [f"重复数据处理失败: {e}"]

    def _normalize_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """数据标准化"""
        try:
            normalized_data = data.copy()
            log = []

            numeric_columns = data.select_dtypes(include=[np.number]).columns

            for column in numeric_columns:
                # 使用Z-score标准化
                mean_val = data[column].mean()
                std_val = data[column].std()

                if std_val > 0:
                    normalized_data[column] = (data[column] - mean_val) / std_val
                    log.append(f"列 {column}：Z-score标准化")

            return normalized_data, log

        except Exception as e:
            logger.error(f"数据标准化失败: {e}")
            return data, [f"数据标准化失败: {e}"]

    def _calculate_cleaning_improvement(
        self, original_data: pd.DataFrame, cleaned_data: pd.DataFrame
    ) -> float:
        """计算清洗改进分数"""
        try:
            improvement_score = 0.0

            # 计算缺失值改进
            original_missing = original_data.isnull().sum().sum()
            cleaned_missing = cleaned_data.isnull().sum().sum()
            if original_missing > 0:
                missing_improvement = (
                    original_missing - cleaned_missing
                ) / original_missing
                improvement_score += missing_improvement * 40

            # 计算重复数据改进
            original_duplicates = original_data.duplicated().sum()
            cleaned_duplicates = cleaned_data.duplicated().sum()
            if original_duplicates > 0:
                duplicate_improvement = (
                    original_duplicates - cleaned_duplicates
                ) / original_duplicates
                improvement_score += duplicate_improvement * 30

            # 计算数据类型优化
            original_object_cols = len(
                original_data.select_dtypes(include=["object"]).columns
            )
            cleaned_object_cols = len(
                cleaned_data.select_dtypes(include=["object"]).columns
            )
            if original_object_cols > 0:
                type_improvement = (
                    original_object_cols - cleaned_object_cols
                ) / original_object_cols
                improvement_score += type_improvement * 30

            return min(100.0, improvement_score * 100)

        except Exception as e:
            logger.error(f"清洗改进分数计算失败: {e}")
            return 0.0
