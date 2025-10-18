"""
产品分析器
提供产品性能分析、产品组合分析、产品生命周期分析等功能
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import logging

logger = logging.getLogger(__name__)

class ProductAnalyzer:
    """产品分析器类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
    
    def analyze_product_performance(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        产品性能分析
        
        Args:
            data: 产品数据
            
        Returns:
            产品性能分析结果
        """
        try:
            # 基础性能指标
            performance_metrics = {
                'total_products': len(data),
                'active_products': len(data[data['status'] == 'active']),
                'featured_products': len(data[data['is_featured'] == True]),
                'total_revenue': data['revenue'].sum(),
                'total_sales_volume': data['sales_volume'].sum(),
                'avg_profit_margin': data['profit_margin'].mean(),
                'avg_quality_score': data['quality_score'].mean(),
                'avg_customer_satisfaction': data['customer_satisfaction'].mean(),
                'avg_market_share': data['market_share'].mean()
            }
            
            # 产品分类分析
            category_analysis = data.groupby('product_category').agg({
                'revenue': ['count', 'sum', 'mean'],
                'sales_volume': 'sum',
                'profit_margin': 'mean',
                'customer_satisfaction': 'mean'
            }).round(2)
            
            # 产品类型分析
            type_analysis = data.groupby('product_type').agg({
                'revenue': ['count', 'sum', 'mean'],
                'base_price': 'mean',
                'profit_margin': 'mean'
            }).round(2)
            
            # 生命周期阶段分析
            lifecycle_analysis = data.groupby('lifecycle_stage').agg({
                'revenue': ['count', 'sum', 'mean'],
                'sales_volume': 'sum',
                'market_share': 'mean'
            }).round(2)
            
            # 价格分析
            price_analysis = {
                'avg_price': data['base_price'].mean(),
                'median_price': data['base_price'].median(),
                'price_range': {
                    'min': data['base_price'].min(),
                    'max': data['base_price'].max()
                },
                'price_quartiles': data['base_price'].quantile([0.25, 0.5, 0.75]).to_dict()
            }
            
            result = {
                'performance_metrics': performance_metrics,
                'category_analysis': category_analysis.to_dict(),
                'type_analysis': type_analysis.to_dict(),
                'lifecycle_analysis': lifecycle_analysis.to_dict(),
                'price_analysis': price_analysis,
                'insights': self._generate_performance_insights(performance_metrics, category_analysis)
            }
            
            self.logger.info("产品性能分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"产品性能分析失败: {e}")
            raise
    
    def analyze_product_portfolio(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        产品组合分析
        
        Args:
            data: 产品数据
            
        Returns:
            产品组合分析结果
        """
        try:
            # 产品组合矩阵（收入 vs 增长率）
            portfolio_matrix = self._create_portfolio_matrix(data)
            
            # 产品集中度分析
            concentration_analysis = self._analyze_concentration(data)
            
            # 产品相关性分析
            correlation_analysis = self._analyze_correlations(data)
            
            # 产品组合优化建议
            optimization_suggestions = self._generate_optimization_suggestions(portfolio_matrix, concentration_analysis)
            
            result = {
                'portfolio_matrix': portfolio_matrix,
                'concentration_analysis': concentration_analysis,
                'correlation_analysis': correlation_analysis,
                'optimization_suggestions': optimization_suggestions,
                'insights': self._generate_portfolio_insights(portfolio_matrix, concentration_analysis)
            }
            
            self.logger.info("产品组合分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"产品组合分析失败: {e}")
            raise
    
    def predict_product_success(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        预测产品成功度
        
        Args:
            data: 产品数据
            
        Returns:
            产品成功度预测结果
        """
        try:
            # 准备特征
            feature_columns = [
                'base_price', 'cost_price', 'profit_margin', 'quality_score',
                'customer_satisfaction', 'market_share'
            ]
            
            # 处理缺失值
            feature_data = data[feature_columns].fillna(0)
            
            # 创建成功度标签（基于收入、销量、满意度等综合指标）
            success_score = (
                data['revenue'].fillna(0) / data['revenue'].fillna(0).max() * 0.4 +
                data['sales_volume'].fillna(0) / data['sales_volume'].fillna(0).max() * 0.3 +
                data['customer_satisfaction'].fillna(0) / 5 * 0.3
            )
            
            # 分割训练和测试集
            X_train, X_test, y_train, y_test = train_test_split(
                feature_data, success_score, test_size=0.2, random_state=42
            )
            
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
            
            # 预测所有产品的成功度
            all_predictions = model.predict(feature_data)
            
            # 成功度分类
            success_categories = pd.cut(
                all_predictions,
                bins=[0, 0.3, 0.6, 0.8, 1.0],
                labels=['低成功度', '中等成功度', '高成功度', '超高成功度']
            )
            
            result = {
                'model_performance': {
                    'mse': mse,
                    'r2_score': r2,
                    'rmse': np.sqrt(mse)
                },
                'feature_importance': feature_importance,
                'predictions': all_predictions.tolist(),
                'success_categories': success_categories.tolist(),
                'insights': self._generate_success_insights(feature_importance, r2, success_categories)
            }
            
            self.logger.info("产品成功度预测完成")
            return result
            
        except Exception as e:
            self.logger.error(f"产品成功度预测失败: {e}")
            raise
    
    def analyze_product_lifecycle(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        产品生命周期分析
        
        Args:
            data: 产品数据
            
        Returns:
            产品生命周期分析结果
        """
        try:
            # 生命周期阶段分析
            lifecycle_stages = data['lifecycle_stage'].value_counts()
            
            # 各阶段性能分析
            stage_performance = data.groupby('lifecycle_stage').agg({
                'revenue': ['count', 'sum', 'mean'],
                'sales_volume': 'sum',
                'market_share': 'mean',
                'customer_satisfaction': 'mean',
                'profit_margin': 'mean'
            }).round(2)
            
            # 产品年龄分析
            if 'launch_date' in data.columns:
                data['product_age_days'] = (pd.Timestamp.now() - pd.to_datetime(data['launch_date'])).dt.days
                data['product_age_years'] = data['product_age_days'] / 365
                
                age_analysis = data.groupby(pd.cut(data['product_age_years'], bins=[0, 1, 3, 5, 10, float('inf')])).agg({
                    'revenue': ['count', 'sum', 'mean'],
                    'customer_satisfaction': 'mean'
                }).round(2)
            else:
                age_analysis = None
            
            # 生命周期趋势分析
            trend_analysis = self._analyze_lifecycle_trends(data)
            
            result = {
                'lifecycle_distribution': lifecycle_stages.to_dict(),
                'stage_performance': stage_performance.to_dict(),
                'age_analysis': age_analysis.to_dict() if age_analysis is not None else None,
                'trend_analysis': trend_analysis,
                'insights': self._generate_lifecycle_insights(lifecycle_stages, stage_performance)
            }
            
            self.logger.info("产品生命周期分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"产品生命周期分析失败: {e}")
            raise
    
    def _create_portfolio_matrix(self, data: pd.DataFrame) -> Dict[str, Any]:
        """创建产品组合矩阵"""
        try:
            # 计算相对市场份额和增长率
            data['relative_market_share'] = data['market_share'] / data['market_share'].median()
            data['growth_rate'] = data['sales_volume'].pct_change().fillna(0)
            
            # 分类产品
            data['portfolio_category'] = '问题产品'
            data.loc[(data['relative_market_share'] > 1) & (data['growth_rate'] > 0), 'portfolio_category'] = '明星产品'
            data.loc[(data['relative_market_share'] > 1) & (data['growth_rate'] <= 0), 'portfolio_category'] = '现金牛产品'
            data.loc[(data['relative_market_share'] <= 1) & (data['growth_rate'] <= 0), 'portfolio_category'] = '瘦狗产品'
            
            portfolio_distribution = data['portfolio_category'].value_counts().to_dict()
            
            return {
                'distribution': portfolio_distribution,
                'products': data[['product_name', 'portfolio_category', 'revenue', 'market_share']].to_dict('records')
            }
        except Exception as e:
            self.logger.error(f"产品组合矩阵创建失败: {e}")
            return {}
    
    def _analyze_concentration(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析产品集中度"""
        try:
            # 收入集中度
            revenue_sorted = data['revenue'].sort_values(ascending=False)
            cumulative_revenue = revenue_sorted.cumsum()
            total_revenue = revenue_sorted.sum()
            
            # 计算80-20法则
            top_20_percent = int(len(data) * 0.2)
            top_20_revenue = cumulative_revenue.iloc[top_20_percent] if top_20_percent < len(data) else total_revenue
            concentration_ratio = (top_20_revenue / total_revenue) * 100
            
            # 赫芬达尔指数
            market_shares = data['market_share'] / 100
            hhi = (market_shares ** 2).sum()
            
            return {
                'concentration_ratio': concentration_ratio,
                'hhi_index': hhi,
                'top_20_percent_products': top_20_percent,
                'top_20_percent_revenue_share': concentration_ratio
            }
        except Exception as e:
            self.logger.error(f"集中度分析失败: {e}")
            return {}
    
    def _analyze_correlations(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析产品相关性"""
        try:
            numeric_columns = ['base_price', 'cost_price', 'profit_margin', 'quality_score', 
                             'customer_satisfaction', 'market_share', 'revenue', 'sales_volume']
            
            correlation_matrix = data[numeric_columns].corr()
            
            # 找出强相关关系
            strong_correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:
                        strong_correlations.append({
                            'feature1': correlation_matrix.columns[i],
                            'feature2': correlation_matrix.columns[j],
                            'correlation': corr_value
                        })
            
            return {
                'correlation_matrix': correlation_matrix.to_dict(),
                'strong_correlations': strong_correlations
            }
        except Exception as e:
            self.logger.error(f"相关性分析失败: {e}")
            return {}
    
    def _analyze_lifecycle_trends(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析生命周期趋势"""
        try:
            # 按生命周期阶段分析趋势
            trends = {}
            
            for stage in data['lifecycle_stage'].unique():
                stage_data = data[data['lifecycle_stage'] == stage]
                trends[stage] = {
                    'avg_revenue': stage_data['revenue'].mean(),
                    'avg_satisfaction': stage_data['customer_satisfaction'].mean(),
                    'avg_market_share': stage_data['market_share'].mean(),
                    'product_count': len(stage_data)
                }
            
            return trends
        except Exception as e:
            self.logger.error(f"生命周期趋势分析失败: {e}")
            return {}
    
    def _generate_performance_insights(self, metrics: Dict, category_analysis: pd.DataFrame) -> List[str]:
        """生成性能洞察"""
        insights = []
        
        if metrics['avg_profit_margin'] > 50:
            insights.append("产品平均利润率较高，盈利能力良好")
        elif metrics['avg_profit_margin'] < 20:
            insights.append("产品平均利润率较低，需要优化成本结构")
        
        if metrics['avg_customer_satisfaction'] > 4:
            insights.append("客户满意度较高，产品质量得到认可")
        elif metrics['avg_customer_satisfaction'] < 3:
            insights.append("客户满意度较低，需要改进产品质量")
        
        # 找出表现最好的产品类别
        if not category_analysis.empty:
            best_category = category_analysis[('revenue', 'sum')].idxmax()
            insights.append(f"表现最好的产品类别是{best_category}")
        
        return insights
    
    def _generate_portfolio_insights(self, portfolio_matrix: Dict, concentration: Dict) -> List[str]:
        """生成组合洞察"""
        insights = []
        
        # 分析产品组合分布
        if 'distribution' in portfolio_matrix:
            distribution = portfolio_matrix['distribution']
            if '明星产品' in distribution and distribution['明星产品'] > 0:
                insights.append("拥有明星产品，具有良好的增长潜力")
            
            if '现金牛产品' in distribution and distribution['现金牛产品'] > 0:
                insights.append("拥有现金牛产品，能够提供稳定的现金流")
        
        # 分析集中度
        if 'concentration_ratio' in concentration:
            if concentration['concentration_ratio'] > 80:
                insights.append("产品收入高度集中，存在风险")
            elif concentration['concentration_ratio'] < 40:
                insights.append("产品收入分布较为均衡")
        
        return insights
    
    def _generate_success_insights(self, feature_importance: Dict, r2_score: float, success_categories: pd.Series) -> List[str]:
        """生成成功度洞察"""
        insights = []
        
        # 模型性能
        if r2_score > 0.8:
            insights.append("产品成功度预测模型准确性很高")
        elif r2_score > 0.6:
            insights.append("产品成功度预测模型准确性良好")
        
        # 特征重要性
        most_important = max(feature_importance.keys(), key=lambda k: feature_importance[k])
        insights.append(f"影响产品成功的最重要因素是{most_important}")
        
        # 成功度分布
        high_success = (success_categories == '高成功度').sum() + (success_categories == '超高成功度').sum()
        if high_success > len(success_categories) * 0.3:
            insights.append("高成功度产品比例较高，产品组合健康")
        
        return insights
    
    def _generate_lifecycle_insights(self, lifecycle_stages: pd.Series, stage_performance: pd.DataFrame) -> List[str]:
        """生成生命周期洞察"""
        insights = []
        
        # 分析生命周期分布
        if '成熟期' in lifecycle_stages.index and lifecycle_stages['成熟期'] > lifecycle_stages.sum() * 0.4:
            insights.append("产品主要集中在成熟期，需要关注产品创新")
        
        if '新上市' in lifecycle_stages.index and lifecycle_stages['新上市'] > lifecycle_stages.sum() * 0.3:
            insights.append("新产品比例较高，具有良好的增长潜力")
        
        return insights
    
    def _generate_optimization_suggestions(self, portfolio_matrix: Dict, concentration: Dict) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        # 基于产品组合矩阵的建议
        if 'distribution' in portfolio_matrix:
            distribution = portfolio_matrix['distribution']
            
            if '问题产品' in distribution and distribution['问题产品'] > 0:
                suggestions.append("考虑对问题产品进行重新定位或淘汰")
            
            if '瘦狗产品' in distribution and distribution['瘦狗产品'] > 0:
                suggestions.append("建议逐步淘汰瘦狗产品，释放资源")
            
            if '明星产品' in distribution and distribution['明星产品'] > 0:
                suggestions.append("加大对明星产品的投入，促进其向现金牛产品转化")
        
        # 基于集中度的建议
        if 'concentration_ratio' in concentration:
            if concentration['concentration_ratio'] > 80:
                suggestions.append("产品收入过于集中，建议分散风险，开发新产品")
        
        return suggestions
