-- ============================================
-- 修复 field_mapping_history 表结构
-- 添加缺失字段并重命名字段以匹配代码需求
-- ============================================

-- 1. 添加缺失字段
ALTER TABLE public.field_mapping_history
  ADD COLUMN IF NOT EXISTS match_confidence NUMERIC(5,2) DEFAULT 0.0,
  ADD COLUMN IF NOT EXISTS match_method TEXT DEFAULT 'manual',
  ADD COLUMN IF NOT EXISTS is_confirmed BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS is_rejected BOOLEAN DEFAULT FALSE;

-- 2. 添加新字段（保持向后兼容，同时支持新旧字段名）
ALTER TABLE public.field_mapping_history
  ADD COLUMN IF NOT EXISTS source_field_name TEXT,
  ADD COLUMN IF NOT EXISTS target_field_name TEXT;

-- 3. 迁移数据（将旧字段数据复制到新字段）
UPDATE public.field_mapping_history
SET 
  source_field_name = COALESCE(source_field_name, source_field),
  target_field_name = COALESCE(target_field_name, target_field),
  is_confirmed = COALESCE(is_confirmed, TRUE),  -- 默认已存在的映射为已确认
  match_method = COALESCE(match_method, mapping_method, 'manual'),  -- 默认映射方法为手动
  match_confidence = COALESCE(match_confidence, confidence_score::numeric, 0.0)  -- 默认置信度为0
WHERE source_field_name IS NULL OR target_field_name IS NULL;

-- 4. 添加target_table字段（如果不存在）
ALTER TABLE public.field_mapping_history
  ADD COLUMN IF NOT EXISTS target_table VARCHAR(100);

-- 5. 添加created_by字段（如果不存在）
ALTER TABLE public.field_mapping_history
  ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES auth.users(id);

-- 5. 删除旧字段（如果不再需要）
-- 注意：为了向后兼容，这里先保留旧字段
-- 如果确认不再需要，可以取消注释下面的代码
-- ALTER TABLE public.field_mapping_history
--   DROP COLUMN IF EXISTS source_field,
--   DROP COLUMN IF EXISTS target_field;

-- 6. 更新唯一约束（如果存在）
-- 先删除旧的唯一约束（如果存在）
ALTER TABLE public.field_mapping_history
  DROP CONSTRAINT IF EXISTS uk_field_mapping_history;

-- 创建新的唯一约束（优先使用新字段名，如果不存在则使用旧字段名）
-- 注意：由于PostgreSQL不支持在唯一约束中使用COALESCE，我们需要创建一个函数索引
CREATE UNIQUE INDEX IF NOT EXISTS uk_field_mapping_history_unique 
  ON public.field_mapping_history(
    tenant_id, 
    source_system, 
    COALESCE(target_table, ''),
    COALESCE(source_field_name, source_field),
    COALESCE(target_field_name, target_field)
  );

-- 7. 更新索引
-- 删除旧索引
DROP INDEX IF EXISTS idx_field_mapping_history_source;

-- 创建新索引（使用新字段名）
CREATE INDEX IF NOT EXISTS idx_field_mapping_history_source 
  ON public.field_mapping_history(source_field_name, source_system, document_type);

-- 创建查询优化索引（包含is_confirmed和is_rejected）
CREATE INDEX IF NOT EXISTS idx_field_mapping_history_lookup 
  ON public.field_mapping_history(
    tenant_id, 
    source_field_name, 
    source_system, 
    document_type, 
    is_confirmed, 
    is_rejected
  );

-- 8. 添加注释
COMMENT ON COLUMN public.field_mapping_history.source_field_name IS '源字段名（已重命名）';
COMMENT ON COLUMN public.field_mapping_history.target_field_name IS '目标字段名（已重命名）';
COMMENT ON COLUMN public.field_mapping_history.match_confidence IS '匹配置信度（0-1）';
COMMENT ON COLUMN public.field_mapping_history.match_method IS '匹配方法（manual/rule/similarity/history）';
COMMENT ON COLUMN public.field_mapping_history.is_confirmed IS '是否已确认';
COMMENT ON COLUMN public.field_mapping_history.is_rejected IS '是否已拒绝';

