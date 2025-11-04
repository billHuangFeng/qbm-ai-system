-- 创建数据导入相关表

-- 1. 数据导入上传记录表
CREATE TABLE IF NOT EXISTS public.data_import_uploads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  user_id UUID,
  file_name TEXT NOT NULL,
  file_size INTEGER NOT NULL,
  row_count INTEGER,
  column_count INTEGER,
  format_type TEXT,
  format_confidence NUMERIC(5,2),
  storage_path TEXT NOT NULL,
  source_system TEXT,
  document_type TEXT,
  status TEXT NOT NULL DEFAULT 'uploaded',
  uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2. 字段映射历史表
CREATE TABLE IF NOT EXISTS public.field_mapping_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  user_id UUID,
  source_field TEXT NOT NULL,
  target_field TEXT NOT NULL,
  source_system TEXT NOT NULL,
  document_type TEXT,
  usage_count INTEGER DEFAULT 1,
  last_used_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3. 导入暂存表（用于存储导入中的数据）
CREATE TABLE IF NOT EXISTS public.staging_document_import (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  upload_id UUID NOT NULL REFERENCES public.data_import_uploads(id) ON DELETE CASCADE,
  tenant_id UUID NOT NULL,
  row_index INTEGER NOT NULL,
  raw_data JSONB NOT NULL,
  mapped_data JSONB,
  validation_status TEXT,
  validation_errors JSONB,
  match_results JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_data_import_uploads_tenant ON public.data_import_uploads(tenant_id);
CREATE INDEX IF NOT EXISTS idx_data_import_uploads_status ON public.data_import_uploads(status);
CREATE INDEX IF NOT EXISTS idx_field_mapping_history_tenant ON public.field_mapping_history(tenant_id);
CREATE INDEX IF NOT EXISTS idx_field_mapping_history_source ON public.field_mapping_history(source_field, source_system, document_type);
CREATE INDEX IF NOT EXISTS idx_staging_document_import_upload ON public.staging_document_import(upload_id);
CREATE INDEX IF NOT EXISTS idx_staging_document_import_tenant ON public.staging_document_import(tenant_id);

-- 启用 pg_trgm 扩展（用于模糊匹配）
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 创建更新时间触发器
CREATE TRIGGER update_data_import_uploads_updated_at
  BEFORE UPDATE ON public.data_import_uploads
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_field_mapping_history_updated_at
  BEFORE UPDATE ON public.field_mapping_history
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_staging_document_import_updated_at
  BEFORE UPDATE ON public.staging_document_import
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- 启用 RLS
ALTER TABLE public.data_import_uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.field_mapping_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.staging_document_import ENABLE ROW LEVEL SECURITY;

-- 创建 RLS 策略
CREATE POLICY "Users can view their tenant's upload records"
  ON public.data_import_uploads FOR SELECT
  USING (tenant_id = get_user_tenant_id(auth.uid()));

CREATE POLICY "Users can insert their tenant's upload records"
  ON public.data_import_uploads FOR INSERT
  WITH CHECK (tenant_id = get_user_tenant_id(auth.uid()));

CREATE POLICY "Users can update their tenant's upload records"
  ON public.data_import_uploads FOR UPDATE
  USING (tenant_id = get_user_tenant_id(auth.uid()));

CREATE POLICY "Users can view their tenant's field mapping history"
  ON public.field_mapping_history FOR SELECT
  USING (tenant_id = get_user_tenant_id(auth.uid()));

CREATE POLICY "Users can insert their tenant's field mapping history"
  ON public.field_mapping_history FOR INSERT
  WITH CHECK (tenant_id = get_user_tenant_id(auth.uid()));

CREATE POLICY "Users can update their tenant's field mapping history"
  ON public.field_mapping_history FOR UPDATE
  USING (tenant_id = get_user_tenant_id(auth.uid()));

CREATE POLICY "Users can view their tenant's staging data"
  ON public.staging_document_import FOR SELECT
  USING (tenant_id = get_user_tenant_id(auth.uid()));

CREATE POLICY "Users can insert their tenant's staging data"
  ON public.staging_document_import FOR INSERT
  WITH CHECK (tenant_id = get_user_tenant_id(auth.uid()));

CREATE POLICY "Users can update their tenant's staging data"
  ON public.staging_document_import FOR UPDATE
  USING (tenant_id = get_user_tenant_id(auth.uid()));

CREATE POLICY "Users can delete their tenant's staging data"
  ON public.staging_document_import FOR DELETE
  USING (tenant_id = get_user_tenant_id(auth.uid()));