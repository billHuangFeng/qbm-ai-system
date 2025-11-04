import { createClient } from 'jsr:@supabase/supabase-js@2';
import { corsHeaders, handleCors } from '../_shared/cors.ts';
import { parseFile } from '../_shared/file-parser.ts';
import { validateData, ValidationRule } from '../_shared/data-validator.ts';

console.log('data-import-validate function started');

Deno.serve(async (req) => {
  // Handle CORS
  const corsResponse = handleCors(req);
  if (corsResponse) return corsResponse;

  try {
    // 验证请求方法
    if (req.method !== 'POST') {
      return new Response(
        JSON.stringify({ error: 'Method not allowed' }),
        { status: 405, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // 获取请求体
    const { file_id, validation_rules } = await req.json();

    if (!file_id) {
      return new Response(
        JSON.stringify({ error: 'file_id is required' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // 获取认证token
    const authHeader = req.headers.get('Authorization');
    if (!authHeader) {
      return new Response(
        JSON.stringify({ error: 'Missing authorization header' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // 创建 Supabase 客户端
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      { global: { headers: { Authorization: authHeader } } }
    );

    // 验证用户
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    if (userError || !user) {
      console.error('Auth error:', userError);
      return new Response(
        JSON.stringify({ error: 'Unauthorized' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    console.log('User authenticated:', user.id);

    // 获取用户的租户ID
    const { data: profile, error: profileError } = await supabase
      .from('user_profiles')
      .select('tenant_id')
      .eq('user_id', user.id)
      .single();

    if (profileError || !profile) {
      console.error('Profile error:', profileError);
      return new Response(
        JSON.stringify({ error: 'User profile not found' }),
        { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    const tenantId = profile.tenant_id;
    console.log('Tenant ID:', tenantId);

    // 获取上传记录
    const { data: upload, error: uploadError } = await supabase
      .from('data_import_uploads')
      .select('*')
      .eq('id', file_id)
      .eq('tenant_id', tenantId)
      .single();

    if (uploadError || !upload) {
      console.error('Upload not found:', uploadError);
      return new Response(
        JSON.stringify({ error: 'File not found' }),
        { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    console.log('Upload record found:', upload.file_name);

    // 从存储中下载文件
    const { data: fileData, error: downloadError } = await supabase.storage
      .from('data-import')
      .download(upload.storage_path);

    if (downloadError || !fileData) {
      console.error('Download error:', downloadError);
      return new Response(
        JSON.stringify({ error: 'Failed to download file' }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    console.log('File downloaded, size:', fileData.size);

    // 解析文件
    const fileExtension = upload.file_name.split('.').pop()?.toLowerCase() || '';
    const file = new File([fileData], upload.file_name);
    const parsedData = await parseFile(file, fileExtension);

    console.log('File parsed, rows:', parsedData.rowCount, 'columns:', parsedData.columnCount);

    // 验证数据
    const rules: ValidationRule = validation_rules || {};
    const qualityReport = await validateData(parsedData, rules);

    console.log('Validation complete, score:', qualityReport.overall_quality_score);

    // 保存质量报告到数据库
    const { error: reportError } = await supabase
      .from('data_quality_report')
      .insert({
        staging_id: file_id,
        tenant_id: tenantId,
        overall_quality_score: qualityReport.overall_quality_score,
        completeness_score: qualityReport.completeness_score,
        accuracy_score: qualityReport.accuracy_score,
        consistency_score: qualityReport.consistency_score,
        quality_issues: qualityReport.issues,
        validation_rules: rules,
        missing_field_count: qualityReport.issues.filter(i => i.type === 'missing_field').length,
        invalid_format_count: qualityReport.issues.filter(i => i.type === 'type_mismatch').length,
        duplicate_count: qualityReport.issues.filter(i => i.type === 'duplicate').reduce((sum, i) => sum + i.affected_rows, 0),
        outlier_count: qualityReport.issues.filter(i => i.type === 'outlier').reduce((sum, i) => sum + i.affected_rows, 0),
      });

    if (reportError) {
      console.error('Failed to save quality report:', reportError);
    }

    // 更新上传记录状态
    await supabase
      .from('data_import_uploads')
      .update({ 
        status: qualityReport.overall_quality_score >= 70 ? 'validated' : 'validation_failed' 
      })
      .eq('id', file_id);

    return new Response(
      JSON.stringify({
        success: true,
        quality_report: qualityReport,
      }),
      { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Validation error:', error);
    return new Response(
      JSON.stringify({ 
        error: 'Validation failed', 
        details: error instanceof Error ? error.message : String(error) 
      }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});
