"""
淘宝/天猫API对接
"""
import requests
import hashlib
import hmac
import time
import json
from typing import List, Dict, Optional
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

class TaobaoAPI:
    """淘宝开放平台API客户端"""
    
    def __init__(self, app_key: str, app_secret: str, access_token: str = None):
        self.app_key = app_key
        self.app_secret = app_secret
        self.access_token = access_token
        self.base_url = "https://eco.taobao.com/router/rest"
        
    def _generate_sign(self, params: Dict) -> str:
        """生成签名"""
        # 按参数名排序
        sorted_params = sorted(params.items())
        query_string = "&".join([f"{k}{v}" for k, v in sorted_params])
        sign_string = f"{self.app_secret}{query_string}{self.app_secret}"
        return hmac.new(
            self.app_secret.encode('utf-8'),
            sign_string.encode('utf-8'),
            hashlib.md5
        ).hexdigest().upper()
    
    def _make_request(self, method: str, params: Dict) -> Dict:
        """发送API请求"""
        # 基础参数
        base_params = {
            'method': method,
            'app_key': self.app_key,
            'timestamp': str(int(time.time() * 1000)),
            'format': 'json',
            'v': '2.0',
            'sign_method': 'md5'
        }
        
        if self.access_token:
            base_params['session'] = self.access_token
        
        # 合并参数
        all_params = {**base_params, **params}
        
        # 生成签名
        all_params['sign'] = self._generate_sign(all_params)
        
        try:
            response = requests.post(self.base_url, data=all_params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"淘宝API请求失败: {e}")
            raise
    
    def fetch_orders(
        self, 
        start_date: date, 
        end_date: date,
        page_size: int = 100
    ) -> List[Dict]:
        """
        拉取订单数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            page_size: 每页数量
        
        Returns:
            订单数据列表
        """
        try:
            orders = []
            page_no = 1
            
            while True:
                params = {
                    'fields': 'tid,status,payment,orders,created,pay_time,receiver_name,receiver_state,receiver_city',
                    'start_created': start_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'end_created': end_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'page_no': page_no,
                    'page_size': page_size
                }
                
                response = self._make_request('taobao.trades.sold.get', params)
                
                if 'trades_sold_get_response' not in response:
                    logger.error(f"淘宝API响应格式错误: {response}")
                    break
                
                trades = response['trades_sold_get_response'].get('trades', {}).get('trade', [])
                if not trades:
                    break
                
                # 处理订单数据
                for trade in trades:
                    order_data = self._process_order(trade)
                    if order_data:
                        orders.append(order_data)
                
                # 检查是否还有更多数据
                total_results = response['trades_sold_get_response'].get('total_results', 0)
                if page_no * page_size >= total_results:
                    break
                
                page_no += 1
                
                # 避免请求过于频繁
                time.sleep(0.1)
            
            logger.info(f"成功拉取淘宝订单数据，数量: {len(orders)}")
            return orders
            
        except Exception as e:
            logger.error(f"拉取淘宝订单数据失败: {e}")
            raise
    
    def _process_order(self, trade: Dict) -> Optional[Dict]:
        """处理单个订单数据"""
        try:
            # 提取订单基本信息
            order_id = trade.get('tid', '')
            status = trade.get('status', '')
            payment = float(trade.get('payment', 0))
            created = trade.get('created', '')
            pay_time = trade.get('pay_time', '')
            
            # 提取收货地址信息
            receiver = trade.get('receiver_name', '')
            receiver_state = trade.get('receiver_state', '')
            receiver_city = trade.get('receiver_city', '')
            
            # 提取商品信息
            orders = trade.get('orders', {}).get('order', [])
            if not orders:
                return None
            
            # 处理第一个商品（简化处理）
            first_order = orders[0]
            sku_id = first_order.get('outer_iid', '')
            sku_name = first_order.get('title', '')
            qty = int(first_order.get('num', 1))
            
            return {
                'order_id': order_id,
                'customer_id': f"taobao_{receiver}_{receiver_city}",  # 简化客户ID
                'sku_id': sku_id,
                'sku_name': sku_name,
                'conv_id': 'tmall',  # 转化渠道
                'date_key': datetime.strptime(created, '%Y-%m-%d %H:%M:%S').date(),
                'order_type': 'normal',
                'qty': qty,
                'amt': payment,
                'vpt_snap': ['vpt001', 'vpt002'],  # 默认价值主张
                'pft_snap': ['pft001'],  # 默认产品特性
                'platform': 'taobao',
                'status': status,
                'receiver_name': receiver,
                'receiver_state': receiver_state,
                'receiver_city': receiver_city,
                'pay_time': pay_time
            }
            
        except Exception as e:
            logger.error(f"处理订单数据失败: {e}")
            return None
    
    def fetch_reviews(self, sku_id: str, page_size: int = 100) -> List[Dict]:
        """
        拉取商品评价数据
        
        Args:
            sku_id: 商品ID
            page_size: 每页数量
        
        Returns:
            评价数据列表
        """
        try:
            reviews = []
            page_no = 1
            
            while True:
                params = {
                    'num_iid': sku_id,
                    'page_no': page_no,
                    'page_size': page_size,
                    'fields': 'rate_id,content,result,created,anony,rated_nick'
                }
                
                response = self._make_request('taobao.traderates.get', params)
                
                if 'traderates_get_response' not in response:
                    logger.error(f"淘宝评价API响应格式错误: {response}")
                    break
                
                rates = response['traderates_get_response'].get('traderates', {}).get('traderate', [])
                if not rates:
                    break
                
                # 处理评价数据
                for rate in rates:
                    review_data = self._process_review(rate, sku_id)
                    if review_data:
                        reviews.append(review_data)
                
                # 检查是否还有更多数据
                total_results = response['traderates_get_response'].get('total_results', 0)
                if page_no * page_size >= total_results:
                    break
                
                page_no += 1
                time.sleep(0.1)
            
            logger.info(f"成功拉取商品评价数据，SKU: {sku_id}, 数量: {len(reviews)}")
            return reviews
            
        except Exception as e:
            logger.error(f"拉取商品评价数据失败: {e}")
            raise
    
    def _process_review(self, rate: Dict, sku_id: str) -> Optional[Dict]:
        """处理单个评价数据"""
        try:
            voice_id = rate.get('rate_id', '')
            content = rate.get('content', '')
            result = rate.get('result', '')
            created = rate.get('created', '')
            anony = rate.get('anony', False)
            rated_nick = rate.get('rated_nick', '')
            
            # 情感分析（简化处理）
            sentiment = self._analyze_sentiment(content)
            cvrs_score = self._calculate_cvrs_score(result, sentiment)
            
            return {
                'voice_id': voice_id,
                'platform': 'taobao',
                'customer_id': f"taobao_{rated_nick}" if not anony else f"taobao_anonymous_{voice_id}",
                'vpt_id': 'vpt001',  # 默认价值主张
                'pft_id': 'pft001',  # 默认产品特性
                'sentiment': sentiment,
                'mention': content,
                'cvrs_score': cvrs_score,
                'lifecycle_stage': 'advocacy',  # 评价属于推荐阶段
                'stage_transition_from': 'purchase',
                'stage_duration_days': 0,
                'awareness_level': 5.0,  # 已购买说明认知充分
                'acceptance_level': 5.0,  # 已购买说明已接纳
                'experience_quality': cvrs_score,
                'publish_time': datetime.strptime(created, '%Y-%m-%d %H:%M:%S'),
                'sku_id': sku_id,
                'result': result,
                'anony': anony
            }
            
        except Exception as e:
            logger.error(f"处理评价数据失败: {e}")
            return None
    
    def _analyze_sentiment(self, content: str) -> str:
        """简单情感分析"""
        positive_words = ['好', '满意', '赞', '优秀', '棒', '喜欢', '推荐', '不错', '很好']
        negative_words = ['差', '烂', '垃圾', '退货', '投诉', '失望', '后悔', '不好', '很差']
        
        content_lower = content.lower()
        pos_count = sum(1 for word in positive_words if word in content_lower)
        neg_count = sum(1 for word in negative_words if word in content_lower)
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _calculate_cvrs_score(self, result: str, sentiment: str) -> float:
        """计算综合评分"""
        # 基于评价结果和情感
        result_scores = {
            'good': 5.0,
            'neutral': 3.0,
            'bad': 1.0
        }
        
        sentiment_scores = {
            'positive': 1.0,
            'neutral': 0.0,
            'negative': -1.0
        }
        
        base_score = result_scores.get(result, 3.0)
        sentiment_bonus = sentiment_scores.get(sentiment, 0.0)
        
        return max(1.0, min(5.0, base_score + sentiment_bonus))


