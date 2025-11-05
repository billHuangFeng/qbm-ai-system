from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_consistency_check_policy():
    payload = {"decision": {"goals": ["G1"], "resources": {"eng": 2}}}
    resp = client.post("/ai-consistency/check-policy", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "success" in data
    assert "compliance_score" in data or "violations" in data or "result" in data


def test_influence_analyze_propagation():
    payload = {
        "source_decision": {"id": "dec-1", "goals": ["G1"], "resources": {"eng": 3}},
        "propagation_depth": 2,
        "time_horizon": 7,
    }
    resp = client.post("/ai-influence/analyze-propagation", json=payload)
    assert resp.status_code == 200
    assert resp.json() is not None
