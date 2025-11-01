$ErrorActionPreference = 'Stop'

$base = "http://127.0.0.1:8081"
$headers = @{"Content-Type"="application/json"}

Write-Host "[1/5] Start batch" -ForegroundColor Cyan
$start = Invoke-RestMethod -Method Post -Uri "$base/ingestion/batches:start" -Headers $headers -Body '{"source_system":"ERP","files":["sales_2025_01.csv"]}'
$batchId = $start.batch_id

Start-Sleep -Seconds 1
Write-Host "[2/5] List issues" -ForegroundColor Cyan
$issues = Invoke-RestMethod -Method Get -Uri "$base/ingestion/issues?batch_id=$batchId"
$issueId = $issues[0].issue_id

Write-Host "[3/5] Preview issue" -ForegroundColor Cyan
$preview = Invoke-RestMethod -Method Get -Uri "$base/ingestion/issues/$issueId/preview"

Write-Host "[4/5] Apply fix" -ForegroundColor Cyan
$apply = Invoke-RestMethod -Method Post -Uri "$base/ingestion/issues/$issueId/apply" -Headers $headers -Body '{"action":"apply","patch":{"product_name":"iPhone 15 Pro"}}'

Write-Host "[5/5] Reconcile report" -ForegroundColor Cyan
$recon = Invoke-RestMethod -Method Get -Uri "$base/ingestion/reconcile/report?batch_id=$batchId"

$report = [pscustomobject]@{
  batch_id = $batchId
  issue_id = $issueId
  start    = $start
  preview  = $preview
  apply    = $apply
  reconcile= $recon
}

$out = Join-Path $PSScriptRoot "acceptance_ingestion_mock_report.json"
$report | ConvertTo-Json -Depth 8 | Out-File -Encoding utf8 -FilePath $out
Write-Host "Saved report to $out" -ForegroundColor Green



