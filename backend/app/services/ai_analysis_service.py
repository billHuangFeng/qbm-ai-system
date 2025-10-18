"""
AI分析服务
提供AI分析功能的业务逻辑层
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import sys
import os

# 添加AI引擎路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..', 'ai_engine'))

from ai_engine.analysis.customer_analyzer import CustomerAnalyzer
from ai_engine.analysis.product_analyzer import ProductAnalyzer
from ai_engine.analysis.financial_analyzer import FinancialAnalyzer
from ai_engine.analysis.market_analyzer import MarketAnalyzer
from ai_engine.nlp.text_processor import TextProcessor
from ai_engine.nlp.sentiment_analyzer import SentimentAnalyzer
from ai_engine.models.prediction_models import PredictionModels
from ai_engine.utils.data_processor import DataProcessor

logger = logging.getLogger(__name__)

class AIAnalysisService:
    """AI分析服务类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 初始化分析器
        self.customer_analyzer = CustomerAnalyzer()
        self.product_analyzer = ProductAnalyzer()
        self.financial_analyzer = FinancialAnalyzer()
        self.market_analyzer = MarketAnalyzer()
        self.text_processor = TextProcessor()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.prediction_models = PredictionModels()
        self.data_processor = DataProcessor()
    
    async def analyze_customers(self, customer_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析客户数据
        
        Args:
            customer_data: 客户数据列表
            
        Returns:
            客户分析结果
        """
        try:
            if not customer_data:
                return {'error': '没有提供客户数据'}
            
            # 转换为DataFrame
            df = pd.DataFrame(customer_data)
            
            # 数据清洗和预处理
            cleaned_df = self.data_processor.clean_customer_data(df)
            processed_df = self.data_processor.create_customer_features(cleaned_df)
            
            # 执行各种分析
            analysis_results = {}
            
            # 客户价值分析
            value_analysis = self.customer_analyzer.analyze_customer_value(processed_df)
            analysis_results['value_analysis'] = value_analysis
            
            # 客户细分
            segmentation = self.customer_analyzer.customer_segmentation(processed_df)
            analysis_results['segmentation'] = segmentation
            
            # 客户生命周期分析
            lifecycle_analysis = self.customer_analyzer.analyze_customer_lifecycle(processed_df)
            analysis_results['lifecycle_analysis'] = lifecycle_analysis
            
            # 客户价值预测
            value_prediction = self.customer_analyzer.predict_customer_value(processed_df)
            analysis_results['value_prediction'] = value_prediction
            
            # 生成综合洞察
            insights = self._generate_customer_insights(analysis_results)
            analysis_results['insights'] = insights
            
            self.logger.info("客户分析完成")
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"客户分析失败: {e}")
            return {'error': str(e)}
    
    async def analyze_products(self, product_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析产品数据
        
        Args:
            product_data: 产品数据列表
            
        Returns:
            产品分析结果
        """
        try:
            if not product_data:
                return {'error': '没有提供产品数据'}
            
            # 转换为DataFrame
            df = pd.DataFrame(product_data)
            
            # 数据清洗和预处理
            cleaned_df = self.data_processor.clean_product_data(df)
            processed_df = self.data_processor.create_product_features(cleaned_df)
            
            # 执行各种分析
            analysis_results = {}
            
            # 产品性能分析
            performance_analysis = self.product_analyzer.analyze_product_performance(processed_df)
            analysis_results['performance_analysis'] = performance_analysis
            
            # 产品组合分析
            portfolio_analysis = self.product_analyzer.analyze_product_portfolio(processed_df)
            analysis_results['portfolio_analysis'] = portfolio_analysis
            
            # 产品成功度预测
            success_prediction = self.product_analyzer.predict_product_success(processed_df)
            analysis_results['success_prediction'] = success_prediction
            
            # 产品生命周期分析
            lifecycle_analysis = self.product_analyzer.analyze_product_lifecycle(processed_df)
            analysis_results['lifecycle_analysis'] = lifecycle_analysis
            
            # 生成综合洞察
            insights = self._generate_product_insights(analysis_results)
            analysis_results['insights'] = insights
            
            self.logger.info("产品分析完成")
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"产品分析失败: {e}")
            return {'error': str(e)}
    
    async def analyze_financials(self, financial_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析财务数据
        
        Args:
            financial_data: 财务数据列表
            
        Returns:
            财务分析结果
        """
        try:
            if not financial_data:
                return {'error': '没有提供财务数据'}
            
            # 转换为DataFrame
            df = pd.DataFrame(financial_data)
            
            # 数据清洗和预处理
            cleaned_df = self.data_processor.clean_financial_data(df)
            processed_df = self.data_processor.create_financial_features(cleaned_df)
            
            # 执行各种分析
            analysis_results = {}
            
            # 财务绩效分析
            performance_analysis = self.financial_analyzer.analyze_financial_performance(processed_df)
            analysis_results['performance_analysis'] = performance_analysis
            
            # 盈利能力分析
            profitability_analysis = self.financial_analyzer.analyze_profitability(processed_df)
            analysis_results['profitability_analysis'] = profitability_analysis
            
            # 现金流分析
            cash_flow_analysis = self.financial_analyzer.analyze_cash_flow(processed_df)
            analysis_results['cash_flow_analysis'] = cash_flow_analysis
            
            # 财务健康度分析
            health_analysis = self.financial_analyzer.analyze_financial_health(processed_df)
            analysis_results['health_analysis'] = health_analysis
            
            # 生成综合洞察
            insights = self._generate_financial_insights(analysis_results)
            analysis_results['insights'] = insights
            
            self.logger.info("财务分析完成")
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"财务分析失败: {e}")
            return {'error': str(e)}
    
    async def analyze_market(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析市场数据
        
        Args:
            market_data: 市场数据列表
            
        Returns:
            市场分析结果
        """
        try:
            if not market_data:
                return {'error': '没有提供市场数据'}
            
            # 转换为DataFrame
            df = pd.DataFrame(market_data)
            
            # 执行各种分析
            analysis_results = {}
            
            # 市场趋势分析
            trend_analysis = self.market_analyzer.analyze_market_trends(df)
            analysis_results['trend_analysis'] = trend_analysis
            
            # 竞争分析
            competition_analysis = self.market_analyzer.analyze_competition(df)
            analysis_results['competition_analysis'] = competition_analysis
            
            # 市场细分分析
            segmentation_analysis = self.market_analyzer.analyze_market_segmentation(df)
            analysis_results['segmentation_analysis'] = segmentation_analysis
            
            # 市场需求预测
            demand_prediction = self.market_analyzer.predict_market_demand(df)
            analysis_results['demand_prediction'] = demand_prediction
            
            # 生成综合洞察
            insights = self._generate_market_insights(analysis_results)
            analysis_results['insights'] = insights
            
            self.logger.info("市场分析完成")
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"市场分析失败: {e}")
            return {'error': str(e)}
    
    async def analyze_text_sentiment(self, text_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析文本情感
        
        Args:
            text_data: 文本数据列表
            
        Returns:
            情感分析结果
        """
        try:
            if not text_data:
                return {'error': '没有提供文本数据'}
            
            # 提取文本内容
            texts = []
            metadata = []
            
            for item in text_data:
                if 'content' in item:
                    texts.append(item['content'])
                    metadata.append({
                        'customer_id': item.get('customer_id', ''),
                        'timestamp': item.get('timestamp', ''),
                        'source': item.get('source', '')
                    })
            
            # 执行情感分析
            analysis_results = {}
            
            # 批量文本处理
            processed_texts = self.text_processor.process_batch_texts(texts)
            analysis_results['text_processing'] = processed_texts
            
            # 情感趋势分析
            timestamps = [item.get('timestamp', '') for item in metadata]
            sentiment_trend = self.sentiment_analyzer.analyze_sentiment_trend(texts, timestamps)
            analysis_results['sentiment_trend'] = sentiment_trend
            
            # 客户情感分析
            customer_feedback = []
            for i, text in enumerate(texts):
                customer_feedback.append({
                    'content': text,
                    'customer_id': metadata[i].get('customer_id', ''),
                    'timestamp': metadata[i].get('timestamp', '')
                })
            
            customer_sentiment = self.sentiment_analyzer.analyze_customer_sentiment(customer_feedback)
            analysis_results['customer_sentiment'] = customer_sentiment
            
            # 生成综合洞察
            insights = self._generate_sentiment_insights(analysis_results)
            analysis_results['insights'] = insights
            
            self.logger.info("文本情感分析完成")
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"文本情感分析失败: {e}")
            return {'error': str(e)}
    
    async def predict_business_metrics(self, data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        预测业务指标
        
        Args:
            data: 包含各种业务数据的字典
            
        Returns:
            预测结果
        """
        try:
            prediction_results = {}
            
            # 销量预测
            if 'products' in data and data['products']:
                product_df = pd.DataFrame(data['products'])
                sales_prediction = self.prediction_models.predict_sales_volume(product_df)
                prediction_results['sales_prediction'] = sales_prediction
            
            # 客户流失预测
            if 'customers' in data and data['customers']:
                customer_df = pd.DataFrame(data['customers'])
                churn_prediction = self.prediction_models.predict_customer_churn(customer_df)
                prediction_results['churn_prediction'] = churn_prediction
            
            # 收入预测
            if 'financials' in data and data['financials']:
                financial_df = pd.DataFrame(data['financials'])
                revenue_prediction = self.prediction_models.predict_revenue(financial_df)
                prediction_results['revenue_prediction'] = revenue_prediction
            
            # 市场需求预测
            if 'market' in data and data['market']:
                market_df = pd.DataFrame(data['market'])
                demand_prediction = self.prediction_models.predict_market_demand(market_df)
                prediction_results['demand_prediction'] = demand_prediction
            
            # 生成综合洞察
            insights = self._generate_prediction_insights(prediction_results)
            prediction_results['insights'] = insights
            
            self.logger.info("业务指标预测完成")
            return prediction_results
            
        except Exception as e:
            self.logger.error(f"业务指标预测失败: {e}")
            return {'error': str(e)}
    
    async def generate_comprehensive_report(self, all_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        生成综合分析报告
        
        Args:
            all_data: 包含所有业务数据的字典
            
        Returns:
            综合分析报告
        """
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'data_summary': {},
                'analysis_results': {},
                'predictions': {},
                'insights': [],
                'recommendations': []
            }
            
            # 数据摘要
            for data_type, data_list in all_data.items():
                report['data_summary'][data_type] = {
                    'count': len(data_list),
                    'last_updated': datetime.now().isoformat()
                }
            
            # 执行各种分析
            if 'customers' in all_data and all_data['customers']:
                customer_analysis = await self.analyze_customers(all_data['customers'])
                report['analysis_results']['customers'] = customer_analysis
            
            if 'products' in all_data and all_data['products']:
                product_analysis = await self.analyze_products(all_data['products'])
                report['analysis_results']['products'] = product_analysis
            
            if 'financials' in all_data and all_data['financials']:
                financial_analysis = await self.analyze_financials(all_data['financials'])
                report['analysis_results']['financials'] = financial_analysis
            
            if 'market' in all_data and all_data['market']:
                market_analysis = await self.analyze_market(all_data['market'])
                report['analysis_results']['market'] = market_analysis
            
            # 执行预测
            predictions = await self.predict_business_metrics(all_data)
            report['predictions'] = predictions
            
            # 生成综合洞察和建议
            report['insights'] = self._generate_comprehensive_insights(report['analysis_results'])
            report['recommendations'] = self._generate_recommendations(report['analysis_results'], predictions)
            
            self.logger.info("综合分析报告生成完成")
            return report
            
        except Exception as e:
            self.logger.error(f"综合分析报告生成失败: {e}")
            return {'error': str(e)}
    
    def _generate_customer_insights(self, analysis_results: Dict[str, Any]) -> List[str]:
        """生成客户洞察"""
        insights = []
        
        # 从价值分析中提取洞察
        if 'value_analysis' in analysis_results:
            value_metrics = analysis_results['value_analysis'].get('value_metrics', {})
            if value_metrics.get('vip_percentage', 0) > 20:
                insights.append("VIP客户比例较高，客户质量良好")
            elif value_metrics.get('vip_percentage', 0) < 5:
                insights.append("VIP客户比例较低，需要提升客户价值")
        
        # 从细分分析中提取洞察
        if 'segmentation' in analysis_results:
            cluster_analysis = analysis_results['segmentation'].get('cluster_analysis', {})
            if cluster_analysis:
                insights.append(f"客户被分为{len(cluster_analysis)}个不同的群体，需要差异化策略")
        
        return insights
    
    def _generate_product_insights(self, analysis_results: Dict[str, Any]) -> List[str]:
        """生成产品洞察"""
        insights = []
        
        # 从性能分析中提取洞察
        if 'performance_analysis' in analysis_results:
            performance_metrics = analysis_results['performance_analysis'].get('performance_metrics', {})
            if performance_metrics.get('avg_profit_margin', 0) > 50:
                insights.append("产品平均利润率较高，盈利能力良好")
            elif performance_metrics.get('avg_profit_margin', 0) < 20:
                insights.append("产品平均利润率较低，需要优化成本结构")
        
        # 从组合分析中提取洞察
        if 'portfolio_analysis' in analysis_results:
            portfolio_matrix = analysis_results['portfolio_analysis'].get('portfolio_matrix', {})
            if 'distribution' in portfolio_matrix:
                distribution = portfolio_matrix['distribution']
                if '明星产品' in distribution and distribution['明星产品'] > 0:
                    insights.append("拥有明星产品，具有良好的增长潜力")
        
        return insights
    
    def _generate_financial_insights(self, analysis_results: Dict[str, Any]) -> List[str]:
        """生成财务洞察"""
        insights = []
        
        # 从盈利能力分析中提取洞察
        if 'profitability_analysis' in analysis_results:
            profit_margin = analysis_results['profitability_analysis'].get('profit_margin', 0)
            if profit_margin > 20:
                insights.append("利润率较高，财务状况良好")
            elif profit_margin < 0:
                insights.append("出现亏损，需要紧急改善财务状况")
        
        # 从健康度分析中提取洞察
        if 'health_analysis' in analysis_results:
            health_score = analysis_results['health_analysis'].get('health_score', 0)
            if health_score > 80:
                insights.append("财务健康度优秀，财务状况非常良好")
            elif health_score < 40:
                insights.append("财务健康度较差，需要紧急改善财务状况")
        
        return insights
    
    def _generate_market_insights(self, analysis_results: Dict[str, Any]) -> List[str]:
        """生成市场洞察"""
        insights = []
        
        # 从趋势分析中提取洞察
        if 'trend_analysis' in analysis_results:
            time_trends = analysis_results['trend_analysis'].get('time_trends', {})
            if 'monthly_growth_rate' in time_trends:
                recent_growth = list(time_trends['monthly_growth_rate'].values())[-3:]
                avg_growth = np.mean(recent_growth) if recent_growth else 0
                if avg_growth > 0.1:
                    insights.append("市场呈现强劲增长趋势")
                elif avg_growth < -0.05:
                    insights.append("市场出现下滑趋势，需要关注")
        
        # 从竞争分析中提取洞察
        if 'competition_analysis' in analysis_results:
            market_share = analysis_results['competition_analysis'].get('market_share_analysis', {})
            if 'avg_market_share' in market_share:
                avg_share = market_share['avg_market_share']
                if avg_share > 20:
                    insights.append("市场份额较高，处于市场领先地位")
                elif avg_share < 10:
                    insights.append("市场份额较低，需要加强市场拓展")
        
        return insights
    
    def _generate_sentiment_insights(self, analysis_results: Dict[str, Any]) -> List[str]:
        """生成情感洞察"""
        insights = []
        
        # 从客户情感分析中提取洞察
        if 'customer_sentiment' in analysis_results:
            sentiment_stats = analysis_results['customer_sentiment'].get('customer_sentiment_stats', {})
            if sentiment_stats.get('positive_ratio', 0) > 0.6:
                insights.append("客户满意度较高，整体反馈积极")
            elif sentiment_stats.get('negative_ratio', 0) > 0.3:
                insights.append("客户负面反馈较多，需要重点关注")
        
        return insights
    
    def _generate_prediction_insights(self, prediction_results: Dict[str, Any]) -> List[str]:
        """生成预测洞察"""
        insights = []
        
        # 从销量预测中提取洞察
        if 'sales_prediction' in prediction_results:
            model_performance = prediction_results['sales_prediction'].get('model_performance', {})
            r2_score = model_performance.get('r2_score', 0)
            if r2_score > 0.8:
                insights.append("销量预测模型准确性很高，预测结果可信")
        
        # 从客户流失预测中提取洞察
        if 'churn_prediction' in prediction_results:
            risk_levels = prediction_results['churn_prediction'].get('risk_levels', [])
            high_risk_count = risk_levels.count('high')
            if high_risk_count > len(risk_levels) * 0.2:
                insights.append("高流失风险客户比例较高，需要重点关注")
        
        return insights
    
    def _generate_comprehensive_insights(self, analysis_results: Dict[str, Any]) -> List[str]:
        """生成综合洞察"""
        insights = []
        
        # 汇总各类洞察
        for data_type, results in analysis_results.items():
            if 'insights' in results:
                insights.extend(results['insights'])
        
        return insights
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any], predictions: Dict[str, Any]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于分析结果生成建议
        if 'customers' in analysis_results:
            customer_insights = analysis_results['customers'].get('insights', [])
            if any('VIP客户比例较低' in insight for insight in customer_insights):
                recommendations.append("制定客户价值提升计划，增加VIP客户比例")
        
        if 'products' in analysis_results:
            product_insights = analysis_results['products'].get('insights', [])
            if any('利润率较低' in insight for insight in product_insights):
                recommendations.append("优化产品成本结构，提升利润率")
        
        if 'financials' in analysis_results:
            financial_insights = analysis_results['financials'].get('insights', [])
            if any('出现亏损' in insight for insight in financial_insights):
                recommendations.append("紧急制定财务改善计划，控制成本，增加收入")
        
        # 基于预测结果生成建议
        if 'churn_prediction' in predictions:
            risk_levels = predictions['churn_prediction'].get('risk_levels', [])
            high_risk_count = risk_levels.count('high')
            if high_risk_count > 0:
                recommendations.append("针对高流失风险客户制定挽留策略")
        
        return recommendations
