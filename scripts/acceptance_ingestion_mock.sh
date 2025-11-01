#!/usr/bin/env bash
set -euo pipefail

BASE="http://127.0.0.1:8081"

echo "[1/5] Start batch"
START=$(curl -sS -X POST "$BASE/ingestion/batches:start" -H 'Content-Type: application/json' -d '{"source_system":"ERP","files":["sales_2025_01.csv"]}')
BATCH_ID=$(echo "$START" | python -c 'import sys,json;print(json.load(sys.stdin)["batch_id"])')

sleep 1
echo "[2/5] List issues"
ISSUES=$(curl -sS "$BASE/ingestion/issues?batch_id=$BATCH_ID")
ISSUE_ID=$(echo "$ISSUES" | python -c 'import sys,json;print(json.load(sys.stdin)[0]["issue_id"])')

echo "[3/5] Preview issue"
PREVIEW=$(curl -sS "$BASE/ingestion/issues/$ISSUE_ID/preview")

echo "[4/5] Apply fix"
APPLY=$(curl -sS -X POST "$BASE/ingestion/issues/$ISSUE_ID/apply" -H 'Content-Type: application/json' -d '{"action":"apply","patch":{"product_name":"iPhone 15 Pro"}}')

echo "[5/5] Reconcile report"
RECON=$(curl -sS "$BASE/ingestion/reconcile/report?batch_id=$BATCH_ID")

REPORT=$(python - <<PY
import json,sys
print(json.dumps({
  'batch_id': '$BATCH_ID',
  'issue_id': '$ISSUE_ID',
  'start': json.loads('''$START'''),
  'preview': json.loads('''$PREVIEW'''),
  'apply': json.loads('''$APPLY'''),
  'reconcile': json.loads('''$RECON''')
}, ensure_ascii=False))
PY
)

OUT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "$REPORT" > "$OUT_DIR/acceptance_ingestion_mock_report.json"
echo "Saved report to $OUT_DIR/acceptance_ingestion_mock_report.json"



