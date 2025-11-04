import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
import { corsHeaders, handleCors } from '../_shared/cors.ts';
import { parseFile } from '../_shared/file-parser.ts';
import { detectFormat } from '../_shared/format-detector.ts';

console.log('data-import-upload Edge Function started');

serve(async (req) => {
  // 处理 CORS preflight 请求
  const corsResponse = handleCors(req);
  if (corsResponse) return corsResponse;

  try {
    // 验证请求方法
    if (req.method !== 'POST') {
      return new Response(
        JSON.stringify({ 
          success: false, 
          error: { 
            code: 'METHOD_NOT_ALLOWED', 
            message: '仅支持POST方法' 
          } 
        }),
        { 
          status: 405, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      );
    }

    // 解析 FormData
    const formData = await req.formData();
    const file = formData.get('file') as File;
    
    if (!file) {
      return new Response(
        JSON.stringify({ 
          success: false, 
          error: { 
            code: 'MISSING_FILE', 
            message: '未提供文件' 
          } 
        }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      );
    }

    // 验证文件格式
    const allowedExtensions = ['.csv', '.xlsx', '.xls', '.json'];
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!allowedExtensions.includes(fileExtension)) {
      return new Response(
        JSON.stringify({ 
          success: false, 
          error: { 
            code: 'INVALID_FILE_FORMAT', 
            message: '不支持的文件格式，仅支持 CSV, Excel, JSON' 
          } 
        }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      );
    }

    // 验证文件大小（最大50MB）
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
      return new Response(
        JSON.stringify({ 
          success: false, 
          error: { 
            code: 'FILE_TOO_LARGE', 
            message: '文件大小超过限制（最大50MB）',
            details: {
              file_size: file.size,
              max_size: maxSize
            }
          } 
        }),
        { 
          status: 413, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      );
    }

    // 获取认证信息
    const authHeader = req.headers.get('Authorization');
    if (!authHeader) {
      return new Response(
        JSON.stringify({ 
          success: false, 
          error: { 
            code: 'UNAUTHORIZED', 
            message: '未提供认证信息' 
          } 
        }),
        { 
          status: 401, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      );
    }

    // 初始化 Supabase 客户端
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey, {
      auth: {
        autoRefreshToken: false,
        persistSession: false
      }
    });

    // 验证用户并获取租户ID
    const token = authHeader.replace('Bearer ', '');
    const { data: { user }, error: authError } = await supabase.auth.getUser(token);
    
    if (authError || !user) {
      return new Response(
        JSON.stringify({ 
          success: false, 
          error: { 
            code: 'UNAUTHORIZED', 
            message: '认证失败' 
          } 
        }),
        { 
          status: 401, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      );
    }

    // 获取用户的租户ID
    const { data: profile } = await supabase
      .from('user_profiles')
      .select('tenant_id')
      .eq('user_id', user.id)
      .single();

    if (!profile?.tenant_id) {
      return new Response(
        JSON.stringify({ 
          success: false, 
          error: { 
            code: 'NO_TENANT', 
            message: '用户未关联租户' 
          } 
        }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      );
    }

    const tenantId = profile.tenant_id;
    const sourceSystem = (formData.get('source_system') as string) || 'unknown';
    const documentType = (formData.get('document_type') as string) || null;

    console.log('Processing file upload:', {
      fileName: file.name,
      fileSize: file.size,
      tenantId,
      userId: user.id
    });

    // 解析文件内容
    const parsedData = await parseFile(file, fileExtension);
    
    console.log('File parsed:', {
      rowCount: parsedData.rowCount,
      columnCount: parsedData.columnCount
    });

    // 调用格式识别算法
    const formatDetection = await detectFormat(parsedData.data);
    
    console.log('Format detected:', {
      formatType: formatDetection.formatType,
      confidence: formatDetection.confidence
    });

    // 生成文件ID和存储路径
    const fileId = crypto.randomUUID();
    const storagePath = `${tenantId}/${fileId}/${file.name}`;

    // 上传文件到 Supabase Storage
    const fileBuffer = await file.arrayBuffer();
    const { error: uploadError } = await supabase.storage
      .from('data-import')
      .upload(storagePath, fileBuffer, {
        contentType: file.type || 'application/octet-stream',
        upsert: false
      });

    if (uploadError) {
      console.error('Storage upload error:', uploadError);
      throw new Error(`文件上传失败: ${uploadError.message}`);
    }

    console.log('File uploaded to storage:', storagePath);

    // 保存上传记录到数据库
    const { error: dbError } = await supabase
      .from('data_import_uploads')
      .insert({
        id: fileId,
        tenant_id: tenantId,
        user_id: user.id,
        file_name: file.name,
        file_size: file.size,
        row_count: parsedData.rowCount,
        column_count: parsedData.columnCount,
        format_type: formatDetection.formatType,
        format_confidence: formatDetection.confidence,
        storage_path: storagePath,
        source_system: sourceSystem,
        document_type: documentType,
        status: 'uploaded',
        uploaded_at: new Date().toISOString()
      });

    if (dbError) {
      console.error('Database insert error:', dbError);
      // 清理已上传的文件
      await supabase.storage.from('data-import').remove([storagePath]);
      throw new Error(`数据库保存失败: ${dbError.message}`);
    }

    console.log('Upload record saved to database');

    // 返回成功响应
    return new Response(
      JSON.stringify({
        success: true,
        file_id: fileId,
        file_name: file.name,
        file_size: file.size,
        row_count: parsedData.rowCount,
        column_count: parsedData.columnCount,
        format_detection: {
          format_type: formatDetection.formatType,
          confidence: formatDetection.confidence,
          details: formatDetection.details
        },
        storage_path: storagePath,
        uploaded_at: new Date().toISOString()
      }),
      { 
        status: 200, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );

  } catch (error: any) {
    console.error('Error in data-import-upload:', error);
    
    return new Response(
      JSON.stringify({
        success: false,
        error: {
          code: 'SERVER_ERROR',
          message: error?.message || '服务器内部错误',
          details: { error: error?.toString() || 'Unknown error' }
        }
      }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );
  }
});
