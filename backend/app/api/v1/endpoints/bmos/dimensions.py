"""
BMOS系统维度表CRUD API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.schemas.bmos.dimensions import *
from app.clickhouse import get_clickhouse_client
from app.clickhouse import Client
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# 价值主张维度表API
@router.post("/vpt", response_model=VPTResponse)
async def create_vpt(vpt: VPTCreate):
    """创建价值主张"""
    try:
        client = get_clickhouse_client()
        
        query = f"""
            INSERT INTO dim_vpt VALUES
            ('{vpt.vpt_id}', '{vpt.vpt_name}', '{vpt.category or ''}', 
             '{vpt.definition or ''}', '{vpt.owner or ''}', now())
        """
        client.execute(query)
        
        logger.info(f"价值主张创建成功: {vpt.vpt_id}")
        return VPTResponse(
            vpt_id=vpt.vpt_id,
            vpt_name=vpt.vpt_name,
            category=vpt.category,
            definition=vpt.definition,
            owner=vpt.owner,
            create_time=datetime.now()
        )
    except Exception as e:
        logger.error(f"创建价值主张失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vpt", response_model=List[VPTResponse])
async def list_vpts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None)
):
    """获取价值主张列表"""
    try:
        client = get_clickhouse_client()
        
        where_clause = f"WHERE category = '{category}'" if category else ""
        query = f"""
            SELECT vpt_id, vpt_name, category, definition, owner, create_time
            FROM dim_vpt
            {where_clause}
            ORDER BY create_time DESC
            LIMIT {limit} OFFSET {skip}
        """
        
        results = client.execute(query)
        vpts = []
        for row in results:
            vpts.append(VPTResponse(
                vpt_id=row[0],
                vpt_name=row[1],
                category=row[2] if row[2] else None,
                definition=row[3] if row[3] else None,
                owner=row[4] if row[4] else None,
                create_time=row[5]
            ))
        
        return vpts
    except Exception as e:
        logger.error(f"获取价值主张列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vpt/{vpt_id}", response_model=VPTResponse)
async def get_vpt(vpt_id: str):
    """获取单个价值主张"""
    try:
        client = get_clickhouse_client()
        
        query = f"""
            SELECT vpt_id, vpt_name, category, definition, owner, create_time
            FROM dim_vpt
            WHERE vpt_id = '{vpt_id}'
        """
        
        results = client.execute(query)
        if not results:
            raise HTTPException(status_code=404, detail="价值主张不存在")
        
        row = results[0]
        return VPTResponse(
            vpt_id=row[0],
            vpt_name=row[1],
            category=row[2] if row[2] else None,
            definition=row[3] if row[3] else None,
            owner=row[4] if row[4] else None,
            create_time=row[5]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取价值主张失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/vpt/{vpt_id}", response_model=VPTResponse)
async def update_vpt(vpt_id: str, vpt_update: VPTUpdate):
    """更新价值主张"""
    try:
        client = get_clickhouse_client()
        
        # 构建更新字段
        update_fields = []
        if vpt_update.vpt_name is not None:
            update_fields.append(f"vpt_name = '{vpt_update.vpt_name}'")
        if vpt_update.category is not None:
            update_fields.append(f"category = '{vpt_update.category}'")
        if vpt_update.definition is not None:
            update_fields.append(f"definition = '{vpt_update.definition}'")
        if vpt_update.owner is not None:
            update_fields.append(f"owner = '{vpt_update.owner}'")
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="没有提供更新字段")
        
        # ClickHouse使用INSERT覆盖更新
        query = f"""
            INSERT INTO dim_vpt VALUES
            ('{vpt_id}', '{vpt_update.vpt_name or ''}', '{vpt_update.category or ''}', 
             '{vpt_update.definition or ''}', '{vpt_update.owner or ''}', now())
        """
        client.execute(query)
        
        logger.info(f"价值主张更新成功: {vpt_id}")
        return await get_vpt(vpt_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新价值主张失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/vpt/{vpt_id}")
async def delete_vpt(vpt_id: str):
    """删除价值主张"""
    try:
        client = get_clickhouse_client()
        
        # ClickHouse不支持DELETE，这里只是标记为删除
        # 实际应用中可能需要软删除或使用ReplacingMergeTree的版本控制
        query = f"""
            INSERT INTO dim_vpt VALUES
            ('{vpt_id}', '', '', '', '', now())
        """
        client.execute(query)
        
        logger.info(f"价值主张删除成功: {vpt_id}")
        return {"message": "价值主张删除成功"}
    except Exception as e:
        logger.error(f"删除价值主张失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 产品特性维度表API
@router.post("/pft", response_model=PFTResponse)
async def create_pft(pft: PFTCreate):
    """创建产品特性"""
    try:
        client = get_clickhouse_client()
        
        query = f"""
            INSERT INTO dim_pft VALUES
            ('{pft.pft_id}', '{pft.pft_name}', '{pft.unit or ''}', 
             '{pft.module or ''}', now())
        """
        client.execute(query)
        
        logger.info(f"产品特性创建成功: {pft.pft_id}")
        return PFTResponse(
            pft_id=pft.pft_id,
            pft_name=pft.pft_name,
            unit=pft.unit,
            module=pft.module,
            create_time=datetime.now()
        )
    except Exception as e:
        logger.error(f"创建产品特性失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pft", response_model=List[PFTResponse])
async def list_pfts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    module: Optional[str] = Query(None)
):
    """获取产品特性列表"""
    try:
        client = get_clickhouse_client()
        
        where_clause = f"WHERE module = '{module}'" if module else ""
        query = f"""
            SELECT pft_id, pft_name, unit, module, create_time
            FROM dim_pft
            {where_clause}
            ORDER BY create_time DESC
            LIMIT {limit} OFFSET {skip}
        """
        
        results = client.execute(query)
        pfts = []
        for row in results:
            pfts.append(PFTResponse(
                pft_id=row[0],
                pft_name=row[1],
                unit=row[2] if row[2] else None,
                module=row[3] if row[3] else None,
                create_time=row[5]
            ))
        
        return pfts
    except Exception as e:
        logger.error(f"获取产品特性列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pft/{pft_id}", response_model=PFTResponse)
async def get_pft(pft_id: str):
    """获取单个产品特性"""
    try:
        client = get_clickhouse_client()
        
        query = f"""
            SELECT pft_id, pft_name, unit, module, create_time
            FROM dim_pft
            WHERE pft_id = '{pft_id}'
        """
        
        results = client.execute(query)
        if not results:
            raise HTTPException(status_code=404, detail="产品特性不存在")
        
        row = results[0]
        return PFTResponse(
            pft_id=row[0],
            pft_name=row[1],
            unit=row[2] if row[2] else None,
            module=row[3] if row[3] else None,
            create_time=row[4]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取产品特性失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 活动维度表API
@router.post("/activity", response_model=ActivityResponse)
async def create_activity(activity: ActivityCreate):
    """创建活动"""
    try:
        client = get_clickhouse_client()
        
        vpt_list_str = "['" + "','".join(activity.vpt_list or []) + "']"
        pft_list_str = "['" + "','".join(activity.pft_list or []) + "']"
        
        query = f"""
            INSERT INTO dim_activity VALUES
            ('{activity.activity_id}', '{activity.activity_name}', '{activity.type or ''}', 
             {vpt_list_str}, {pft_list_str}, '{activity.start_date or ''}', 
             '{activity.end_date or ''}', '{activity.dept or ''}', now())
        """
        client.execute(query)
        
        logger.info(f"活动创建成功: {activity.activity_id}")
        return ActivityResponse(
            activity_id=activity.activity_id,
            activity_name=activity.activity_name,
            type=activity.type,
            vpt_list=activity.vpt_list,
            pft_list=activity.pft_list,
            start_date=activity.start_date,
            end_date=activity.end_date,
            dept=activity.dept,
            create_time=datetime.now()
        )
    except Exception as e:
        logger.error(f"创建活动失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activity", response_model=List[ActivityResponse])
async def list_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    dept: Optional[str] = Query(None)
):
    """获取活动列表"""
    try:
        client = get_clickhouse_client()
        
        where_clause = f"WHERE dept = '{dept}'" if dept else ""
        query = f"""
            SELECT activity_id, activity_name, type, vpt_list, pft_list, 
                   start_date, end_date, dept, create_time
            FROM dim_activity
            {where_clause}
            ORDER BY create_time DESC
            LIMIT {limit} OFFSET {skip}
        """
        
        results = client.execute(query)
        activities = []
        for row in results:
            activities.append(ActivityResponse(
                activity_id=row[0],
                activity_name=row[1],
                type=row[2] if row[2] else None,
                vpt_list=row[3] if row[3] else None,
                pft_list=row[4] if row[4] else None,
                start_date=row[5] if row[5] else None,
                end_date=row[6] if row[6] else None,
                dept=row[7] if row[7] else None,
                create_time=row[8]
            ))
        
        return activities
    except Exception as e:
        logger.error(f"获取活动列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 媒体渠道维度表API
@router.post("/media-channel", response_model=MediaChannelResponse)
async def create_media_channel(media: MediaChannelCreate):
    """创建媒体渠道"""
    try:
        client = get_clickhouse_client()
        
        vpt_list_str = "['" + "','".join(media.vpt_list or []) + "']"
        pft_list_str = "['" + "','".join(media.pft_list or []) + "']"
        
        query = f"""
            INSERT INTO dim_media_channel VALUES
            ('{media.media_id}', '{media.media_name}', '{media.type or ''}', 
             {vpt_list_str}, {pft_list_str}, '{media.start_date or ''}', 
             '{media.end_date or ''}', now())
        """
        client.execute(query)
        
        logger.info(f"媒体渠道创建成功: {media.media_id}")
        return MediaChannelResponse(
            media_id=media.media_id,
            media_name=media.media_name,
            type=media.type,
            vpt_list=media.vpt_list,
            pft_list=media.pft_list,
            start_date=media.start_date,
            end_date=media.end_date,
            create_time=datetime.now()
        )
    except Exception as e:
        logger.error(f"创建媒体渠道失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/media-channel", response_model=List[MediaChannelResponse])
async def list_media_channels(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: Optional[str] = Query(None)
):
    """获取媒体渠道列表"""
    try:
        client = get_clickhouse_client()
        
        where_clause = f"WHERE type = '{type}'" if type else ""
        query = f"""
            SELECT media_id, media_name, type, vpt_list, pft_list, 
                   start_date, end_date, create_time
            FROM dim_media_channel
            {where_clause}
            ORDER BY create_time DESC
            LIMIT {limit} OFFSET {skip}
        """
        
        results = client.execute(query)
        channels = []
        for row in results:
            channels.append(MediaChannelResponse(
                media_id=row[0],
                media_name=row[1],
                type=row[2] if row[2] else None,
                vpt_list=row[3] if row[3] else None,
                pft_list=row[4] if row[4] else None,
                start_date=row[5] if row[5] else None,
                end_date=row[6] if row[6] else None,
                create_time=row[7]
            ))
        
        return channels
    except Exception as e:
        logger.error(f"获取媒体渠道列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 其他维度表API类似实现...
# 为了节省篇幅，这里只展示前几个表的完整实现


