"""
情感分析器
提供高级情感分析、情感趋势分析、情感分类等功能
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter, defaultdict
import logging
from .text_processor import TextProcessor

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """情感分析器类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.text_processor = TextProcessor()
        
        # 扩展情感词典
        self.emotion_lexicon = {
            'joy': {'高兴', '开心', '快乐', '兴奋', '满意', '愉快', '欣喜', '欢乐', '喜悦', '满足'},
            'anger': {'愤怒', '生气', '恼火', '愤怒', '气愤', '暴怒', '愤慨', '恼怒', '愤恨', '愤懑'},
            'fear': {'害怕', '恐惧', '担心', '忧虑', '焦虑', '紧张', '恐慌', '畏惧', '不安', '担忧'},
            'sadness': {'悲伤', '难过', '沮丧', '失望', '痛苦', '伤心', '忧郁', '哀伤', '沮丧', '绝望'},
            'surprise': {'惊讶', '惊奇', '意外', '震惊', '诧异', '吃惊', '惊异', '愕然', '震撼', '惊愕'},
            'disgust': {'厌恶', '恶心', '反感', '讨厌', '憎恶', '嫌弃', '厌烦', '憎恨', '厌恶', '反感'}
        }
        
        # 强度修饰词
        self.intensity_modifiers = {
            'very': 1.5, '很': 1.5, '非常': 1.5, '极其': 2.0, '特别': 1.3,
            'quite': 1.2, '相当': 1.2, '比较': 1.1, '稍微': 0.8, '有点': 0.8,
            'slightly': 0.8, 'somewhat': 0.9, 'rather': 1.1, 'pretty': 1.2
        }
        
        # 否定词
        self.negation_words = {'不', '没', '无', '非', '未', '别', '莫', '勿', '休', 'never', 'not', 'no', 'none'}
    
    def analyze_emotion(self, text: str) -> Dict[str, Any]:
        """
        情感分析
        
        Args:
            text: 输入文本
            
        Returns:
            情感分析结果
        """
        try:
            # 清洗文本
            cleaned_text = self.text_processor.clean_text(text)
            
            if not cleaned_text:
                return {'emotion': 'neutral', 'intensity': 0, 'confidence': 0}
            
            # 分词
            words = self.text_processor.extract_keywords(cleaned_text, top_k=50)
            word_list = [word for word, _ in words]
            
            # 计算各种情感分数
            emotion_scores = {}
            for emotion, emotion_words in self.emotion_lexicon.items():
                score = self._calculate_emotion_score(word_list, emotion_words)
                emotion_scores[emotion] = score
            
            # 确定主导情感
            dominant_emotion = max(emotion_scores.keys(), key=lambda k: emotion_scores[k])
            max_score = emotion_scores[dominant_emotion]
            
            # 计算整体情感强度
            total_intensity = sum(emotion_scores.values())
            
            # 计算置信度
            confidence = min(max_score / total_intensity if total_intensity > 0 else 0, 1.0)
            
            # 确定情感类别
            if max_score > 0.3:
                emotion_category = dominant_emotion
            elif total_intensity > 0.1:
                emotion_category = 'mixed'
            else:
                emotion_category = 'neutral'
            
            return {
                'emotion': emotion_category,
                'intensity': total_intensity,
                'confidence': confidence,
                'emotion_scores': emotion_scores,
                'dominant_emotion': dominant_emotion
            }
            
        except Exception as e:
            self.logger.error(f"情感分析失败: {e}")
            return {'emotion': 'neutral', 'intensity': 0, 'confidence': 0}
    
    def analyze_sentiment_trend(self, texts: List[str], time_labels: List[str] = None) -> Dict[str, Any]:
        """
        分析情感趋势
        
        Args:
            texts: 文本列表
            time_labels: 时间标签列表
            
        Returns:
            情感趋势分析结果
        """
        try:
            if not texts:
                return {'error': '没有提供文本数据'}
            
            # 分析每条文本的情感
            sentiment_results = []
            for text in texts:
                result = self.analyze_emotion(text)
                sentiment_results.append(result)
            
            # 计算整体趋势
            emotions = [result['emotion'] for result in sentiment_results]
            intensities = [result['intensity'] for result in sentiment_results]
            confidences = [result['confidence'] for result in sentiment_results]
            
            # 情感分布
            emotion_distribution = Counter(emotions)
            
            # 趋势分析
            trend_analysis = self._analyze_sentiment_trend_pattern(intensities, confidences)
            
            # 时间序列分析
            time_series = None
            if time_labels and len(time_labels) == len(texts):
                time_series = self._create_sentiment_time_series(texts, time_labels)
            
            result = {
                'total_texts': len(texts),
                'emotion_distribution': dict(emotion_distribution),
                'avg_intensity': np.mean(intensities),
                'avg_confidence': np.mean(confidences),
                'trend_analysis': trend_analysis,
                'time_series': time_series,
                'insights': self._generate_sentiment_insights(emotion_distribution, trend_analysis)
            }
            
            self.logger.info(f"情感趋势分析完成，处理了 {len(texts)} 条文本")
            return result
            
        except Exception as e:
            self.logger.error(f"情感趋势分析失败: {e}")
            return {'error': str(e)}
    
    def classify_sentiment_polarity(self, text: str) -> Dict[str, Any]:
        """
        情感极性分类
        
        Args:
            text: 输入文本
            
        Returns:
            情感极性分类结果
        """
        try:
            # 基础情感分析
            emotion_result = self.analyze_emotion(text)
            
            # 情感极性映射
            polarity_mapping = {
                'joy': 'positive',
                'surprise': 'positive',
                'anger': 'negative',
                'fear': 'negative',
                'sadness': 'negative',
                'disgust': 'negative',
                'neutral': 'neutral',
                'mixed': 'neutral'
            }
            
            polarity = polarity_mapping.get(emotion_result['emotion'], 'neutral')
            
            # 计算极性强度
            if polarity == 'positive':
                intensity = emotion_result['emotion_scores'].get('joy', 0) + emotion_result['emotion_scores'].get('surprise', 0)
            elif polarity == 'negative':
                intensity = sum([
                    emotion_result['emotion_scores'].get('anger', 0),
                    emotion_result['emotion_scores'].get('fear', 0),
                    emotion_result['emotion_scores'].get('sadness', 0),
                    emotion_result['emotion_scores'].get('disgust', 0)
                ])
            else:
                intensity = 0
            
            return {
                'polarity': polarity,
                'intensity': intensity,
                'confidence': emotion_result['confidence'],
                'emotion_details': emotion_result
            }
            
        except Exception as e:
            self.logger.error(f"情感极性分类失败: {e}")
            return {'polarity': 'neutral', 'intensity': 0, 'confidence': 0}
    
    def analyze_customer_sentiment(self, customer_feedback: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析客户情感
        
        Args:
            customer_feedback: 客户反馈数据
            
        Returns:
            客户情感分析结果
        """
        try:
            if not customer_feedback:
                return {'error': '没有提供客户反馈数据'}
            
            # 提取文本内容
            texts = []
            customer_ids = []
            timestamps = []
            
            for feedback in customer_feedback:
                if 'content' in feedback:
                    texts.append(feedback['content'])
                    customer_ids.append(feedback.get('customer_id', ''))
                    timestamps.append(feedback.get('timestamp', ''))
            
            # 分析每条反馈的情感
            sentiment_analysis = []
            for i, text in enumerate(texts):
                result = self.classify_sentiment_polarity(text)
                result.update({
                    'customer_id': customer_ids[i],
                    'timestamp': timestamps[i],
                    'text': text
                })
                sentiment_analysis.append(result)
            
            # 计算客户情感统计
            customer_sentiment_stats = self._calculate_customer_sentiment_stats(sentiment_analysis)
            
            # 情感趋势分析
            sentiment_trend = self._analyze_customer_sentiment_trend(sentiment_analysis)
            
            # 问题识别
            issues_identified = self._identify_customer_issues(sentiment_analysis)
            
            result = {
                'total_feedback': len(customer_feedback),
                'sentiment_analysis': sentiment_analysis,
                'customer_sentiment_stats': customer_sentiment_stats,
                'sentiment_trend': sentiment_trend,
                'issues_identified': issues_identified,
                'insights': self._generate_customer_sentiment_insights(customer_sentiment_stats, sentiment_trend)
            }
            
            self.logger.info(f"客户情感分析完成，处理了 {len(customer_feedback)} 条反馈")
            return result
            
        except Exception as e:
            self.logger.error(f"客户情感分析失败: {e}")
            return {'error': str(e)}
    
    def _calculate_emotion_score(self, words: List[str], emotion_words: set) -> float:
        """计算情感分数"""
        try:
            score = 0.0
            
            for i, word in enumerate(words):
                if word in emotion_words:
                    # 基础分数
                    base_score = 1.0
                    
                    # 检查强度修饰词
                    if i > 0 and words[i-1] in self.intensity_modifiers:
                        modifier = self.intensity_modifiers[words[i-1]]
                        base_score *= modifier
                    
                    # 检查否定词
                    negation_factor = 1.0
                    for j in range(max(0, i-3), i):
                        if words[j] in self.negation_words:
                            negation_factor = -0.5  # 否定词降低情感强度
                            break
                    
                    score += base_score * negation_factor
            
            return score
            
        except Exception as e:
            self.logger.error(f"情感分数计算失败: {e}")
            return 0.0
    
    def _analyze_sentiment_trend_pattern(self, intensities: List[float], confidences: List[float]) -> Dict[str, Any]:
        """分析情感趋势模式"""
        try:
            if len(intensities) < 2:
                return {'trend': 'stable', 'volatility': 0}
            
            # 计算趋势
            intensity_trend = np.polyfit(range(len(intensities)), intensities, 1)[0]
            confidence_trend = np.polyfit(range(len(confidences)), confidences, 1)[0]
            
            # 计算波动性
            intensity_volatility = np.std(intensities)
            confidence_volatility = np.std(confidences)
            
            # 确定趋势方向
            if intensity_trend > 0.1:
                trend_direction = 'improving'
            elif intensity_trend < -0.1:
                trend_direction = 'declining'
            else:
                trend_direction = 'stable'
            
            return {
                'trend': trend_direction,
                'intensity_trend': intensity_trend,
                'confidence_trend': confidence_trend,
                'intensity_volatility': intensity_volatility,
                'confidence_volatility': confidence_volatility
            }
        except Exception as e:
            self.logger.error(f"情感趋势模式分析失败: {e}")
            return {'trend': 'stable', 'volatility': 0}
    
    def _create_sentiment_time_series(self, texts: List[str], time_labels: List[str]) -> Dict[str, Any]:
        """创建情感时间序列"""
        try:
            # 按时间分组
            time_groups = defaultdict(list)
            for i, time_label in enumerate(time_labels):
                time_groups[time_label].append(texts[i])
            
            # 计算每个时间点的情感
            time_series_data = {}
            for time_label, group_texts in time_groups.items():
                group_sentiments = [self.classify_sentiment_polarity(text) for text in group_texts]
                
                # 计算平均值
                avg_intensity = np.mean([s['intensity'] for s in group_sentiments])
                avg_confidence = np.mean([s['confidence'] for s in group_sentiments])
                
                # 计算极性分布
                polarities = [s['polarity'] for s in group_sentiments]
                polarity_dist = Counter(polarities)
                
                time_series_data[time_label] = {
                    'avg_intensity': avg_intensity,
                    'avg_confidence': avg_confidence,
                    'polarity_distribution': dict(polarity_dist),
                    'text_count': len(group_texts)
                }
            
            return time_series_data
        except Exception as e:
            self.logger.error(f"情感时间序列创建失败: {e}")
            return {}
    
    def _calculate_customer_sentiment_stats(self, sentiment_analysis: List[Dict]) -> Dict[str, Any]:
        """计算客户情感统计"""
        try:
            polarities = [s['polarity'] for s in sentiment_analysis]
            intensities = [s['intensity'] for s in sentiment_analysis]
            confidences = [s['confidence'] for s in sentiment_analysis]
            
            # 极性分布
            polarity_distribution = Counter(polarities)
            
            # 统计指标
            stats = {
                'total_feedback': len(sentiment_analysis),
                'polarity_distribution': dict(polarity_distribution),
                'avg_intensity': np.mean(intensities),
                'avg_confidence': np.mean(confidences),
                'positive_ratio': polarity_distribution.get('positive', 0) / len(sentiment_analysis),
                'negative_ratio': polarity_distribution.get('negative', 0) / len(sentiment_analysis),
                'neutral_ratio': polarity_distribution.get('neutral', 0) / len(sentiment_analysis)
            }
            
            return stats
        except Exception as e:
            self.logger.error(f"客户情感统计计算失败: {e}")
            return {}
    
    def _analyze_customer_sentiment_trend(self, sentiment_analysis: List[Dict]) -> Dict[str, Any]:
        """分析客户情感趋势"""
        try:
            # 按时间排序
            sorted_analysis = sorted(sentiment_analysis, key=lambda x: x.get('timestamp', ''))
            
            if len(sorted_analysis) < 2:
                return {'trend': 'insufficient_data'}
            
            # 计算时间趋势
            intensities = [s['intensity'] for s in sorted_analysis]
            trend_slope = np.polyfit(range(len(intensities)), intensities, 1)[0]
            
            # 计算最近趋势
            recent_count = min(10, len(intensities))
            recent_intensities = intensities[-recent_count:]
            recent_trend = np.polyfit(range(len(recent_intensities)), recent_intensities, 1)[0]
            
            return {
                'overall_trend': 'improving' if trend_slope > 0.1 else 'declining' if trend_slope < -0.1 else 'stable',
                'recent_trend': 'improving' if recent_trend > 0.1 else 'declining' if recent_trend < -0.1 else 'stable',
                'trend_slope': trend_slope,
                'recent_trend_slope': recent_trend
            }
        except Exception as e:
            self.logger.error(f"客户情感趋势分析失败: {e}")
            return {'trend': 'error'}
    
    def _identify_customer_issues(self, sentiment_analysis: List[Dict]) -> List[Dict[str, Any]]:
        """识别客户问题"""
        try:
            issues = []
            
            # 识别负面情感反馈
            negative_feedback = [s for s in sentiment_analysis if s['polarity'] == 'negative' and s['intensity'] > 0.5]
            
            for feedback in negative_feedback:
                # 提取关键词
                keywords = self.text_processor.extract_keywords(feedback['text'], top_k=5)
                
                issue = {
                    'customer_id': feedback.get('customer_id', ''),
                    'timestamp': feedback.get('timestamp', ''),
                    'text': feedback['text'],
                    'intensity': feedback['intensity'],
                    'confidence': feedback['confidence'],
                    'keywords': [word for word, _ in keywords],
                    'issue_type': self._classify_issue_type(feedback['text'])
                }
                issues.append(issue)
            
            return issues
        except Exception as e:
            self.logger.error(f"客户问题识别失败: {e}")
            return []
    
    def _classify_issue_type(self, text: str) -> str:
        """分类问题类型"""
        try:
            # 问题类型关键词
            issue_types = {
                'quality': ['质量', '品质', '问题', '故障', '错误', 'bug', '缺陷'],
                'service': ['服务', '客服', '态度', '响应', '支持', '帮助'],
                'price': ['价格', '费用', '成本', '贵', '便宜', '性价比'],
                'delivery': ['交付', '发货', '物流', '运输', '时间', '延迟'],
                'product': ['产品', '功能', '性能', '使用', '操作', '界面']
            }
            
            text_lower = text.lower()
            
            for issue_type, keywords in issue_types.items():
                if any(keyword in text_lower for keyword in keywords):
                    return issue_type
            
            return 'other'
        except Exception as e:
            self.logger.error(f"问题类型分类失败: {e}")
            return 'unknown'
    
    def _generate_sentiment_insights(self, emotion_distribution: Counter, trend_analysis: Dict) -> List[str]:
        """生成情感洞察"""
        insights = []
        
        # 情感分布洞察
        total = sum(emotion_distribution.values())
        if total > 0:
            positive_ratio = emotion_distribution.get('positive', 0) / total
            negative_ratio = emotion_distribution.get('negative', 0) / total
            
            if positive_ratio > 0.6:
                insights.append("整体情感倾向积极，客户满意度较高")
            elif negative_ratio > 0.4:
                insights.append("负面情感比例较高，需要关注客户问题")
            else:
                insights.append("情感分布相对均衡")
        
        # 趋势洞察
        if 'trend' in trend_analysis:
            trend = trend_analysis['trend']
            if trend == 'improving':
                insights.append("情感趋势向好，客户满意度在提升")
            elif trend == 'declining':
                insights.append("情感趋势下降，需要采取措施改善客户体验")
            else:
                insights.append("情感趋势保持稳定")
        
        return insights
    
    def _generate_customer_sentiment_insights(self, stats: Dict, trend: Dict) -> List[str]:
        """生成客户情感洞察"""
        insights = []
        
        # 满意度洞察
        if stats.get('positive_ratio', 0) > 0.6:
            insights.append("客户满意度较高，整体反馈积极")
        elif stats.get('negative_ratio', 0) > 0.3:
            insights.append("客户负面反馈较多，需要重点关注")
        
        # 趋势洞察
        if 'overall_trend' in trend:
            if trend['overall_trend'] == 'improving':
                insights.append("客户满意度呈上升趋势")
            elif trend['overall_trend'] == 'declining':
                insights.append("客户满意度呈下降趋势，需要紧急关注")
        
        return insights




