"""
客户分析器
提供客户价值分析、客户细分、客户生命周期分析等功能
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import logging

logger = logging.getLogger(__name__)

class CustomerAnalyzer:
    """客户分析器类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=2)
    
    def analyze_customer_value(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        客户价值分析
        
        Args:
            data: 客户数据
            
        Returns:
            客户价值分析结果
        """
        try:
            # 计算客户价值指标
            value_metrics = {
                'total_customers': len(data),
                'avg_lifetime_value': data['customer_lifetime_value'].mean(),
                'median_lifetime_value': data['customer_lifetime_value'].median(),
                'total_lifetime_value': data['customer_lifetime_value'].sum(),
                'avg_value_score': data['customer_value_score'].mean(),
                'avg_satisfaction': data['customer_satisfaction'].mean(),
                'avg_retention_rate': data['customer_retention_rate'].mean(),
                'vip_customers': data['is_vip'].sum(),
                'vip_percentage': (data['is_vip'].sum() / len(data)) * 100
            }
            
            # 客户价值分布
            value_distribution = {
                'high_value_customers': len(data[data['customer_lifetime_value'] > data['customer_lifetime_value'].quantile(0.8)]),
                'medium_value_customers': len(data[(data['customer_lifetime_value'] > data['customer_lifetime_value'].quantile(0.4)) & 
                                                 (data['customer_lifetime_value'] <= data['customer_lifetime_value'].quantile(0.8))]),
                'low_value_customers': len(data[data['customer_lifetime_value'] <= data['customer_lifetime_value'].quantile(0.4)])
            }
            
            # 行业分析
            industry_analysis = data.groupby('industry').agg({
                'customer_lifetime_value': ['count', 'mean', 'sum'],
                'customer_satisfaction': 'mean',
                'customer_retention_rate': 'mean'
            }).round(2)
            
            # 地区分析
            region_analysis = data.groupby(['province', 'city']).agg({
                'customer_lifetime_value': ['count', 'mean', 'sum'],
                'customer_satisfaction': 'mean'
            }).round(2)
            
            result = {
                'value_metrics': value_metrics,
                'value_distribution': value_distribution,
                'industry_analysis': industry_analysis.to_dict(),
                'region_analysis': region_analysis.to_dict(),
                'insights': self._generate_customer_insights(value_metrics, value_distribution)
            }
            
            self.logger.info("客户价值分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"客户价值分析失败: {e}")
            raise
    
    def customer_segmentation(self, data: pd.DataFrame, n_clusters: int = 4) -> Dict[str, Any]:
        """
        客户细分
        
        Args:
            data: 客户数据
            n_clusters: 聚类数量
            
        Returns:
            客户细分结果
        """
        try:
            # 选择用于聚类的特征
            features = ['customer_lifetime_value', 'customer_value_score', 
                       'customer_satisfaction', 'customer_retention_rate']
            
            # 处理缺失值
            feature_data = data[features].fillna(0)
            
            # 标准化数据
            scaled_data = self.scaler.fit_transform(feature_data)
            
            # K-means聚类
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(scaled_data)
            
            # 计算轮廓系数
            silhouette_avg = silhouette_score(scaled_data, clusters)
            
            # 添加聚类标签
            data_with_clusters = data.copy()
            data_with_clusters['cluster'] = clusters
            
            # 分析每个聚类
            cluster_analysis = {}
            for i in range(n_clusters):
                cluster_data = data_with_clusters[data_with_clusters['cluster'] == i]
                cluster_analysis[f'cluster_{i}'] = {
                    'size': len(cluster_data),
                    'percentage': (len(cluster_data) / len(data)) * 100,
                    'avg_lifetime_value': cluster_data['customer_lifetime_value'].mean(),
                    'avg_value_score': cluster_data['customer_value_score'].mean(),
                    'avg_satisfaction': cluster_data['customer_satisfaction'].mean(),
                    'avg_retention_rate': cluster_data['customer_retention_rate'].mean(),
                    'vip_percentage': (cluster_data['is_vip'].sum() / len(cluster_data)) * 100
                }
            
            # 生成聚类洞察
            insights = self._generate_segmentation_insights(cluster_analysis)
            
            result = {
                'n_clusters': n_clusters,
                'silhouette_score': silhouette_avg,
                'cluster_analysis': cluster_analysis,
                'insights': insights,
                'cluster_labels': clusters.tolist()
            }
            
            self.logger.info(f"客户细分完成，分为 {n_clusters} 个聚类")
            return result
            
        except Exception as e:
            self.logger.error(f"客户细分失败: {e}")
            raise
    
    def analyze_customer_lifecycle(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        客户生命周期分析
        
        Args:
            data: 客户数据
            
        Returns:
            客户生命周期分析结果
        """
        try:
            # 计算客户年龄（从首次接触开始）
            if 'first_contact_date' in data.columns:
                data['customer_age_days'] = (pd.Timestamp.now() - pd.to_datetime(data['first_contact_date'])).dt.days
                data['customer_age_months'] = data['customer_age_days'] / 30
                
                # 生命周期阶段
                data['lifecycle_stage'] = pd.cut(
                    data['customer_age_months'],
                    bins=[0, 6, 24, 60, float('inf')],
                    labels=['新客户', '成长期', '成熟期', '忠诚期']
                )
                
                # 各阶段分析
                lifecycle_analysis = data.groupby('lifecycle_stage').agg({
                    'customer_lifetime_value': ['count', 'mean', 'sum'],
                    'customer_satisfaction': 'mean',
                    'customer_retention_rate': 'mean',
                    'customer_value_score': 'mean'
                }).round(2)
                
                # 流失风险分析
                churn_risk = self._calculate_churn_risk(data)
                
                result = {
                    'lifecycle_analysis': lifecycle_analysis.to_dict(),
                    'churn_risk': churn_risk,
                    'insights': self._generate_lifecycle_insights(lifecycle_analysis, churn_risk)
                }
            else:
                result = {
                    'error': '缺少首次接触日期数据，无法进行生命周期分析'
                }
            
            self.logger.info("客户生命周期分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"客户生命周期分析失败: {e}")
            raise
    
    def predict_customer_value(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        预测客户价值
        
        Args:
            data: 客户数据
            
        Returns:
            客户价值预测结果
        """
        try:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_squared_error, r2_score
            
            # 准备特征
            feature_columns = ['customer_value_score', 'customer_satisfaction', 'customer_retention_rate']
            if 'customer_age_days' in data.columns:
                feature_columns.append('customer_age_days')
            
            X = data[feature_columns].fillna(0)
            y = data['customer_lifetime_value']
            
            # 分割训练和测试集
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # 训练模型
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # 预测
            y_pred = model.predict(X_test)
            
            # 评估模型
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # 特征重要性
            feature_importance = dict(zip(feature_columns, model.feature_importances_))
            
            # 预测所有客户的价值
            all_predictions = model.predict(X)
            
            result = {
                'model_performance': {
                    'mse': mse,
                    'r2_score': r2,
                    'rmse': np.sqrt(mse)
                },
                'feature_importance': feature_importance,
                'predictions': all_predictions.tolist(),
                'insights': self._generate_prediction_insights(feature_importance, r2)
            }
            
            self.logger.info("客户价值预测完成")
            return result
            
        except Exception as e:
            self.logger.error(f"客户价值预测失败: {e}")
            raise
    
    def _generate_customer_insights(self, metrics: Dict, distribution: Dict) -> List[str]:
        """生成客户洞察"""
        insights = []
        
        if metrics['vip_percentage'] > 20:
            insights.append("VIP客户比例较高，说明客户质量良好")
        elif metrics['vip_percentage'] < 5:
            insights.append("VIP客户比例较低，需要提升客户价值")
        
        if metrics['avg_satisfaction'] > 4:
            insights.append("客户满意度较高，客户关系良好")
        elif metrics['avg_satisfaction'] < 3:
            insights.append("客户满意度较低，需要改善服务质量")
        
        if distribution['high_value_customers'] > distribution['low_value_customers']:
            insights.append("高价值客户数量超过低价值客户，客户结构健康")
        else:
            insights.append("低价值客户较多，需要制定客户价值提升策略")
        
        return insights
    
    def _generate_segmentation_insights(self, cluster_analysis: Dict) -> List[str]:
        """生成细分洞察"""
        insights = []
        
        # 找出最大的聚类
        max_cluster = max(cluster_analysis.keys(), key=lambda k: cluster_analysis[k]['size'])
        insights.append(f"最大客户群体是{max_cluster}，占总客户的{cluster_analysis[max_cluster]['percentage']:.1f}%")
        
        # 找出高价值聚类
        high_value_clusters = [k for k, v in cluster_analysis.items() if v['avg_lifetime_value'] > 500000]
        if high_value_clusters:
            insights.append(f"高价值客户群体：{', '.join(high_value_clusters)}")
        
        # 找出高满意度聚类
        high_satisfaction_clusters = [k for k, v in cluster_analysis.items() if v['avg_satisfaction'] > 4]
        if high_satisfaction_clusters:
            insights.append(f"高满意度客户群体：{', '.join(high_satisfaction_clusters)}")
        
        return insights
    
    def _generate_lifecycle_insights(self, lifecycle_analysis: pd.DataFrame, churn_risk: Dict) -> List[str]:
        """生成生命周期洞察"""
        insights = []
        
        # 分析各阶段客户数量
        stage_counts = lifecycle_analysis[('customer_lifetime_value', 'count')]
        max_stage = stage_counts.idxmax()
        insights.append(f"客户主要集中在{max_stage}阶段")
        
        # 分析流失风险
        if churn_risk['high_risk_percentage'] > 20:
            insights.append("高流失风险客户比例较高，需要重点关注")
        
        return insights
    
    def _generate_prediction_insights(self, feature_importance: Dict, r2_score: float) -> List[str]:
        """生成预测洞察"""
        insights = []
        
        # 模型性能
        if r2_score > 0.8:
            insights.append("模型预测准确性很高")
        elif r2_score > 0.6:
            insights.append("模型预测准确性良好")
        else:
            insights.append("模型预测准确性需要改进")
        
        # 特征重要性
        most_important = max(feature_importance.keys(), key=lambda k: feature_importance[k])
        insights.append(f"最重要的预测因子是{most_important}")
        
        return insights
    
    def _calculate_churn_risk(self, data: pd.DataFrame) -> Dict[str, Any]:
        """计算流失风险"""
        try:
            # 基于多个指标计算流失风险
            risk_factors = []
            
            # 满意度低
            if 'customer_satisfaction' in data.columns:
                low_satisfaction = data['customer_satisfaction'] < 3
                risk_factors.append(low_satisfaction)
            
            # 留存率低
            if 'customer_retention_rate' in data.columns:
                low_retention = data['customer_retention_rate'] < 0.7
                risk_factors.append(low_retention)
            
            # 长期未联系
            if 'last_contact_date' in data.columns:
                long_no_contact = (pd.Timestamp.now() - pd.to_datetime(data['last_contact_date'])).dt.days > 90
                risk_factors.append(long_no_contact)
            
            # 计算综合风险分数
            if risk_factors:
                risk_score = sum(risk_factors) / len(risk_factors)
                data['churn_risk_score'] = risk_score
                
                high_risk = risk_score > 0.6
                medium_risk = (risk_score > 0.3) & (risk_score <= 0.6)
                low_risk = risk_score <= 0.3
                
                return {
                    'high_risk_count': high_risk.sum(),
                    'medium_risk_count': medium_risk.sum(),
                    'low_risk_count': low_risk.sum(),
                    'high_risk_percentage': (high_risk.sum() / len(data)) * 100,
                    'avg_risk_score': risk_score.mean()
                }
            else:
                return {'error': '缺少计算流失风险所需的数据'}
                
        except Exception as e:
            self.logger.error(f"流失风险计算失败: {e}")
            return {'error': str(e)}



