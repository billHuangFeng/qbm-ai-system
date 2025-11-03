"""
数据增强服务模块
提供数据导入完善系统的第3阶段服务
"""

try:
    from .master_data_matcher import MasterDataMatcher, MasterDataMatchError
    from .calculation_conflict_detector import CalculationConflictDetector, CalculationConflictError
    from .smart_value_imputer import SmartValueImputer, ImputationError
    from .data_quality_assessor import DataQualityAssessor, QualityAssessmentError
    from .staging_table_manager import StagingTableManager, StagingTableError
except ImportError as e:
    # 处理依赖缺失的情况
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"数据增强服务导入失败，可能缺少依赖: {e}")
    
    # 创建占位类
    class MasterDataMatcher:
        pass
    class CalculationConflictDetector:
        pass
    class SmartValueImputer:
        pass
    class DataQualityAssessor:
        pass
    class StagingTableManager:
        pass
    class MasterDataMatchError(Exception):
        pass
    class CalculationConflictError(Exception):
        pass
    class ImputationError(Exception):
        pass
    class QualityAssessmentError(Exception):
        pass
    class StagingTableError(Exception):
        pass

__all__ = [
    "MasterDataMatcher",
    "MasterDataMatchError",
    "CalculationConflictDetector",
    "CalculationConflictError",
    "SmartValueImputer",
    "ImputationError",
    "DataQualityAssessor",
    "QualityAssessmentError",
    "StagingTableManager",
    "StagingTableError",
]

