from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import os
from fastapi import APIRouter, HTTPException, Query, Header
from pydantic import BaseModel, Field


router = APIRouter()


# ---- Pydantic models (Mock) ----


class StartBatchRequest(BaseModel):
    source_system: str = Field(
        ..., description="数据来源系统名称或渠道，如 ERP/CRM/SFTP/API"
    )
    time_window_start: Optional[datetime] = None
    time_window_end: Optional[datetime] = None
    files: Optional[List[str]] = Field(
        default=None, description="当为文件导入时的文件名列表"
    )


class StartBatchResponse(BaseModel):
    batch_id: str
    status: str
    started_at: datetime


class UploadResponse(BaseModel):
    batch_id: str
    file_name: str
    head_valid: bool
    sample_preview: List[Dict[str, Any]]


class Issue(BaseModel):
    issue_id: str
    batch_id: str
    table: str
    row_ref: str
    issue_type: str
    confidence: float
    suggested_fix: Dict[str, Any]
    created_at: datetime
    status: str


class IssueApplyRequest(BaseModel):
    action: str = Field(..., description="apply/ignore/custom")
    patch: Optional[Dict[str, Any]] = None


class Rule(BaseModel):
    rule_id: str
    name: str
    params: Dict[str, Any]
    version: int
    enabled: bool = True


class AliasEntry(BaseModel):
    dict_type: str
    src_value: str
    std_value: str
    confidence: float = 0.95


class ReconcileReport(BaseModel):
    batch_id: str
    status: str
    diffs: List[Dict[str, Any]]


class QualityCheck(BaseModel):
    batch_id: str
    rule_id: str
    passed: bool
    failed_cnt: int


# ---- Endpoints (Mock implementations) ----


@router.post("/batches:start", response_model=StartBatchResponse)
async def start_batch(payload: StartBatchRequest) -> StartBatchResponse:
    now = datetime.utcnow()
    return StartBatchResponse(
        batch_id=f"batch_{int(now.timestamp())}",
        status="started",
        started_at=now,
    )


@router.get("/batches/{batch_id}")
async def get_batch_status(batch_id: str) -> Dict[str, Any]:
    return {
        "batch_id": batch_id,
        "status": "running",
        "started_at": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
        "progress": {
            "schema_validation": 100,
            "standardization": 60,
            "quality_checks": 20,
        },
    }


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file_name: str) -> UploadResponse:
    preview = [
        {"order_id": "SO-001", "amount": 123.45, "currency": "USD"},
        {"order_id": "SO-002", "amount": 98.00, "currency": "USD"},
    ]
    return UploadResponse(
        batch_id=f"batch_{int(datetime.utcnow().timestamp())}",
        file_name=file_name,
        head_valid=True,
        sample_preview=preview,
    )


@router.get("/issues", response_model=List[Issue])
async def list_issues(
    batch_id: str = Query(...),
    issue_type: Optional[str] = Query(None),
) -> List[Issue]:
    now = datetime.utcnow()
    issues: List[Issue] = [
        Issue(
            issue_id="iss-1",
            batch_id=batch_id,
            table="l1_sales_fact",
            row_ref="row-123",
            issue_type=issue_type or "low_confidence_match",
            confidence=0.62,
            suggested_fix={"customer": "ACME CORP"},
            created_at=now,
            status="pending",
        ),
        Issue(
            issue_id="iss-2",
            batch_id=batch_id,
            table="l1_sales_fact",
            row_ref="row-456",
            issue_type=issue_type or "enum_missing",
            confidence=0.0,
            suggested_fix={"channel": "B2B"},
            created_at=now,
            status="pending",
        ),
    ]
    return issues


@router.get("/issues/{issue_id}/preview")
async def preview_issue_fix(issue_id: str) -> Dict[str, Any]:
    return {
        "issue_id": issue_id,
        "before": {"product_name": "iPhne 15 Pro"},
        "after": {"product_name": "iPhone 15 Pro"},
        "delta": {"product_name": ["iPhne 15 Pro", "iPhone 15 Pro"]},
    }


@router.post("/issues/{issue_id}/apply")
async def apply_issue_fix(
    issue_id: str,
    payload: IssueApplyRequest,
    x_api_key: str | None = Header(default=None, convert_underscores=False),
) -> Dict[str, Any]:
    expected = os.getenv("INGESTION_API_KEY")
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="invalid api key")
    if payload.action not in {"apply", "ignore", "custom"}:
        raise HTTPException(status_code=400, detail="invalid action")
    return {
        "issue_id": issue_id,
        "result": "ok",
        "action": payload.action,
        "mock_mode": True,
    }


@router.post("/issues/bulk-apply")
async def bulk_apply_issues(
    issue_ids: List[str],
    x_api_key: str | None = Header(default=None, convert_underscores=False),
) -> Dict[str, Any]:
    expected = os.getenv("INGESTION_API_KEY")
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="invalid api key")
    return {"updated": len(issue_ids), "result": "ok", "mock_mode": True}


@router.get("/rules", response_model=List[Rule])
async def get_rules() -> List[Rule]:
    return [
        Rule(rule_id="r-1", name="currency_normalize", params={"to": "CNY"}, version=1),
        Rule(rule_id="r-2", name="tax_split", params={"rate": 0.13}, version=3),
    ]


class UpsertRuleRequest(BaseModel):
    name: str
    params: Dict[str, Any]
    enabled: bool = True


@router.post("/rules", response_model=Rule)
async def upsert_rule(
    payload: UpsertRuleRequest,
    x_api_key: str | None = Header(default=None, convert_underscores=False),
) -> Rule:
    expected = os.getenv("INGESTION_API_KEY")
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="invalid api key")
    return Rule(
        rule_id="r-new",
        name=payload.name,
        params=payload.params,
        version=1,
        enabled=payload.enabled,
    )


@router.get("/alias-dictionary", response_model=List[AliasEntry])
async def get_alias_dictionary(dict_type: str = Query(...)) -> List[AliasEntry]:
    return [
        AliasEntry(
            dict_type=dict_type,
            src_value="Apple Inc.",
            std_value="APPLE",
            confidence=0.97,
        ),
        AliasEntry(
            dict_type=dict_type, src_value="Aplle", std_value="APPLE", confidence=0.88
        ),
    ]


class UpsertAliasEntriesRequest(BaseModel):
    entries: List[AliasEntry]


@router.post("/alias-dictionary")
async def upsert_alias_entries(
    payload: UpsertAliasEntriesRequest,
    x_api_key: str | None = Header(default=None, convert_underscores=False),
) -> Dict[str, Any]:
    expected = os.getenv("INGESTION_API_KEY")
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="invalid api key")
    return {"inserted": len(payload.entries), "result": "ok", "mock_mode": True}


@router.get("/reconcile/report", response_model=ReconcileReport)
async def get_reconcile_report(batch_id: str = Query(...)) -> ReconcileReport:
    return ReconcileReport(
        batch_id=batch_id,
        status="balanced",
        diffs=[{"organization": "CN", "delta": 0.0}],
    )


@router.get("/../data-quality/checks", response_model=List[QualityCheck])
async def get_quality_checks(batch_id: str = Query(...)) -> List[QualityCheck]:
    return [
        QualityCheck(
            batch_id=batch_id, rule_id="Q-duplicate", passed=True, failed_cnt=0
        ),
        QualityCheck(
            batch_id=batch_id, rule_id="Q-foreign-key", passed=True, failed_cnt=0
        ),
    ]


@router.get("/actions")
async def get_actions(batch_id: str = Query(...)) -> Dict[str, Any]:
    return {
        "batch_id": batch_id,
        "actions": [
            {
                "action_id": "a-1",
                "issue_id": "iss-1",
                "operator": "admin",
                "ts": datetime.utcnow().isoformat(),
            },
            {
                "action_id": "a-2",
                "issue_id": "iss-2",
                "operator": "qa",
                "ts": datetime.utcnow().isoformat(),
            },
        ],
    }


@router.post("/batches/{batch_id}:replay")
async def replay_batch(batch_id: str) -> Dict[str, Any]:
    return {"batch_id": batch_id, "result": "queued"}
