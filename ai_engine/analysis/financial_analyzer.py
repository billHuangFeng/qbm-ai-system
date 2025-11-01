"""
财务分析器
提供财务数据分析、现金流分析、盈利能力分析等功能
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class FinancialAnalyzer:
    """财务分析器类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_financial_performance(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        财务绩效分析
        
        Args:
            data: 财务数据
            
        Returns:
            财务绩效分析结果
        """
        try:
            # 基础财务指标
            performance_metrics = {
                'total_transactions': len(data),
                'total_revenue': data[data['amount'] > 0]['amount'].sum(),
                'total_expenses': abs(data[data['amount'] < 0]['amount'].sum()),
                'net_income': data['amount'].sum(),
                'avg_transaction_amount': data['amount'].mean(),
                'largest_transaction': data['amount'].max(),
                'smallest_transaction': data['amount'].min()
            }
            
            # 按类型分析
            type_analysis = data.groupby('financial_type').agg({
                'amount': ['count', 'sum', 'mean'],
                'transaction_date': ['min', 'max']
            }).round(2)
            
            # 按类别分析
            category_analysis = data.groupby('category').agg({
                'amount': ['count', 'sum', 'mean']
            }).round(2)
            
            # 时间趋势分析
            time_analysis = self._analyze_time_trends(data)
            
            # 现金流分析
            cash_flow_analysis = self._analyze_cash_flow(data)
            
            result = {
                'performance_metrics': performance_metrics,
                'type_analysis': type_analysis.to_dict(),
                'category_analysis': category_analysis.to_dict(),
                'time_analysis': time_analysis,
                'cash_flow_analysis': cash_flow_analysis,
                'insights': self._generate_performance_insights(performance_metrics, type_analysis)
            }
            
            self.logger.info("财务绩效分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"财务绩效分析失败: {e}")
            raise
    
    def analyze_profitability(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        盈利能力分析
        
        Args:
            data: 财务数据
            
        Returns:
            盈利能力分析结果
        """
        try:
            # 收入分析
            revenue_data = data[data['amount'] > 0]
            revenue_analysis = {
                'total_revenue': revenue_data['amount'].sum(),
                'avg_revenue_per_transaction': revenue_data['amount'].mean(),
                'revenue_growth_rate': self._calculate_growth_rate(revenue_data),
                'revenue_by_category': revenue_data.groupby('category')['amount'].sum().to_dict(),
                'revenue_by_type': revenue_data.groupby('financial_type')['amount'].sum().to_dict()
            }
            
            # 支出分析
            expense_data = data[data['amount'] < 0]
            expense_analysis = {
                'total_expenses': abs(expense_data['amount'].sum()),
                'avg_expense_per_transaction': abs(expense_data['amount'].mean()),
                'expense_growth_rate': self._calculate_growth_rate(expense_data),
                'expense_by_category': abs(expense_data.groupby('category')['amount'].sum()).to_dict(),
                'expense_by_type': abs(expense_data.groupby('financial_type')['amount'].sum()).to_dict()
            }
            
            # 利润率分析
            profit_margin = (revenue_analysis['total_revenue'] - expense_analysis['total_expenses']) / revenue_analysis['total_revenue'] * 100 if revenue_analysis['total_revenue'] > 0 else 0
            
            # 成本结构分析
            cost_structure = self._analyze_cost_structure(expense_data)
            
            result = {
                'revenue_analysis': revenue_analysis,
                'expense_analysis': expense_analysis,
                'profit_margin': profit_margin,
                'cost_structure': cost_structure,
                'insights': self._generate_profitability_insights(revenue_analysis, expense_analysis, profit_margin)
            }
            
            self.logger.info("盈利能力分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"盈利能力分析失败: {e}")
            raise
    
    def analyze_cash_flow(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        现金流分析
        
        Args:
            data: 财务数据
            
        Returns:
            现金流分析结果
        """
        try:
            # 按现金流类型分析
            cash_flow_analysis = data.groupby('cash_flow_type').agg({
                'cash_flow_impact': ['count', 'sum', 'mean']
            }).round(2)
            
            # 现金流趋势分析
            if 'transaction_date' in data.columns:
                data['year_month'] = pd.to_datetime(data['transaction_date']).dt.to_period('M')
                monthly_cash_flow = data.groupby('year_month')['cash_flow_impact'].sum()
                
                # 计算现金流波动性
                cash_flow_volatility = monthly_cash_flow.std()
                cash_flow_trend = self._calculate_trend(monthly_cash_flow.values)
            else:
                monthly_cash_flow = None
                cash_flow_volatility = 0
                cash_flow_trend = 0
            
            # 现金流预测
            cash_flow_forecast = self._forecast_cash_flow(data)
            
            result = {
                'cash_flow_by_type': cash_flow_analysis.to_dict(),
                'monthly_cash_flow': monthly_cash_flow.to_dict() if monthly_cash_flow is not None else None,
                'volatility': cash_flow_volatility,
                'trend': cash_flow_trend,
                'forecast': cash_flow_forecast,
                'insights': self._generate_cash_flow_insights(cash_flow_analysis, cash_flow_volatility, cash_flow_trend)
            }
            
            self.logger.info("现金流分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"现金流分析失败: {e}")
            raise
    
    def analyze_financial_health(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        财务健康度分析
        
        Args:
            data: 财务数据
            
        Returns:
            财务健康度分析结果
        """
        try:
            # 计算财务比率
            financial_ratios = self._calculate_financial_ratios(data)
            
            # 风险评估
            risk_assessment = self._assess_financial_risks(data)
            
            # 财务稳定性分析
            stability_analysis = self._analyze_financial_stability(data)
            
            # 综合健康度评分
            health_score = self._calculate_health_score(financial_ratios, risk_assessment, stability_analysis)
            
            result = {
                'financial_ratios': financial_ratios,
                'risk_assessment': risk_assessment,
                'stability_analysis': stability_analysis,
                'health_score': health_score,
                'insights': self._generate_health_insights(financial_ratios, risk_assessment, health_score)
            }
            
            self.logger.info("财务健康度分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"财务健康度分析失败: {e}")
            raise
    
    def _analyze_time_trends(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析时间趋势"""
        try:
            if 'transaction_date' not in data.columns:
                return {'error': '缺少交易日期数据'}
            
            # 按月分析
            data['year_month'] = pd.to_datetime(data['transaction_date']).dt.to_period('M')
            monthly_trends = data.groupby('year_month').agg({
                'amount': ['count', 'sum', 'mean']
            }).round(2)
            
            # 按季度分析
            data['quarter'] = pd.to_datetime(data['transaction_date']).dt.to_period('Q')
            quarterly_trends = data.groupby('quarter').agg({
                'amount': ['count', 'sum', 'mean']
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
    
    def _analyze_cash_flow(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析现金流"""
        try:
            if 'cash_flow_impact' not in data.columns:
                return {'error': '缺少现金流影响数据'}
            
            # 现金流类型分析
            cash_flow_by_type = data.groupby('cash_flow_type')['cash_flow_impact'].agg(['count', 'sum', 'mean']).round(2)
            
            # 现金流趋势
            if 'transaction_date' in data.columns:
                data['year_month'] = pd.to_datetime(data['transaction_date']).dt.to_period('M')
                monthly_cash_flow = data.groupby('year_month')['cash_flow_impact'].sum()
                cash_flow_trend = self._calculate_trend(monthly_cash_flow.values)
            else:
                cash_flow_trend = 0
            
            return {
                'by_type': cash_flow_by_type.to_dict(),
                'trend': cash_flow_trend,
                'total_impact': data['cash_flow_impact'].sum()
            }
        except Exception as e:
            self.logger.error(f"现金流分析失败: {e}")
            return {}
    
    def _calculate_growth_rate(self, data: pd.DataFrame) -> float:
        """计算增长率"""
        try:
            if 'transaction_date' not in data.columns or len(data) < 2:
                return 0
            
            # 按时间排序
            data_sorted = data.sort_values('transaction_date')
            
            # 计算第一个月和最后一个月的金额
            first_month = data_sorted.iloc[0]['amount']
            last_month = data_sorted.iloc[-1]['amount']
            
            if first_month == 0:
                return 0
            
            return ((last_month - first_month) / abs(first_month)) * 100
        except Exception as e:
            self.logger.error(f"增长率计算失败: {e}")
            return 0
    
    def _analyze_cost_structure(self, expense_data: pd.DataFrame) -> Dict[str, Any]:
        """分析成本结构"""
        try:
            if expense_data.empty:
                return {}
            
            # 按类别分析成本结构
            cost_by_category = abs(expense_data.groupby('category')['amount'].sum()).sort_values(ascending=False)
            cost_percentage = (cost_by_category / cost_by_category.sum() * 100).round(2)
            
            # 按类型分析成本结构
            cost_by_type = abs(expense_data.groupby('financial_type')['amount'].sum()).sort_values(ascending=False)
            type_percentage = (cost_by_type / cost_by_type.sum() * 100).round(2)
            
            return {
                'by_category': {
                    'amounts': cost_by_category.to_dict(),
                    'percentages': cost_percentage.to_dict()
                },
                'by_type': {
                    'amounts': cost_by_type.to_dict(),
                    'percentages': type_percentage.to_dict()
                }
            }
        except Exception as e:
            self.logger.error(f"成本结构分析失败: {e}")
            return {}
    
    def _forecast_cash_flow(self, data: pd.DataFrame) -> Dict[str, Any]:
        """预测现金流"""
        try:
            if 'transaction_date' not in data.columns or 'cash_flow_impact' not in data.columns:
                return {'error': '缺少必要的数据字段'}
            
            # 按月聚合现金流
            data['year_month'] = pd.to_datetime(data['transaction_date']).dt.to_period('M')
            monthly_cash_flow = data.groupby('year_month')['cash_flow_impact'].sum()
            
            if len(monthly_cash_flow) < 3:
                return {'error': '数据不足，无法进行预测'}
            
            # 简单线性趋势预测
            x = np.arange(len(monthly_cash_flow))
            y = monthly_cash_flow.values
            
            # 计算线性回归
            coeffs = np.polyfit(x, y, 1)
            
            # 预测未来3个月
            future_months = len(monthly_cash_flow) + np.arange(1, 4)
            predictions = coeffs[0] * future_months + coeffs[1]
            
            return {
                'next_month': predictions[0],
                'month_2': predictions[1],
                'month_3': predictions[2],
                'trend_slope': coeffs[0]
            }
        except Exception as e:
            self.logger.error(f"现金流预测失败: {e}")
            return {}
    
    def _calculate_financial_ratios(self, data: pd.DataFrame) -> Dict[str, float]:
        """计算财务比率"""
        try:
            revenue = data[data['amount'] > 0]['amount'].sum()
            expenses = abs(data[data['amount'] < 0]['amount'].sum())
            
            ratios = {}
            
            # 利润率
            if revenue > 0:
                ratios['profit_margin'] = ((revenue - expenses) / revenue) * 100
            else:
                ratios['profit_margin'] = 0
            
            # 收入增长率
            ratios['revenue_growth_rate'] = self._calculate_growth_rate(data[data['amount'] > 0])
            
            # 成本控制率
            if revenue > 0:
                ratios['cost_control_ratio'] = (expenses / revenue) * 100
            else:
                ratios['cost_control_ratio'] = 0
            
            return ratios
        except Exception as e:
            self.logger.error(f"财务比率计算失败: {e}")
            return {}
    
    def _assess_financial_risks(self, data: pd.DataFrame) -> Dict[str, Any]:
        """评估财务风险"""
        try:
            risks = {}
            
            # 现金流风险
            if 'cash_flow_impact' in data.columns:
                negative_cash_flow_months = (data['cash_flow_impact'] < 0).sum()
                total_months = len(data)
                risks['cash_flow_risk'] = (negative_cash_flow_months / total_months) * 100 if total_months > 0 else 0
            
            # 收入集中度风险
            revenue_data = data[data['amount'] > 0]
            if not revenue_data.empty:
                # 计算收入的标准差
                revenue_std = revenue_data['amount'].std()
                revenue_mean = revenue_data['amount'].mean()
                risks['revenue_concentration_risk'] = (revenue_std / revenue_mean) * 100 if revenue_mean > 0 else 0
            
            # 成本波动风险
            expense_data = data[data['amount'] < 0]
            if not expense_data.empty:
                expense_std = abs(expense_data['amount']).std()
                expense_mean = abs(expense_data['amount']).mean()
                risks['cost_volatility_risk'] = (expense_std / expense_mean) * 100 if expense_mean > 0 else 0
            
            return risks
        except Exception as e:
            self.logger.error(f"财务风险评估失败: {e}")
            return {}
    
    def _analyze_financial_stability(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析财务稳定性"""
        try:
            stability = {}
            
            # 收入稳定性
            if 'transaction_date' in data.columns:
                data['year_month'] = pd.to_datetime(data['transaction_date']).dt.to_period('M')
                monthly_revenue = data[data['amount'] > 0].groupby('year_month')['amount'].sum()
                
                if len(monthly_revenue) > 1:
                    revenue_cv = monthly_revenue.std() / monthly_revenue.mean() * 100
                    stability['revenue_stability'] = max(0, 100 - revenue_cv)  # 变异系数越小，稳定性越高
                else:
                    stability['revenue_stability'] = 100
            
            # 成本稳定性
            if 'transaction_date' in data.columns:
                monthly_expenses = abs(data[data['amount'] < 0].groupby('year_month')['amount'].sum())
                
                if len(monthly_expenses) > 1:
                    expense_cv = monthly_expenses.std() / monthly_expenses.mean() * 100
                    stability['expense_stability'] = max(0, 100 - expense_cv)
                else:
                    stability['expense_stability'] = 100
            
            return stability
        except Exception as e:
            self.logger.error(f"财务稳定性分析失败: {e}")
            return {}
    
    def _calculate_health_score(self, ratios: Dict, risks: Dict, stability: Dict) -> float:
        """计算综合健康度评分"""
        try:
            score = 0
            factors = 0
            
            # 利润率评分 (0-30分)
            if 'profit_margin' in ratios:
                profit_margin = ratios['profit_margin']
                if profit_margin > 20:
                    score += 30
                elif profit_margin > 10:
                    score += 20
                elif profit_margin > 0:
                    score += 10
                factors += 1
            
            # 收入增长率评分 (0-20分)
            if 'revenue_growth_rate' in ratios:
                growth_rate = ratios['revenue_growth_rate']
                if growth_rate > 10:
                    score += 20
                elif growth_rate > 5:
                    score += 15
                elif growth_rate > 0:
                    score += 10
                factors += 1
            
            # 稳定性评分 (0-25分)
            if 'revenue_stability' in stability:
                score += stability['revenue_stability'] * 0.25
                factors += 1
            
            # 风险评分 (0-25分)
            if 'cash_flow_risk' in risks:
                risk_score = max(0, 25 - risks['cash_flow_risk'])
                score += risk_score
                factors += 1
            
            return score / factors if factors > 0 else 0
        except Exception as e:
            self.logger.error(f"健康度评分计算失败: {e}")
            return 0
    
    def _calculate_trend(self, values: np.ndarray) -> float:
        """计算趋势"""
        try:
            if len(values) < 2:
                return 0
            
            x = np.arange(len(values))
            coeffs = np.polyfit(x, values, 1)
            return coeffs[0]  # 斜率
        except Exception as e:
            self.logger.error(f"趋势计算失败: {e}")
            return 0
    
    def _generate_performance_insights(self, metrics: Dict, type_analysis: pd.DataFrame) -> List[str]:
        """生成绩效洞察"""
        insights = []
        
        if metrics['net_income'] > 0:
            insights.append("财务状况良好，实现盈利")
        else:
            insights.append("财务状况需要改善，出现亏损")
        
        if metrics['total_revenue'] > metrics['total_expenses'] * 1.2:
            insights.append("收入与支出比例健康，有良好的盈利空间")
        
        return insights
    
    def _generate_profitability_insights(self, revenue_analysis: Dict, expense_analysis: Dict, profit_margin: float) -> List[str]:
        """生成盈利能力洞察"""
        insights = []
        
        if profit_margin > 20:
            insights.append("利润率较高，盈利能力强劲")
        elif profit_margin > 10:
            insights.append("利润率适中，盈利能力良好")
        elif profit_margin > 0:
            insights.append("利润率较低，需要提升盈利能力")
        else:
            insights.append("出现亏损，需要紧急改善财务状况")
        
        if revenue_analysis['revenue_growth_rate'] > 10:
            insights.append("收入增长强劲，业务发展良好")
        elif revenue_analysis['revenue_growth_rate'] > 0:
            insights.append("收入保持增长，业务稳定发展")
        else:
            insights.append("收入出现下降，需要关注业务发展")
        
        return insights
    
    def _generate_cash_flow_insights(self, cash_flow_analysis: pd.DataFrame, volatility: float, trend: float) -> List[str]:
        """生成现金流洞察"""
        insights = []
        
        if trend > 0:
            insights.append("现金流呈上升趋势，财务状况改善")
        elif trend < 0:
            insights.append("现金流呈下降趋势，需要关注资金状况")
        else:
            insights.append("现金流保持稳定")
        
        if volatility < 20:
            insights.append("现金流波动较小，财务稳定性良好")
        elif volatility > 50:
            insights.append("现金流波动较大，存在财务风险")
        
        return insights
    
    def _generate_health_insights(self, ratios: Dict, risks: Dict, health_score: float) -> List[str]:
        """生成健康度洞察"""
        insights = []
        
        if health_score > 80:
            insights.append("财务健康度优秀，财务状况非常良好")
        elif health_score > 60:
            insights.append("财务健康度良好，财务状况稳定")
        elif health_score > 40:
            insights.append("财务健康度一般，需要关注财务状况")
        else:
            insights.append("财务健康度较差，需要紧急改善财务状况")
        
        if 'cash_flow_risk' in risks and risks['cash_flow_risk'] > 30:
            insights.append("现金流风险较高，需要加强资金管理")
        
        return insights





