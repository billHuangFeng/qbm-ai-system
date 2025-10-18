"""
市场分析器
提供市场趋势分析、竞争分析、市场细分分析等功能
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import logging

logger = logging.getLogger(__name__)

class MarketAnalyzer:
    """市场分析器类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=2)
    
    def analyze_market_trends(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        市场趋势分析
        
        Args:
            data: 市场数据
            
        Returns:
            市场趋势分析结果
        """
        try:
            # 时间趋势分析
            time_trends = self._analyze_time_trends(data)
            
            # 产品类别趋势
            category_trends = self._analyze_category_trends(data)
            
            # 地区趋势分析
            region_trends = self._analyze_region_trends(data)
            
            # 客户行为趋势
            behavior_trends = self._analyze_behavior_trends(data)
            
            result = {
                'time_trends': time_trends,
                'category_trends': category_trends,
                'region_trends': region_trends,
                'behavior_trends': behavior_trends,
                'insights': self._generate_trend_insights(time_trends, category_trends)
            }
            
            self.logger.info("市场趋势分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"市场趋势分析失败: {e}")
            raise
    
    def analyze_competition(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        竞争分析
        
        Args:
            data: 竞争数据
            
        Returns:
            竞争分析结果
        """
        try:
            # 市场份额分析
            market_share_analysis = self._analyze_market_share(data)
            
            # 竞争强度分析
            competition_intensity = self._analyze_competition_intensity(data)
            
            # 竞争优势分析
            competitive_advantages = self._analyze_competitive_advantages(data)
            
            # 竞争威胁分析
            competitive_threats = self._analyze_competitive_threats(data)
            
            result = {
                'market_share_analysis': market_share_analysis,
                'competition_intensity': competition_intensity,
                'competitive_advantages': competitive_advantages,
                'competitive_threats': competitive_threats,
                'insights': self._generate_competition_insights(market_share_analysis, competition_intensity)
            }
            
            self.logger.info("竞争分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"竞争分析失败: {e}")
            raise
    
    def analyze_market_segmentation(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        市场细分分析
        
        Args:
            data: 市场数据
            
        Returns:
            市场细分分析结果
        """
        try:
            # 客户细分
            customer_segments = self._analyze_customer_segments(data)
            
            # 产品细分
            product_segments = self._analyze_product_segments(data)
            
            # 地理细分
            geographic_segments = self._analyze_geographic_segments(data)
            
            # 行为细分
            behavioral_segments = self._analyze_behavioral_segments(data)
            
            result = {
                'customer_segments': customer_segments,
                'product_segments': product_segments,
                'geographic_segments': geographic_segments,
                'behavioral_segments': behavioral_segments,
                'insights': self._generate_segmentation_insights(customer_segments, product_segments)
            }
            
            self.logger.info("市场细分分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"市场细分分析失败: {e}")
            raise
    
    def predict_market_demand(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        预测市场需求
        
        Args:
            data: 市场数据
            
        Returns:
            市场需求预测结果
        """
        try:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_squared_error, r2_score
            
            # 准备特征
            feature_columns = ['market_share', 'customer_satisfaction', 'price_sensitivity', 'seasonality_factor']
            available_features = [col for col in feature_columns if col in data.columns]
            
            if len(available_features) < 2:
                return {'error': '缺少足够的特征数据进行预测'}
            
            X = data[available_features].fillna(0)
            y = data['demand'] if 'demand' in data.columns else data['sales_volume']
            
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
            feature_importance = dict(zip(available_features, model.feature_importances_))
            
            # 预测未来需求
            future_predictions = model.predict(X)
            
            result = {
                'model_performance': {
                    'mse': mse,
                    'r2_score': r2,
                    'rmse': np.sqrt(mse)
                },
                'feature_importance': feature_importance,
                'predictions': future_predictions.tolist(),
                'insights': self._generate_demand_insights(feature_importance, r2)
            }
            
            self.logger.info("市场需求预测完成")
            return result
            
        except Exception as e:
            self.logger.error(f"市场需求预测失败: {e}")
            raise
    
    def _analyze_time_trends(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析时间趋势"""
        try:
            if 'transaction_date' not in data.columns:
                return {'error': '缺少交易日期数据'}
            
            # 按月分析
            data['year_month'] = pd.to_datetime(data['transaction_date']).dt.to_period('M')
            monthly_trends = data.groupby('year_month').agg({
                'amount': ['count', 'sum', 'mean'],
                'sales_volume': 'sum' if 'sales_volume' in data.columns else 'count'
            }).round(2)
            
            # 按季度分析
            data['quarter'] = pd.to_datetime(data['transaction_date']).dt.to_period('Q')
            quarterly_trends = data.groupby('quarter').agg({
                'amount': ['count', 'sum', 'mean'],
                'sales_volume': 'sum' if 'sales_volume' in data.columns else 'count'
            }).round(2)
            
            # 计算增长率
            monthly_growth = monthly_trends[('amount', 'sum')].pct_change().fillna(0)
            quarterly_growth = quarterly_trends[('amount', 'sum')].pct_change().fillna(0)
            
            return {
                'monthly_trends': monthly_trends.to_dict(),
                'quarterly_trends': quarterly_trends.to_dict(),
                'monthly_growth_rate': monthly_growth.to_dict(),
                'quarterly_growth_rate': quarterly_growth.to_dict()
            }
        except Exception as e:
            self.logger.error(f"时间趋势分析失败: {e}")
            return {}
    
    def _analyze_category_trends(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析产品类别趋势"""
        try:
            if 'product_category' not in data.columns:
                return {'error': '缺少产品类别数据'}
            
            # 按类别分析
            category_analysis = data.groupby('product_category').agg({
                'amount': ['count', 'sum', 'mean'],
                'sales_volume': 'sum' if 'sales_volume' in data.columns else 'count',
                'customer_satisfaction': 'mean' if 'customer_satisfaction' in data.columns else 'count'
            }).round(2)
            
            # 类别增长率
            if 'transaction_date' in data.columns:
                data['year_month'] = pd.to_datetime(data['transaction_date']).dt.to_period('M')
                category_monthly = data.groupby(['product_category', 'year_month'])['amount'].sum().unstack(fill_value=0)
                category_growth = category_monthly.pct_change(axis=1).fillna(0)
            else:
                category_growth = None
            
            return {
                'category_analysis': category_analysis.to_dict(),
                'category_growth': category_growth.to_dict() if category_growth is not None else None
            }
        except Exception as e:
            self.logger.error(f"产品类别趋势分析失败: {e}")
            return {}
    
    def _analyze_region_trends(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析地区趋势"""
        try:
            if 'province' not in data.columns and 'city' not in data.columns:
                return {'error': '缺少地区数据'}
            
            # 按省份分析
            if 'province' in data.columns:
                province_analysis = data.groupby('province').agg({
                    'amount': ['count', 'sum', 'mean'],
                    'sales_volume': 'sum' if 'sales_volume' in data.columns else 'count'
                }).round(2)
            else:
                province_analysis = None
            
            # 按城市分析
            if 'city' in data.columns:
                city_analysis = data.groupby('city').agg({
                    'amount': ['count', 'sum', 'mean'],
                    'sales_volume': 'sum' if 'sales_volume' in data.columns else 'count'
                }).round(2)
            else:
                city_analysis = None
            
            return {
                'province_analysis': province_analysis.to_dict() if province_analysis is not None else None,
                'city_analysis': city_analysis.to_dict() if city_analysis is not None else None
            }
        except Exception as e:
            self.logger.error(f"地区趋势分析失败: {e}")
            return {}
    
    def _analyze_behavior_trends(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析客户行为趋势"""
        try:
            behavior_analysis = {}
            
            # 购买频率分析
            if 'customer_id' in data.columns and 'transaction_date' in data.columns:
                customer_purchase_freq = data.groupby('customer_id')['transaction_date'].count()
                behavior_analysis['purchase_frequency'] = {
                    'avg_purchases_per_customer': customer_purchase_freq.mean(),
                    'median_purchases_per_customer': customer_purchase_freq.median(),
                    'high_frequency_customers': (customer_purchase_freq > customer_purchase_freq.quantile(0.8)).sum()
                }
            
            # 价格敏感度分析
            if 'base_price' in data.columns and 'amount' in data.columns:
                price_sensitivity = data.groupby('base_price')['amount'].sum()
                behavior_analysis['price_sensitivity'] = {
                    'price_elasticity': self._calculate_price_elasticity(price_sensitivity),
                    'optimal_price_range': self._find_optimal_price_range(price_sensitivity)
                }
            
            return behavior_analysis
        except Exception as e:
            self.logger.error(f"客户行为趋势分析失败: {e}")
            return {}
    
    def _analyze_market_share(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析市场份额"""
        try:
            if 'market_share' not in data.columns:
                return {'error': '缺少市场份额数据'}
            
            # 总体市场份额
            total_market_share = data['market_share'].sum()
            avg_market_share = data['market_share'].mean()
            
            # 按产品类别的市场份额
            if 'product_category' in data.columns:
                category_market_share = data.groupby('product_category')['market_share'].sum()
                category_share_percentage = (category_market_share / total_market_share * 100).round(2)
            else:
                category_market_share = None
                category_share_percentage = None
            
            # 按地区的市场份额
            if 'province' in data.columns:
                region_market_share = data.groupby('province')['market_share'].sum()
                region_share_percentage = (region_market_share / total_market_share * 100).round(2)
            else:
                region_market_share = None
                region_share_percentage = None
            
            return {
                'total_market_share': total_market_share,
                'avg_market_share': avg_market_share,
                'category_market_share': category_market_share.to_dict() if category_market_share is not None else None,
                'category_share_percentage': category_share_percentage.to_dict() if category_share_percentage is not None else None,
                'region_market_share': region_market_share.to_dict() if region_market_share is not None else None,
                'region_share_percentage': region_share_percentage.to_dict() if region_share_percentage is not None else None
            }
        except Exception as e:
            self.logger.error(f"市场份额分析失败: {e}")
            return {}
    
    def _analyze_competition_intensity(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析竞争强度"""
        try:
            # 计算竞争强度指标
            intensity_metrics = {}
            
            # 产品数量（竞争密度）
            if 'product_id' in data.columns:
                intensity_metrics['product_count'] = data['product_id'].nunique()
            
            # 价格竞争强度
            if 'base_price' in data.columns:
                price_std = data['base_price'].std()
                price_mean = data['base_price'].mean()
                intensity_metrics['price_competition_intensity'] = (price_std / price_mean) * 100 if price_mean > 0 else 0
            
            # 市场份额集中度
            if 'market_share' in data.columns:
                market_shares = data['market_share'] / 100
                hhi = (market_shares ** 2).sum()
                intensity_metrics['market_concentration'] = hhi
            
            return intensity_metrics
        except Exception as e:
            self.logger.error(f"竞争强度分析失败: {e}")
            return {}
    
    def _analyze_competitive_advantages(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析竞争优势"""
        try:
            advantages = {}
            
            # 质量优势
            if 'quality_score' in data.columns:
                avg_quality = data['quality_score'].mean()
                advantages['quality_advantage'] = {
                    'avg_quality_score': avg_quality,
                    'quality_ranking': 'high' if avg_quality > 4 else 'medium' if avg_quality > 3 else 'low'
                }
            
            # 价格优势
            if 'base_price' in data.columns:
                avg_price = data['base_price'].mean()
                price_quartile = data['base_price'].quantile(0.25)
                advantages['price_advantage'] = {
                    'avg_price': avg_price,
                    'price_positioning': 'premium' if avg_price > price_quartile * 1.5 else 'competitive' if avg_price > price_quartile else 'budget'
                }
            
            # 客户满意度优势
            if 'customer_satisfaction' in data.columns:
                avg_satisfaction = data['customer_satisfaction'].mean()
                advantages['satisfaction_advantage'] = {
                    'avg_satisfaction': avg_satisfaction,
                    'satisfaction_level': 'excellent' if avg_satisfaction > 4.5 else 'good' if avg_satisfaction > 3.5 else 'needs_improvement'
                }
            
            return advantages
        except Exception as e:
            self.logger.error(f"竞争优势分析失败: {e}")
            return {}
    
    def _analyze_competitive_threats(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析竞争威胁"""
        try:
            threats = {}
            
            # 市场份额威胁
            if 'market_share' in data.columns:
                market_share_trend = data['market_share'].pct_change().mean()
                threats['market_share_threat'] = {
                    'trend': 'declining' if market_share_trend < -0.05 else 'stable' if abs(market_share_trend) < 0.05 else 'growing',
                    'trend_rate': market_share_trend
                }
            
            # 价格竞争威胁
            if 'base_price' in data.columns:
                price_trend = data['base_price'].pct_change().mean()
                threats['price_competition_threat'] = {
                    'price_trend': 'declining' if price_trend < -0.05 else 'stable' if abs(price_trend) < 0.05 else 'rising',
                    'trend_rate': price_trend
                }
            
            return threats
        except Exception as e:
            self.logger.error(f"竞争威胁分析失败: {e}")
            return {}
    
    def _analyze_customer_segments(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析客户细分"""
        try:
            if 'customer_id' not in data.columns:
                return {'error': '缺少客户ID数据'}
            
            # 按客户价值细分
            customer_analysis = data.groupby('customer_id').agg({
                'amount': ['count', 'sum', 'mean'],
                'customer_satisfaction': 'mean' if 'customer_satisfaction' in data.columns else 'count'
            }).round(2)
            
            # 客户价值等级
            customer_analysis['value_level'] = pd.cut(
                customer_analysis[('amount', 'sum')],
                bins=[0, customer_analysis[('amount', 'sum')].quantile(0.33), 
                      customer_analysis[('amount', 'sum')].quantile(0.67), float('inf')],
                labels=['低价值', '中价值', '高价值']
            )
            
            segment_analysis = customer_analysis.groupby('value_level').agg({
                ('amount', 'count'): 'count',
                ('amount', 'sum'): 'sum',
                ('customer_satisfaction', 'mean'): 'mean'
            }).round(2)
            
            return segment_analysis.to_dict()
        except Exception as e:
            self.logger.error(f"客户细分分析失败: {e}")
            return {}
    
    def _analyze_product_segments(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析产品细分"""
        try:
            if 'product_category' not in data.columns:
                return {'error': '缺少产品类别数据'}
            
            # 按产品类别细分
            product_analysis = data.groupby('product_category').agg({
                'amount': ['count', 'sum', 'mean'],
                'sales_volume': 'sum' if 'sales_volume' in data.columns else 'count',
                'market_share': 'mean' if 'market_share' in data.columns else 'count'
            }).round(2)
            
            return product_analysis.to_dict()
        except Exception as e:
            self.logger.error(f"产品细分分析失败: {e}")
            return {}
    
    def _analyze_geographic_segments(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析地理细分"""
        try:
            if 'province' not in data.columns:
                return {'error': '缺少省份数据'}
            
            # 按省份细分
            geographic_analysis = data.groupby('province').agg({
                'amount': ['count', 'sum', 'mean'],
                'sales_volume': 'sum' if 'sales_volume' in data.columns else 'count'
            }).round(2)
            
            return geographic_analysis.to_dict()
        except Exception as e:
            self.logger.error(f"地理细分分析失败: {e}")
            return {}
    
    def _analyze_behavioral_segments(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析行为细分"""
        try:
            if 'customer_id' not in data.columns:
                return {'error': '缺少客户ID数据'}
            
            # 按购买行为细分
            behavioral_analysis = data.groupby('customer_id').agg({
                'amount': ['count', 'sum', 'mean'],
                'transaction_date': ['min', 'max'] if 'transaction_date' in data.columns else 'count'
            }).round(2)
            
            # 计算客户生命周期
            if 'transaction_date' in data.columns:
                behavioral_analysis['customer_lifetime'] = (
                    pd.to_datetime(behavioral_analysis[('transaction_date', 'max')]) - 
                    pd.to_datetime(behavioral_analysis[('transaction_date', 'min')])
                ).dt.days
            
            return behavioral_analysis.to_dict()
        except Exception as e:
            self.logger.error(f"行为细分分析失败: {e}")
            return {}
    
    def _calculate_price_elasticity(self, price_data: pd.Series) -> float:
        """计算价格弹性"""
        try:
            if len(price_data) < 2:
                return 0
            
            # 计算价格和销量的相关性
            prices = price_data.index.values
            quantities = price_data.values
            
            # 计算价格弹性
            price_changes = np.diff(prices) / prices[:-1]
            quantity_changes = np.diff(quantities) / quantities[:-1]
            
            if len(price_changes) == 0 or np.std(price_changes) == 0:
                return 0
            
            elasticity = np.mean(quantity_changes / price_changes)
            return elasticity
        except Exception as e:
            self.logger.error(f"价格弹性计算失败: {e}")
            return 0
    
    def _find_optimal_price_range(self, price_data: pd.Series) -> Dict[str, float]:
        """找到最优价格区间"""
        try:
            if len(price_data) < 3:
                return {'min': 0, 'max': 0, 'optimal': 0}
            
            # 找到销量最高的价格区间
            max_quantity_idx = price_data.idxmax()
            max_quantity = price_data.max()
            
            # 计算价格区间
            prices = price_data.index.values
            quantities = price_data.values
            
            # 找到销量在最高销量80%以上的价格区间
            threshold = max_quantity * 0.8
            optimal_prices = prices[quantities >= threshold]
            
            return {
                'min': optimal_prices.min() if len(optimal_prices) > 0 else prices.min(),
                'max': optimal_prices.max() if len(optimal_prices) > 0 else prices.max(),
                'optimal': max_quantity_idx
            }
        except Exception as e:
            self.logger.error(f"最优价格区间计算失败: {e}")
            return {'min': 0, 'max': 0, 'optimal': 0}
    
    def _generate_trend_insights(self, time_trends: Dict, category_trends: Dict) -> List[str]:
        """生成趋势洞察"""
        insights = []
        
        # 分析时间趋势
        if 'monthly_growth_rate' in time_trends:
            recent_growth = list(time_trends['monthly_growth_rate'].values())[-3:]  # 最近3个月
            avg_growth = np.mean(recent_growth)
            
            if avg_growth > 0.1:
                insights.append("市场呈现强劲增长趋势")
            elif avg_growth > 0.05:
                insights.append("市场保持稳定增长")
            elif avg_growth < -0.05:
                insights.append("市场出现下滑趋势，需要关注")
        
        # 分析类别趋势
        if 'category_analysis' in category_trends:
            insights.append("不同产品类别的表现存在差异，需要针对性策略")
        
        return insights
    
    def _generate_competition_insights(self, market_share: Dict, competition_intensity: Dict) -> List[str]:
        """生成竞争洞察"""
        insights = []
        
        # 市场份额分析
        if 'avg_market_share' in market_share:
            avg_share = market_share['avg_market_share']
            if avg_share > 20:
                insights.append("市场份额较高，处于市场领先地位")
            elif avg_share > 10:
                insights.append("市场份额适中，有提升空间")
            else:
                insights.append("市场份额较低，需要加强市场拓展")
        
        # 竞争强度分析
        if 'price_competition_intensity' in competition_intensity:
            intensity = competition_intensity['price_competition_intensity']
            if intensity > 30:
                insights.append("价格竞争激烈，需要差异化策略")
            elif intensity < 10:
                insights.append("价格竞争相对温和")
        
        return insights
    
    def _generate_segmentation_insights(self, customer_segments: Dict, product_segments: Dict) -> List[str]:
        """生成细分洞察"""
        insights = []
        
        # 客户细分洞察
        if '高价值' in str(customer_segments):
            insights.append("存在高价值客户群体，需要重点维护")
        
        # 产品细分洞察
        if product_segments:
            insights.append("产品组合多样化，覆盖不同细分市场")
        
        return insights
    
    def _generate_demand_insights(self, feature_importance: Dict, r2_score: float) -> List[str]:
        """生成需求预测洞察"""
        insights = []
        
        # 模型性能
        if r2_score > 0.8:
            insights.append("市场需求预测模型准确性很高")
        elif r2_score > 0.6:
            insights.append("市场需求预测模型准确性良好")
        
        # 特征重要性
        if feature_importance:
            most_important = max(feature_importance.keys(), key=lambda k: feature_importance[k])
            insights.append(f"影响市场需求的最重要因素是{most_important}")
        
        return insights
