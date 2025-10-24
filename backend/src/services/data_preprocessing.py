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
    
    def detect_outliers_iqr(self, data: pd.DataFrame, column: str, factor: float = 1.5) -> pd.Index:
        """使用IQR方法检测异常值"""
        try:
            Q1 = data[column].quantile(0.25)
            Q3 = data[column].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - factor * IQR
            upper_bound = Q3 + factor * IQR
            
            outliers = data[(data[column] < lower_bound) | (data[column] > upper_bound)].index
            
            logger.info(f"检测到 {len(outliers)} 个异常值在列 {column}")
            return outliers
            
        except Exception as e:
            logger.error(f"IQR异常值检测失败: {e}")
            raise DataQualityError(f"IQR异常值检测失败: {e}")
    
    def detect_outliers_zscore(self, data: pd.DataFrame, column: str, threshold: float = 3) -> pd.Index:
        """使用Z-score方法检测异常值"""
        try:
            z_scores = np.abs(stats.zscore(data[column].dropna()))
            outliers = data[column].dropna().index[z_scores > threshold]
            
            logger.info(f"检测到 {len(outliers)} 个异常值在列 {column}")
            return outliers
            
        except Exception as e:
            logger.error(f"Z-score异常值检测失败: {e}")
            raise DataQualityError(f"Z-score异常值检测失败: {e}")
    
    def detect_outliers_isolation_forest(self, data: pd.DataFrame, columns: List[str], contamination: float = 0.1) -> pd.Index:
        """使用Isolation Forest检测异常值"""
        try:
            if columns not in data.columns:
                raise ValidationError(f"列 {columns} 不存在于数据中")
            
            iso_forest = IsolationForest(contamination=contamination, random_state=42)
            outlier_labels = iso_forest.fit_predict(data[columns])
            
            outliers = data.index[outlier_labels == -1]
            
            logger.info(f"检测到 {len(outliers)} 个异常值")
            return outliers
            
        except Exception as e:
            logger.error(f"Isolation Forest异常值检测失败: {e}")
            raise DataQualityError(f"Isolation Forest异常值检测失败: {e}")
    
    def handle_missing_values(self, data: pd.DataFrame, column: str, method: str = 'mean') -> pd.DataFrame:
        """处理缺失值"""
        try:
            if column not in data.columns:
                raise ValidationError(f"列 {column} 不存在于数据中")
            
            if method == 'mean':
                imputer = SimpleImputer(strategy='mean')
            elif method == 'median':
                imputer = SimpleImputer(strategy='median')
            elif method == 'mode':
                imputer = SimpleImputer(strategy='most_frequent')
            elif method == 'forward_fill':
                data[column] = data[column].fillna(method='ffill')
                return data
            elif method == 'backward_fill':
                data[column] = data[column].fillna(method='bfill')
                return data
            elif method == 'knn':
                imputer = KNNImputer(n_neighbors=5)
            elif method == 'iterative':
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
            self.scalers['standard'] = scaler
            
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
            self.scalers['minmax'] = scaler
            
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
            self.scalers['robust'] = scaler
            
            logger.info(f"鲁棒标准化列: {columns}")
            return data
            
        except Exception as e:
            logger.error(f"鲁棒标准化失败: {e}")
            raise DataQualityError(f"鲁棒标准化失败: {e}")
    
    def validate_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """验证数据质量"""
        try:
            quality_report = {
                'completeness': self._calculate_completeness(data),
                'consistency': self._calculate_consistency(data),
                'accuracy': self._calculate_accuracy(data),
                'timeliness': self._calculate_timeliness(data),
                'validity': self._calculate_validity(data)
            }
            
            # 计算总体质量分数
            quality_report['overall_score'] = np.mean(list(quality_report.values()))
            
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
            if data[column].dtype == 'object':
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
            if data[column].min() < 0 and column in ['rd_asset', 'design_asset', 'production_asset']:
                accuracy_score -= 0.1  # 资产值不应为负
        
        return max(0, accuracy_score)
    
    def _calculate_timeliness(self, data: pd.DataFrame) -> float:
        """计算数据时效性"""
        # 如果有时间列，检查数据的新鲜度
        if 'data_date' in data.columns:
            latest_date = pd.to_datetime(data['data_date']).max()
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
        required_fields = ['tenant_id', 'data_type', 'data_date']
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
                if column not in ['id', 'tenant_id']:
                    # 计算移动平均
                    engineered_data[f'{column}_ma_3'] = data[column].rolling(window=3).mean()
                    engineered_data[f'{column}_ma_5'] = data[column].rolling(window=5).mean()
                    
                    # 计算趋势
                    engineered_data[f'{column}_trend'] = data[column].diff()
                    
                    # 计算变化率
                    engineered_data[f'{column}_pct_change'] = data[column].pct_change()
            
            # 创建组合特征
            if 'rd_asset' in data.columns and 'design_asset' in data.columns:
                engineered_data['total_assets'] = data['rd_asset'] + data['design_asset']
                engineered_data['asset_ratio'] = data['rd_asset'] / (data['design_asset'] + 1e-8)
            
            # 创建时间特征
            if 'data_date' in data.columns:
                data['data_date'] = pd.to_datetime(data['data_date'])
                engineered_data['year'] = data['data_date'].dt.year
                engineered_data['month'] = data['data_date'].dt.month
                engineered_data['quarter'] = data['data_date'].dt.quarter
                engineered_data['day_of_year'] = data['data_date'].dt.dayofyear
            
            logger.info(f"特征工程完成，新增 {len(engineered_data.columns) - len(data.columns)} 个特征")
            return engineered_data
            
        except Exception as e:
            logger.error(f"特征工程失败: {e}")
            raise DataQualityError(f"特征工程失败: {e}")
    
    def validate_data_rules(self, data: pd.DataFrame) -> Dict[str, Any]:
        """验证数据规则"""
        try:
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            # 检查必填字段
            required_fields = ['tenant_id', 'data_type', 'data_date']
            for field in required_fields:
                if field in data.columns and data[field].isnull().any():
                    validation_result['errors'].append(f"必填字段 {field} 存在空值")
                    validation_result['is_valid'] = False
            
            # 检查数值字段范围
            numeric_fields = ['rd_asset', 'design_asset', 'production_asset', 'marketing_asset', 'delivery_asset', 'channel_asset']
            for field in numeric_fields:
                if field in data.columns:
                    if (data[field] < 0).any():
                        validation_result['errors'].append(f"字段 {field} 存在负值")
                        validation_result['is_valid'] = False
                    
                    if (data[field] > 1000000).any():
                        validation_result['warnings'].append(f"字段 {field} 存在异常大的值")
            
            # 检查能力字段范围
            capability_fields = ['rd_capability', 'design_capability', 'production_capability', 'marketing_capability', 'delivery_capability', 'channel_capability']
            for field in capability_fields:
                if field in data.columns:
                    if (data[field] < 0).any() or (data[field] > 1).any():
                        validation_result['errors'].append(f"字段 {field} 超出范围 [0, 1]")
                        validation_result['is_valid'] = False
            
            logger.info(f"数据规则验证完成: {validation_result}")
            return validation_result
            
        except Exception as e:
            logger.error(f"数据规则验证失败: {e}")
            raise DataQualityError(f"数据规则验证失败: {e}")
    
    def calculate_data_quality_score(self, data: pd.DataFrame) -> float:
        """计算数据质量分数"""
        try:
            quality_metrics = self.validate_data_quality(data)
            return quality_metrics['overall_score']
            
        except Exception as e:
            logger.error(f"数据质量分数计算失败: {e}")
            raise DataQualityError(f"数据质量分数计算失败: {e}")
    
    def treat_outliers(self, data: pd.DataFrame, column: str, method: str = 'remove') -> pd.DataFrame:
        """处理异常值"""
        try:
            if column not in data.columns:
                raise ValidationError(f"列 {column} 不存在于数据中")
            
            if method == 'remove':
                outliers = self.detect_outliers_iqr(data, column)
                return data.drop(outliers)
            
            elif method == 'replace':
                outliers = self.detect_outliers_iqr(data, column)
                data_copy = data.copy()
                # 用中位数替换异常值
                median_value = data[column].median()
                data_copy.loc[outliers, column] = median_value
                return data_copy
            
            elif method == 'cap':
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
    
    def transform_data(self, data: pd.DataFrame, column: str, method: str) -> pd.DataFrame:
        """数据转换"""
        try:
            if column not in data.columns:
                raise ValidationError(f"列 {column} 不存在于数据中")
            
            data_copy = data.copy()
            
            if method == 'log':
                data_copy[f'{column}_log'] = np.log1p(data[column])
            elif method == 'sqrt':
                data_copy[f'{column}_sqrt'] = np.sqrt(data[column])
            elif method == 'square':
                data_copy[f'{column}_square'] = data[column] ** 2
            elif method == 'reciprocal':
                data_copy[f'{column}_reciprocal'] = 1 / (data[column] + 1e-8)
            else:
                raise ValidationError(f"不支持的转换方法: {method}")
            
            logger.info(f"数据转换完成: {column} -> {method}")
            return data_copy
            
        except Exception as e:
            logger.error(f"数据转换失败: {e}")
            raise DataQualityError(f"数据转换失败: {e}")
    
    def split_data(self, data: pd.DataFrame, test_size: float = 0.2, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """数据分割"""
        try:
            from sklearn.model_selection import train_test_split
            
            train_data, test_data = train_test_split(
                data, test_size=test_size, random_state=random_state
            )
            
            logger.info(f"数据分割完成: 训练集 {len(train_data)} 条，测试集 {len(test_data)} 条")
            return train_data, test_data
            
        except Exception as e:
            logger.error(f"数据分割失败: {e}")
            raise DataQualityError(f"数据分割失败: {e}")
    
    def cross_validation_split(self, data: pd.DataFrame, n_splits: int = 5) -> List[Tuple[np.ndarray, np.ndarray]]:
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
    
    def impute_missing_values(self, data: pd.DataFrame, column: str, method: str = 'knn') -> pd.DataFrame:
        """插补缺失值"""
        try:
            if column not in data.columns:
                raise ValidationError(f"列 {column} 不存在于数据中")
            
            data_copy = data.copy()
            
            if method == 'knn':
                imputer = KNNImputer(n_neighbors=5)
            elif method == 'iterative':
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
                'completeness': self._calculate_completeness(data),
                'consistency': self._calculate_consistency(data),
                'accuracy': self._calculate_accuracy(data),
                'timeliness': self._calculate_timeliness(data),
                'validity': self._calculate_validity(data)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"质量指标计算失败: {e}")
            raise DataQualityError(f"质量指标计算失败: {e}")
    
    def preprocess_pipeline(self, data: pd.DataFrame, target_columns: List[str], 
                          handle_outliers: bool = True, handle_missing: bool = True, 
                          standardize: bool = True) -> pd.DataFrame:
        """完整的数据预处理流水线"""
        try:
            processed_data = data.copy()
            
            # 处理缺失值
            if handle_missing:
                for column in target_columns:
                    if column in processed_data.columns and processed_data[column].isnull().any():
                        processed_data = self.handle_missing_values(processed_data, column, method='mean')
            
            # 处理异常值
            if handle_outliers:
                for column in target_columns:
                    if column in processed_data.columns:
                        processed_data = self.treat_outliers(processed_data, column, method='cap')
            
            # 标准化
            if standardize:
                processed_data = self.standardize_data(processed_data, target_columns)
            
            logger.info("数据预处理流水线完成")
            return processed_data
            
        except Exception as e:
            logger.error(f"数据预处理流水线失败: {e}")
            raise DataQualityError(f"数据预处理流水线失败: {e}")


