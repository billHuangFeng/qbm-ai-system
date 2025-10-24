"""
数据处理器
提供数据清洗、预处理和特征工程功能
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    """数据处理器类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def clean_customer_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        清洗客户数据
        
        Args:
            data: 原始客户数据
            
        Returns:
            清洗后的客户数据
        """
        try:
            df = data.copy()
            
            # 处理缺失值
            df['customer_value_score'] = df['customer_value_score'].fillna(0)
            df['customer_lifetime_value'] = df['customer_lifetime_value'].fillna(0)
            df['customer_satisfaction'] = df['customer_satisfaction'].fillna(0)
            df['customer_retention_rate'] = df['customer_retention_rate'].fillna(0)
            
            # 处理字符串字段
            string_columns = ['customer_name', 'contact_person', 'industry', 'city']
            for col in string_columns:
                if col in df.columns:
                    df[col] = df[col].fillna('').astype(str).str.strip()
            
            # 处理日期字段
            date_columns = ['first_contact_date', 'last_contact_date', 'created_at']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # 处理布尔字段
            if 'is_vip' in df.columns:
                df['is_vip'] = df['is_vip'].astype(bool)
            
            self.logger.info(f"客户数据清洗完成，处理了 {len(df)} 条记录")
            return df
            
        except Exception as e:
            self.logger.error(f"客户数据清洗失败: {e}")
            raise
    
    def clean_product_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        清洗产品数据
        
        Args:
            data: 原始产品数据
            
        Returns:
            清洗后的产品数据
        """
        try:
            df = data.copy()
            
            # 处理数值字段
            numeric_columns = [
                'base_price', 'cost_price', 'profit_margin', 'quality_score',
                'customer_satisfaction', 'market_share', 'sales_volume', 'revenue'
            ]
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # 处理字符串字段
            string_columns = ['product_name', 'product_category', 'product_type', 'description']
            for col in string_columns:
                if col in df.columns:
                    df[col] = df[col].fillna('').astype(str).str.strip()
            
            # 处理日期字段
            date_columns = ['launch_date', 'end_of_life_date', 'created_at']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # 处理布尔字段
            if 'is_featured' in df.columns:
                df['is_featured'] = df['is_featured'].astype(bool)
            
            self.logger.info(f"产品数据清洗完成，处理了 {len(df)} 条记录")
            return df
            
        except Exception as e:
            self.logger.error(f"产品数据清洗失败: {e}")
            raise
    
    def clean_financial_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        清洗财务数据
        
        Args:
            data: 原始财务数据
            
        Returns:
            清洗后的财务数据
        """
        try:
            df = data.copy()
            
            # 处理数值字段
            numeric_columns = [
                'amount', 'exchange_rate', 'variance_amount', 'variance_percentage',
                'cash_flow_impact', 'tax_amount', 'tax_rate'
            ]
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # 处理日期字段
            date_columns = ['transaction_date', 'accounting_date', 'due_date', 'created_at']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # 处理字符串字段
            string_columns = ['financial_name', 'financial_type', 'category', 'description']
            for col in string_columns:
                if col in df.columns:
                    df[col] = df[col].fillna('').astype(str).str.strip()
            
            self.logger.info(f"财务数据清洗完成，处理了 {len(df)} 条记录")
            return df
            
        except Exception as e:
            self.logger.error(f"财务数据清洗失败: {e}")
            raise
    
    def create_customer_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        创建客户特征
        
        Args:
            data: 清洗后的客户数据
            
        Returns:
            包含特征的客户数据
        """
        try:
            df = data.copy()
            
            # 客户价值等级
            df['value_level'] = pd.cut(
                df['customer_lifetime_value'],
                bins=[0, 100000, 500000, 1000000, float('inf')],
                labels=['低价值', '中价值', '高价值', '超高价值']
            )
            
            # 客户活跃度
            if 'last_contact_date' in df.columns and 'created_at' in df.columns:
                df['days_since_last_contact'] = (datetime.now() - df['last_contact_date']).dt.days
                df['customer_age_days'] = (datetime.now() - df['created_at']).dt.days
                df['contact_frequency'] = df['customer_age_days'] / (df['days_since_last_contact'] + 1)
            
            # 满意度等级
            df['satisfaction_level'] = pd.cut(
                df['customer_satisfaction'],
                bins=[0, 2, 3, 4, 5],
                labels=['不满意', '一般', '满意', '非常满意']
            )
            
            # 留存率等级
            df['retention_level'] = pd.cut(
                df['customer_retention_rate'],
                bins=[0, 0.5, 0.7, 0.85, 1.0],
                labels=['低留存', '中留存', '高留存', '超高留存']
            )
            
            self.logger.info("客户特征创建完成")
            return df
            
        except Exception as e:
            self.logger.error(f"客户特征创建失败: {e}")
            raise
    
    def create_product_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        创建产品特征
        
        Args:
            data: 清洗后的产品数据
            
        Returns:
            包含特征的产品数据
        """
        try:
            df = data.copy()
            
            # 利润率等级
            df['profit_level'] = pd.cut(
                df['profit_margin'],
                bins=[0, 20, 40, 60, 100],
                labels=['低利润', '中利润', '高利润', '超高利润']
            )
            
            # 价格等级
            df['price_level'] = pd.cut(
                df['base_price'],
                bins=[0, 10000, 50000, 100000, float('inf')],
                labels=['低价', '中价', '高价', '超高价']
            )
            
            # 生命周期阶段
            if 'launch_date' in df.columns:
                df['product_age_days'] = (datetime.now() - df['launch_date']).dt.days
                df['lifecycle_stage_numeric'] = pd.cut(
                    df['product_age_days'],
                    bins=[0, 365, 1095, 1825, float('inf')],
                    labels=['新上市', '成长期', '成熟期', '衰退期']
                )
            
            # 市场表现等级
            df['market_performance'] = pd.cut(
                df['market_share'],
                bins=[0, 5, 15, 30, 100],
                labels=['低份额', '中份额', '高份额', '主导地位']
            )
            
            self.logger.info("产品特征创建完成")
            return df
            
        except Exception as e:
            self.logger.error(f"产品特征创建失败: {e}")
            raise
    
    def create_financial_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        创建财务特征
        
        Args:
            data: 清洗后的财务数据
            
        Returns:
            包含特征的财务数据
        """
        try:
            df = data.copy()
            
            # 金额等级
            df['amount_level'] = pd.cut(
                abs(df['amount']),
                bins=[0, 10000, 100000, 1000000, float('inf')],
                labels=['小额', '中额', '大额', '超大额']
            )
            
            # 收入/支出类型
            df['transaction_type'] = df['amount'].apply(
                lambda x: '收入' if x > 0 else '支出' if x < 0 else '其他'
            )
            
            # 时间特征
            if 'transaction_date' in df.columns:
                df['year'] = df['transaction_date'].dt.year
                df['month'] = df['transaction_date'].dt.month
                df['quarter'] = df['transaction_date'].dt.quarter
                df['day_of_week'] = df['transaction_date'].dt.dayofweek
                df['is_weekend'] = df['day_of_week'].isin([5, 6])
            
            # 现金流影响等级
            if 'cash_flow_impact' in df.columns:
                df['cash_flow_level'] = pd.cut(
                    abs(df['cash_flow_impact']),
                    bins=[0, 50000, 200000, 500000, float('inf')],
                    labels=['低影响', '中影响', '高影响', '超高影响']
                )
            
            self.logger.info("财务特征创建完成")
            return df
            
        except Exception as e:
            self.logger.error(f"财务特征创建失败: {e}")
            raise
    
    def normalize_data(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        数据标准化
        
        Args:
            data: 原始数据
            columns: 需要标准化的列名
            
        Returns:
            标准化后的数据
        """
        try:
            df = data.copy()
            
            for col in columns:
                if col in df.columns:
                    # 使用Z-score标准化
                    mean_val = df[col].mean()
                    std_val = df[col].std()
                    if std_val > 0:
                        df[f'{col}_normalized'] = (df[col] - mean_val) / std_val
                    else:
                        df[f'{col}_normalized'] = 0
            
            self.logger.info(f"数据标准化完成，处理了 {len(columns)} 个字段")
            return df
            
        except Exception as e:
            self.logger.error(f"数据标准化失败: {e}")
            raise
    
    def detect_outliers(self, data: pd.DataFrame, columns: List[str], method: str = 'iqr') -> Dict[str, List[int]]:
        """
        异常值检测
        
        Args:
            data: 数据
            columns: 需要检测的列名
            method: 检测方法 ('iqr' 或 'zscore')
            
        Returns:
            异常值索引字典
        """
        try:
            outliers = {}
            
            for col in columns:
                if col not in data.columns:
                    continue
                
                if method == 'iqr':
                    Q1 = data[col].quantile(0.25)
                    Q3 = data[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    outlier_indices = data[(data[col] < lower_bound) | (data[col] > upper_bound)].index.tolist()
                
                elif method == 'zscore':
                    z_scores = np.abs((data[col] - data[col].mean()) / data[col].std())
                    outlier_indices = data[z_scores > 3].index.tolist()
                
                outliers[col] = outlier_indices
            
            self.logger.info(f"异常值检测完成，检测了 {len(columns)} 个字段")
            return outliers
            
        except Exception as e:
            self.logger.error(f"异常值检测失败: {e}")
            raise
    
    def aggregate_data(self, data: pd.DataFrame, group_by: List[str], agg_dict: Dict[str, List[str]]) -> pd.DataFrame:
        """
        数据聚合
        
        Args:
            data: 原始数据
            group_by: 分组字段
            agg_dict: 聚合字典
            
        Returns:
            聚合后的数据
        """
        try:
            result = data.groupby(group_by).agg(agg_dict).reset_index()
            
            # 展平多级列名
            result.columns = ['_'.join(col).strip() if col[1] else col[0] for col in result.columns.values]
            
            self.logger.info(f"数据聚合完成，按 {group_by} 分组")
            return result
            
        except Exception as e:
            self.logger.error(f"数据聚合失败: {e}")
            raise



