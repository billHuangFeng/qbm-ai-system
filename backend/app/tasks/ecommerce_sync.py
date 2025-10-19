"""
电商平台数据同步任务
"""
from celery import Celery
from app.integrations.ecommerce.taobao_api import TaobaoAPI
from app.integrations.ecommerce.douyin_api import DouyinAPI
from app.clickhouse import get_clickhouse_client
from datetime import datetime, date, timedelta
import logging
import os

logger = logging.getLogger(__name__)

# 创建Celery应用
app = Celery('bmos', broker='redis://localhost:6379/0')

@app.task
def sync_taobao_orders():
    """同步淘宝订单数据"""
    try:
        # 从环境变量获取API配置
        app_key = os.getenv('TAOBAO_APP_KEY')
        app_secret = os.getenv('TAOBAO_APP_SECRET')
        access_token = os.getenv('TAOBAO_ACCESS_TOKEN')
        
        if not all([app_key, app_secret]):
            logger.error("淘宝API配置不完整")
            return
        
        # 创建API客户端
        taobao_api = TaobaoAPI(app_key, app_secret, access_token)
        
        # 获取过去7天的订单数据
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        # 拉取订单数据
        orders = taobao_api.fetch_orders(start_date, end_date)
        
        if not orders:
            logger.info("没有新的淘宝订单数据")
            return
        
        # 写入ClickHouse
        client = get_clickhouse_client()
        
        for order in orders:
            try:
                query = f"""
                    INSERT INTO fact_order VALUES
                    ('{order['order_id']}', '{order['customer_id']}', '{order['sku_id']}', 
                     '{order['conv_id']}', '{order['date_key']}', '{order['order_type']}', 
                     {order['qty']}, {order['amt']}, {order['vpt_snap']}, {order['pft_snap']}, now())
                """
                client.execute(query)
            except Exception as e:
                logger.error(f"插入订单数据失败: {order['order_id']}, 错误: {e}")
        
        logger.info(f"淘宝订单数据同步完成，同步数量: {len(orders)}")
        
    except Exception as e:
        logger.error(f"淘宝订单数据同步失败: {e}")

@app.task
def sync_taobao_reviews():
    """同步淘宝评价数据"""
    try:
        # 从环境变量获取API配置
        app_key = os.getenv('TAOBAO_APP_KEY')
        app_secret = os.getenv('TAOBAO_APP_SECRET')
        access_token = os.getenv('TAOBAO_ACCESS_TOKEN')
        
        if not all([app_key, app_secret]):
            logger.error("淘宝API配置不完整")
            return
        
        # 创建API客户端
        taobao_api = TaobaoAPI(app_key, app_secret, access_token)
        
        # 获取需要同步评价的SKU列表
        client = get_clickhouse_client()
        sku_query = """
            SELECT DISTINCT sku_id 
            FROM fact_order 
            WHERE date_key >= today() - INTERVAL 30 DAY
            AND platform = 'taobao'
        """
        sku_results = client.execute(sku_query)
        sku_ids = [row[0] for row in sku_results]
        
        if not sku_ids:
            logger.info("没有需要同步评价的SKU")
            return
        
        # 拉取评价数据
        all_reviews = []
        for sku_id in sku_ids[:10]:  # 限制前10个SKU，避免请求过多
            try:
                reviews = taobao_api.fetch_reviews(sku_id)
                all_reviews.extend(reviews)
            except Exception as e:
                logger.error(f"拉取SKU {sku_id} 评价数据失败: {e}")
        
        if not all_reviews:
            logger.info("没有新的淘宝评价数据")
            return
        
        # 写入ClickHouse
        for review in all_reviews:
            try:
                query = f"""
                    INSERT INTO fact_voice VALUES
                    ('{review['voice_id']}', '{review['platform']}', '{review['customer_id']}', 
                     '{review['vpt_id']}', '{review['pft_id']}', '{review['sentiment']}', 
                     '{review['mention']}', {review['cvrs_score']}, '{review['lifecycle_stage']}', 
                     '{review['stage_transition_from']}', {review['stage_duration_days']}, 
                     {review['awareness_level']}, {review['acceptance_level']}, 
                     {review['experience_quality']}, '{review['publish_time']}', now())
                """
                client.execute(query)
            except Exception as e:
                logger.error(f"插入评价数据失败: {review['voice_id']}, 错误: {e}")
        
        logger.info(f"淘宝评价数据同步完成，同步数量: {len(all_reviews)}")
        
    except Exception as e:
        logger.error(f"淘宝评价数据同步失败: {e}")

@app.task
def sync_douyin_ads():
    """同步抖音广告数据"""
    try:
        # 从环境变量获取API配置
        client_key = os.getenv('DOUYIN_CLIENT_KEY')
        client_secret = os.getenv('DOUYIN_CLIENT_SECRET')
        access_token = os.getenv('DOUYIN_ACCESS_TOKEN')
        advertiser_id = os.getenv('DOUYIN_ADVERTISER_ID')
        
        if not all([client_key, client_secret, advertiser_id]):
            logger.error("抖音API配置不完整")
            return
        
        # 创建API客户端
        douyin_api = DouyinAPI(client_key, client_secret, access_token)
        
        # 获取过去7天的广告数据
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        # 拉取广告数据
        ad_data = douyin_api.fetch_ad_data(start_date, end_date, advertiser_id)
        
        if not ad_data:
            logger.info("没有新的抖音广告数据")
            return
        
        # 写入ClickHouse
        client = get_clickhouse_client()
        
        for ad in ad_data:
            try:
                query = f"""
                    INSERT INTO fact_cost VALUES
                    ('{ad['cost_id']}', '{ad['date_key']}', '{ad['activity_id']}', 
                     {ad['amount']}, '{ad['cost_center']}', '{ad['vendor_id']}', now())
                """
                client.execute(query)
            except Exception as e:
                logger.error(f"插入广告数据失败: {ad['cost_id']}, 错误: {e}")
        
        logger.info(f"抖音广告数据同步完成，同步数量: {len(ad_data)}")
        
    except Exception as e:
        logger.error(f"抖音广告数据同步失败: {e}")

@app.task
def sync_douyin_creatives():
    """同步抖音创意数据"""
    try:
        # 从环境变量获取API配置
        client_key = os.getenv('DOUYIN_CLIENT_KEY')
        client_secret = os.getenv('DOUYIN_CLIENT_SECRET')
        access_token = os.getenv('DOUYIN_ACCESS_TOKEN')
        advertiser_id = os.getenv('DOUYIN_ADVERTISER_ID')
        
        if not all([client_key, client_secret, advertiser_id]):
            logger.error("抖音API配置不完整")
            return
        
        # 创建API客户端
        douyin_api = DouyinAPI(client_key, client_secret, access_token)
        
        # 获取过去7天的创意数据
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        # 拉取创意数据
        creative_data = douyin_api.fetch_creative_data(start_date, end_date, advertiser_id)
        
        if not creative_data:
            logger.info("没有新的抖音创意数据")
            return
        
        # 写入ClickHouse（可以存储到专门的创意表或扩展fact_cost表）
        client = get_clickhouse_client()
        
        for creative in creative_data:
            try:
                # 这里可以将创意数据存储到专门的表中
                # 或者作为成本数据的补充信息
                logger.info(f"创意数据: {creative['creative_id']}, 成本: {creative['cost']}")
            except Exception as e:
                logger.error(f"处理创意数据失败: {creative['creative_id']}, 错误: {e}")
        
        logger.info(f"抖音创意数据同步完成，同步数量: {len(creative_data)}")
        
    except Exception as e:
        logger.error(f"抖音创意数据同步失败: {e}")

@app.task
def daily_ecommerce_sync():
    """每日电商数据同步任务"""
    try:
        logger.info("开始每日电商数据同步")
        
        # 同步淘宝订单数据
        sync_taobao_orders.delay()
        
        # 同步淘宝评价数据
        sync_taobao_reviews.delay()
        
        # 同步抖音广告数据
        sync_douyin_ads.delay()
        
        # 同步抖音创意数据
        sync_douyin_creatives.delay()
        
        logger.info("每日电商数据同步任务已提交")
        
    except Exception as e:
        logger.error(f"每日电商数据同步任务失败: {e}")

# Celery Beat 定时任务配置
app.conf.beat_schedule = {
    'daily-ecommerce-sync': {
        'task': 'app.tasks.ecommerce_sync.daily_ecommerce_sync',
        'schedule': crontab(hour=1, minute=0),  # 每日凌晨1点
    },
    'hourly-taobao-orders': {
        'task': 'app.tasks.ecommerce_sync.sync_taobao_orders',
        'schedule': crontab(minute=0),  # 每小时
    },
    'hourly-douyin-ads': {
        'task': 'app.tasks.ecommerce_sync.sync_douyin_ads',
        'schedule': crontab(minute=30),  # 每小时30分
    }
}


