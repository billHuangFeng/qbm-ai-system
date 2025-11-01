from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_start_batch_and_list_issues():
    # start batch
    resp = client.post("/ingestion/batches:start", json={"source_system": "ERP", "files": ["s.csv"]})
    assert resp.status_code == 200
    batch_id = resp.json()["batch_id"]

    # list issues
    resp2 = client.get(f"/ingestion/issues", params={"batch_id": batch_id})
    assert resp2.status_code == 200
    assert isinstance(resp2.json(), list)


def test_ingestion_rules_get():
    resp = client.get("/ingestion/rules")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)

