"""
文本处理器
提供文本清洗、特征提取、关键词提取等功能
"""
import re
import jieba
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class TextProcessor:
    """文本处理器类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # 初始化jieba分词
        jieba.initialize()
        
        # 停用词列表
        self.stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'
        }
        
        # 情感词典
        self.positive_words = {
            '好', '很好', '非常好', '优秀', '满意', '喜欢', '推荐', '赞', '棒', '完美', '出色', '卓越', '优质', '高效', '便捷', '方便', '快速', '稳定', '可靠'
        }
        
        self.negative_words = {
            '差', '很差', '不好', '不满意', '讨厌', '糟糕', '垃圾', '烂', '慢', '卡', '不稳定', '不可靠', '麻烦', '复杂', '困难', '问题', '错误', '失败'
        }
    
    def clean_text(self, text: str) -> str:
        """
        清洗文本
        
        Args:
            text: 原始文本
            
        Returns:
            清洗后的文本
        """
        try:
            if not isinstance(text, str):
                return ""
            
            # 移除HTML标签
            text = re.sub(r'<[^>]+>', '', text)
            
            # 移除特殊字符，保留中文、英文、数字和基本标点
            text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s.,!?;:()（）]', '', text)
            
            # 移除多余空格
            text = re.sub(r'\s+', ' ', text)
            
            # 移除首尾空格
            text = text.strip()
            
            return text
            
        except Exception as e:
            self.logger.error(f"文本清洗失败: {e}")
            return ""
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        提取关键词
        
        Args:
            text: 输入文本
            top_k: 返回前k个关键词
            
        Returns:
            关键词列表，包含词和权重
        """
        try:
            # 清洗文本
            cleaned_text = self.clean_text(text)
            
            if not cleaned_text:
                return []
            
            # 分词
            words = jieba.lcut(cleaned_text)
            
            # 过滤停用词和短词
            filtered_words = [
                word for word in words 
                if len(word) > 1 and word not in self.stop_words
            ]
            
            # 计算词频
            word_freq = Counter(filtered_words)
            
            # 计算TF-IDF权重（简化版）
            total_words = len(filtered_words)
            keywords = []
            
            for word, freq in word_freq.most_common(top_k):
                # 简化的TF-IDF计算
                tf = freq / total_words
                # 这里可以加入IDF计算，暂时使用TF
                weight = tf
                keywords.append((word, weight))
            
            return keywords
            
        except Exception as e:
            self.logger.error(f"关键词提取失败: {e}")
            return []
    
    def extract_features(self, text: str) -> Dict[str, Any]:
        """
        提取文本特征
        
        Args:
            text: 输入文本
            
        Returns:
            文本特征字典
        """
        try:
            cleaned_text = self.clean_text(text)
            
            if not cleaned_text:
                return {}
            
            # 分词
            words = jieba.lcut(cleaned_text)
            
            # 基础特征
            features = {
                'text_length': len(cleaned_text),
                'word_count': len(words),
                'unique_word_count': len(set(words)),
                'avg_word_length': np.mean([len(word) for word in words]) if words else 0,
                'sentence_count': len(re.split(r'[.!?。！？]', cleaned_text)),
                'has_question': '?' in cleaned_text or '？' in cleaned_text,
                'has_exclamation': '!' in cleaned_text or '！' in cleaned_text,
                'has_numbers': bool(re.search(r'\d', cleaned_text)),
                'has_english': bool(re.search(r'[a-zA-Z]', cleaned_text))
            }
            
            # 情感特征
            sentiment_features = self._extract_sentiment_features(words)
            features.update(sentiment_features)
            
            # 主题特征
            topic_features = self._extract_topic_features(words)
            features.update(topic_features)
            
            return features
            
        except Exception as e:
            self.logger.error(f"文本特征提取失败: {e}")
            return {}
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        情感分析
        
        Args:
            text: 输入文本
            
        Returns:
            情感分析结果
        """
        try:
            cleaned_text = self.clean_text(text)
            
            if not cleaned_text:
                return {'sentiment': 'neutral', 'score': 0, 'confidence': 0}
            
            # 分词
            words = jieba.lcut(cleaned_text)
            
            # 计算情感分数
            positive_count = sum(1 for word in words if word in self.positive_words)
            negative_count = sum(1 for word in words if word in self.negative_words)
            
            total_sentiment_words = positive_count + negative_count
            
            if total_sentiment_words == 0:
                return {'sentiment': 'neutral', 'score': 0, 'confidence': 0}
            
            # 计算情感分数 (-1 到 1)
            sentiment_score = (positive_count - negative_count) / total_sentiment_words
            
            # 确定情感类别
            if sentiment_score > 0.2:
                sentiment = 'positive'
            elif sentiment_score < -0.2:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            # 计算置信度
            confidence = min(total_sentiment_words / len(words), 1.0) if words else 0
            
            return {
                'sentiment': sentiment,
                'score': sentiment_score,
                'confidence': confidence,
                'positive_count': positive_count,
                'negative_count': negative_count
            }
            
        except Exception as e:
            self.logger.error(f"情感分析失败: {e}")
            return {'sentiment': 'neutral', 'score': 0, 'confidence': 0}
    
    def extract_business_entities(self, text: str) -> Dict[str, List[str]]:
        """
        提取商业实体
        
        Args:
            text: 输入文本
            
        Returns:
            商业实体字典
        """
        try:
            cleaned_text = self.clean_text(text)
            
            if not cleaned_text:
                return {}
            
            entities = {
                'products': [],
                'companies': [],
                'people': [],
                'locations': [],
                'numbers': [],
                'dates': []
            }
            
            # 提取产品名称（简单规则）
            product_patterns = [
                r'产品[：:]\s*([^\s，,。！!？?]+)',
                r'服务[：:]\s*([^\s，,。！!？?]+)',
                r'([^\s，,。！!？?]+)(?:软件|系统|平台|工具|应用)'
            ]
            
            for pattern in product_patterns:
                matches = re.findall(pattern, cleaned_text)
                entities['products'].extend(matches)
            
            # 提取公司名称
            company_patterns = [
                r'([^\s，,。！!？?]+)(?:公司|企业|集团|有限公司|股份有限公司)',
                r'([^\s，,。！!？?]+)(?:科技|技术|信息|数据|网络)'
            ]
            
            for pattern in company_patterns:
                matches = re.findall(pattern, cleaned_text)
                entities['companies'].extend(matches)
            
            # 提取人名
            name_patterns = [
                r'([^\s，,。！!？?]{2,4})(?:先生|女士|经理|总监|主任|总)',
                r'(?:联系人|负责人)[：:]\s*([^\s，,。！!？?]+)'
            ]
            
            for pattern in name_patterns:
                matches = re.findall(pattern, cleaned_text)
                entities['people'].extend(matches)
            
            # 提取地点
            location_patterns = [
                r'([^\s，,。！!？?]+)(?:市|省|区|县|街道|路|号)',
                r'(?:地址|位置)[：:]\s*([^\s，,。！!？?]+)'
            ]
            
            for pattern in location_patterns:
                matches = re.findall(pattern, cleaned_text)
                entities['locations'].extend(matches)
            
            # 提取数字
            number_matches = re.findall(r'\d+(?:\.\d+)?', cleaned_text)
            entities['numbers'] = number_matches
            
            # 提取日期
            date_patterns = [
                r'\d{4}年\d{1,2}月\d{1,2}日',
                r'\d{4}-\d{1,2}-\d{1,2}',
                r'\d{1,2}月\d{1,2}日'
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, cleaned_text)
                entities['dates'].extend(matches)
            
            # 去重
            for key in entities:
                entities[key] = list(set(entities[key]))
            
            return entities
            
        except Exception as e:
            self.logger.error(f"商业实体提取失败: {e}")
            return {}
    
    def process_batch_texts(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        批量处理文本
        
        Args:
            texts: 文本列表
            
        Returns:
            处理结果列表
        """
        try:
            results = []
            
            for text in texts:
                result = {
                    'original_text': text,
                    'cleaned_text': self.clean_text(text),
                    'keywords': self.extract_keywords(text),
                    'features': self.extract_features(text),
                    'sentiment': self.analyze_sentiment(text),
                    'entities': self.extract_business_entities(text)
                }
                results.append(result)
            
            self.logger.info(f"批量处理了 {len(texts)} 条文本")
            return results
            
        except Exception as e:
            self.logger.error(f"批量文本处理失败: {e}")
            return []
    
    def _extract_sentiment_features(self, words: List[str]) -> Dict[str, Any]:
        """提取情感特征"""
        try:
            positive_count = sum(1 for word in words if word in self.positive_words)
            negative_count = sum(1 for word in words if word in self.negative_words)
            total_words = len(words)
            
            return {
                'positive_word_ratio': positive_count / total_words if total_words > 0 else 0,
                'negative_word_ratio': negative_count / total_words if total_words > 0 else 0,
                'sentiment_word_ratio': (positive_count + negative_count) / total_words if total_words > 0 else 0
            }
        except Exception as e:
            self.logger.error(f"情感特征提取失败: {e}")
            return {}
    
    def _extract_topic_features(self, words: List[str]) -> Dict[str, Any]:
        """提取主题特征"""
        try:
            # 定义主题关键词
            topic_keywords = {
                'technology': ['技术', '科技', '软件', '系统', '平台', '数据', 'AI', '人工智能', '算法'],
                'business': ['业务', '商业', '市场', '销售', '客户', '服务', '产品', '管理'],
                'finance': ['财务', '资金', '投资', '成本', '收入', '利润', '预算', '费用'],
                'quality': ['质量', '品质', '标准', '规范', '认证', '测试', '检验', '评估']
            }
            
            topic_features = {}
            
            for topic, keywords in topic_keywords.items():
                count = sum(1 for word in words if word in keywords)
                topic_features[f'{topic}_word_count'] = count
                topic_features[f'{topic}_word_ratio'] = count / len(words) if words else 0
            
            return topic_features
        except Exception as e:
            self.logger.error(f"主题特征提取失败: {e}")
            return {}
    
    def create_text_summary(self, texts: List[str], max_length: int = 200) -> str:
        """
        创建文本摘要
        
        Args:
            texts: 文本列表
            max_length: 最大长度
            
        Returns:
            文本摘要
        """
        try:
            if not texts:
                return ""
            
            # 合并所有文本
            combined_text = ' '.join(texts)
            
            # 提取关键词
            keywords = self.extract_keywords(combined_text, top_k=20)
            
            # 创建摘要（简化版）
            if len(combined_text) <= max_length:
                return combined_text
            
            # 找到包含最多关键词的句子
            sentences = re.split(r'[.!?。！？]', combined_text)
            sentence_scores = []
            
            for sentence in sentences:
                if not sentence.strip():
                    continue
                
                score = 0
                for keyword, weight in keywords:
                    if keyword in sentence:
                        score += weight
                
                sentence_scores.append((sentence.strip(), score))
            
            # 按分数排序
            sentence_scores.sort(key=lambda x: x[1], reverse=True)
            
            # 选择前几个句子
            summary_sentences = []
            current_length = 0
            
            for sentence, score in sentence_scores:
                if current_length + len(sentence) <= max_length:
                    summary_sentences.append(sentence)
                    current_length += len(sentence)
                else:
                    break
            
            return '。'.join(summary_sentences) + '。'
            
        except Exception as e:
            self.logger.error(f"文本摘要创建失败: {e}")
            return ""
    
    def analyze_text_similarity(self, text1: str, text2: str) -> float:
        """
        分析文本相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            相似度分数 (0-1)
        """
        try:
            # 提取关键词
            keywords1 = set([word for word, _ in self.extract_keywords(text1)])
            keywords2 = set([word for word, _ in self.extract_keywords(text2)])
            
            if not keywords1 or not keywords2:
                return 0.0
            
            # 计算Jaccard相似度
            intersection = len(keywords1.intersection(keywords2))
            union = len(keywords1.union(keywords2))
            
            similarity = intersection / union if union > 0 else 0.0
            
            return similarity
            
        except Exception as e:
            self.logger.error(f"文本相似度分析失败: {e}")
            return 0.0
