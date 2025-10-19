"""
抖音API对接
"""
import requests
import json
import time
from typing import List, Dict, Optional
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

class DouyinAPI:
    """抖音开放平台API客户端"""
    
    def __init__(self, client_key: str, client_secret: str, access_token: str = None):
        self.client_key = client_key
        self.client_secret = client_secret
        self.access_token = access_token
        self.base_url = "https://open.douyin.com"
        
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'BMOS-System/1.0'
        }
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        return headers
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Dict:
        """发送API请求"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=30)
            else:
                response = requests.post(url, json=data, headers=headers, timeout=30)
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"抖音API请求失败: {e}")
            raise
    
    def fetch_ad_data(
        self, 
        start_date: date, 
        end_date: date,
        advertiser_id: str
    ) -> List[Dict]:
        """
        拉取广告投放数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            advertiser_id: 广告主ID
        
        Returns:
            广告数据列表
        """
        try:
            params = {
                'advertiser_id': advertiser_id,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'page': 1,
                'page_size': 100
            }
            
            response = self._make_request('GET', '/open_api/v1.3/advertiser/ad/get/', params)
            
            if 'data' not in response:
                logger.error(f"抖音广告API响应格式错误: {response}")
                return []
            
            ad_list = response['data'].get('list', [])
            ad_data = []
            
            for ad in ad_list:
                processed_ad = self._process_ad_data(ad)
                if processed_ad:
                    ad_data.append(processed_ad)
            
            logger.info(f"成功拉取抖音广告数据，数量: {len(ad_data)}")
            return ad_data
            
        except Exception as e:
            logger.error(f"拉取抖音广告数据失败: {e}")
            raise
    
    def _process_ad_data(self, ad: Dict) -> Optional[Dict]:
        """处理单个广告数据"""
        try:
            ad_id = ad.get('ad_id', '')
            ad_name = ad.get('ad_name', '')
            campaign_id = ad.get('campaign_id', '')
            campaign_name = ad.get('campaign_name', '')
            
            # 广告投放数据
            cost = float(ad.get('cost', 0))  # 消耗金额
            show_cnt = int(ad.get('show_cnt', 0))  # 展示次数
            click_cnt = int(ad.get('click_cnt', 0))  # 点击次数
            convert_cnt = int(ad.get('convert_cnt', 0))  # 转化次数
            
            # 计算指标
            ctr = click_cnt / show_cnt if show_cnt > 0 else 0  # 点击率
            cvr = convert_cnt / click_cnt if click_cnt > 0 else 0  # 转化率
            cpc = cost / click_cnt if click_cnt > 0 else 0  # 点击成本
            cpa = cost / convert_cnt if convert_cnt > 0 else 0  # 转化成本
            
            # 日期信息
            stat_date = ad.get('stat_date', '')
            if stat_date:
                date_key = datetime.strptime(stat_date, '%Y-%m-%d').date()
            else:
                date_key = date.today()
            
            return {
                'cost_id': f"douyin_{ad_id}_{stat_date}",
                'date_key': date_key,
                'activity_id': f"douyin_campaign_{campaign_id}",
                'amount': cost,
                'cost_center': 'douyin_advertising',
                'vendor_id': 'douyin',
                'ad_id': ad_id,
                'ad_name': ad_name,
                'campaign_id': campaign_id,
                'campaign_name': campaign_name,
                'show_cnt': show_cnt,
                'click_cnt': click_cnt,
                'convert_cnt': convert_cnt,
                'ctr': ctr,
                'cvr': cvr,
                'cpc': cpc,
                'cpa': cpa,
                'platform': 'douyin'
            }
            
        except Exception as e:
            logger.error(f"处理广告数据失败: {e}")
            return None
    
    def fetch_creative_data(
        self, 
        start_date: date, 
        end_date: date,
        advertiser_id: str
    ) -> List[Dict]:
        """
        拉取创意数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            advertiser_id: 广告主ID
        
        Returns:
            创意数据列表
        """
        try:
            params = {
                'advertiser_id': advertiser_id,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'page': 1,
                'page_size': 100
            }
            
            response = self._make_request('GET', '/open_api/v1.3/creative/get/', params)
            
            if 'data' not in response:
                logger.error(f"抖音创意API响应格式错误: {response}")
                return []
            
            creative_list = response['data'].get('list', [])
            creative_data = []
            
            for creative in creative_list:
                processed_creative = self._process_creative_data(creative)
                if processed_creative:
                    creative_data.append(processed_creative)
            
            logger.info(f"成功拉取抖音创意数据，数量: {len(creative_data)}")
            return creative_data
            
        except Exception as e:
            logger.error(f"拉取抖音创意数据失败: {e}")
            raise
    
    def _process_creative_data(self, creative: Dict) -> Optional[Dict]:
        """处理单个创意数据"""
        try:
            creative_id = creative.get('creative_id', '')
            creative_name = creative.get('creative_name', '')
            ad_id = creative.get('ad_id', '')
            
            # 创意表现数据
            cost = float(creative.get('cost', 0))
            show_cnt = int(creative.get('show_cnt', 0))
            click_cnt = int(creative.get('click_cnt', 0))
            convert_cnt = int(creative.get('convert_cnt', 0))
            
            # 创意内容
            title = creative.get('title', '')
            description = creative.get('description', '')
            image_url = creative.get('image_url', '')
            video_url = creative.get('video_url', '')
            
            # 日期信息
            stat_date = creative.get('stat_date', '')
            if stat_date:
                date_key = datetime.strptime(stat_date, '%Y-%m-%d').date()
            else:
                date_key = date.today()
            
            return {
                'creative_id': creative_id,
                'creative_name': creative_name,
                'ad_id': ad_id,
                'date_key': date_key,
                'cost': cost,
                'show_cnt': show_cnt,
                'click_cnt': click_cnt,
                'convert_cnt': convert_cnt,
                'title': title,
                'description': description,
                'image_url': image_url,
                'video_url': video_url,
                'platform': 'douyin'
            }
            
        except Exception as e:
            logger.error(f"处理创意数据失败: {e}")
            return None
    
    def fetch_audience_insights(
        self, 
        advertiser_id: str,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        拉取受众洞察数据
        
        Args:
            advertiser_id: 广告主ID
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            受众洞察数据
        """
        try:
            params = {
                'advertiser_id': advertiser_id,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }
            
            response = self._make_request('GET', '/open_api/v1.3/audience/insights/', params)
            
            if 'data' not in response:
                logger.error(f"抖音受众洞察API响应格式错误: {response}")
                return {}
            
            insights_data = response['data']
            
            # 处理受众洞察数据
            processed_insights = {
                'advertiser_id': advertiser_id,
                'start_date': start_date,
                'end_date': end_date,
                'age_distribution': insights_data.get('age_distribution', {}),
                'gender_distribution': insights_data.get('gender_distribution', {}),
                'city_distribution': insights_data.get('city_distribution', {}),
                'interest_tags': insights_data.get('interest_tags', []),
                'device_distribution': insights_data.get('device_distribution', {}),
                'platform': 'douyin'
            }
            
            logger.info(f"成功拉取抖音受众洞察数据，广告主: {advertiser_id}")
            return processed_insights
            
        except Exception as e:
            logger.error(f"拉取抖音受众洞察数据失败: {e}")
            raise


