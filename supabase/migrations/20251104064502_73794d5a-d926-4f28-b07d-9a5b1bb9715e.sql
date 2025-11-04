-- 创建数据导入文件存储桶
INSERT INTO storage.buckets (id, name, public)
VALUES ('data-import', 'data-import', false)
ON CONFLICT (id) DO NOTHING;

-- 创建存储桶的 RLS 策略
CREATE POLICY "Users can upload files to their tenant folder"
  ON storage.objects FOR INSERT
  WITH CHECK (
    bucket_id = 'data-import' 
    AND (storage.foldername(name))[1] = get_user_tenant_id(auth.uid())::text
  );

CREATE POLICY "Users can view their tenant's files"
  ON storage.objects FOR SELECT
  USING (
    bucket_id = 'data-import' 
    AND (storage.foldername(name))[1] = get_user_tenant_id(auth.uid())::text
  );

CREATE POLICY "Users can update their tenant's files"
  ON storage.objects FOR UPDATE
  USING (
    bucket_id = 'data-import' 
    AND (storage.foldername(name))[1] = get_user_tenant_id(auth.uid())::text
  );

CREATE POLICY "Users can delete their tenant's files"
  ON storage.objects FOR DELETE
  USING (
    bucket_id = 'data-import' 
    AND (storage.foldername(name))[1] = get_user_tenant_id(auth.uid())::text
  );