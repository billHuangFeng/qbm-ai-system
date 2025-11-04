import { createClient } from 'jsr:@supabase/supabase-js@2';
import { corsHeaders, handleCors } from '../_shared/cors.ts';
import { parseFile } from '../_shared/file-parser.ts';
import { matchMasterData, extractUniqueValues, MatchConfig } from '../_shared/master-data-matcher.ts';

console.log('data-import-match-master function started');

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
    const { file_id, match_config } = await req.json();

    if (!file_id || !match_config) {
      return new Response(
        JSON.stringify({ error: 'file_id and match_config are required' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // 验证 match_config
    const config: MatchConfig = match_config;
    if (!config.entity_type || !config.match_fields || config.match_fields.length === 0) {
      return new Response(
        JSON.stringify({ error: 'Invalid match_config: entity_type and match_fields are required' }),
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

    // 提取要匹配的字段值（使用第一个匹配字段）
    const matchField = config.match_fields[0];
    if (!parsedData.columns.includes(matchField)) {
      return new Response(
        JSON.stringify({ 
          error: `Match field "${matchField}" not found in file. Available columns: ${parsedData.columns.join(', ')}` 
        }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    const sourceValues = extractUniqueValues(parsedData.data, matchField);
    console.log(`Extracted ${sourceValues.length} unique values from field "${matchField}"`);

    // 执行匹配
    const matchResults = await matchMasterData(supabase, tenantId, sourceValues, config);

    // 计算统计信息
    const matchedCount = matchResults.filter(r => r.matched).length;
    const unmatchedCount = matchResults.length - matchedCount;
    const matchRate = matchResults.length > 0 ? (matchedCount / matchResults.length * 100) : 0;

    console.log(`Match complete: ${matchedCount} matched, ${unmatchedCount} unmatched (${matchRate.toFixed(1)}%)`);

    return new Response(
      JSON.stringify({
        success: true,
        match_results: matchResults,
        statistics: {
          total: matchResults.length,
          matched: matchedCount,
          unmatched: unmatchedCount,
          match_rate: Math.round(matchRate * 10) / 10,
        },
      }),
      { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Match error:', error);
    return new Response(
      JSON.stringify({ 
        error: 'Match failed', 
        details: error instanceof Error ? error.message : String(error) 
      }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});
