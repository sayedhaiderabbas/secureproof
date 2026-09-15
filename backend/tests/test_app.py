import hashlib
import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./data/test.db"
os.environ["UPLOAD_DIR"] = "./data/test-evidence"
os.environ["BLOCKCHAIN_MODE"] = "memory"

from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.database import Base, engine


client = TestClient(app)


def setup_function():
    Path("./data").mkdir(parents=True, exist_ok=True)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    engine.dispose()
    database = Path("./data/test.db")
    if database.exists():
        database.unlink()
    if settings.upload_dir.exists():
        for path in settings.upload_dir.glob("*"):
            path.unlink()
    Base.metadata.create_all(bind=engine)


def test_health():
    assert client.get("/api/health").json() == {"status": "ok", "service": "secureproof"}


def test_upload_hash_analysis_and_duplicate():
    content = b"FAILED LOGIN\nFAILED LOGIN\nSUSPICIOUS LOGIN\nPRIVILEGE ESCALATION INDICATOR\n"
    response = client.post("/api/evidence/upload", files={"file": ("sample-auth-incident.log", content, "text/plain")})
    assert response.status_code == 201
    body = response.json()
    assert body["sha256_hash"] == hashlib.sha256(content).hexdigest()
    assert body["analysis"]["risk_level"] == "HIGH"
    assert client.post("/api/evidence/upload", files={"file": ("duplicate.log", content, "text/plain")}).status_code == 409


def test_blockchain_verification_and_tamper_detection():
    content = b"FAILED LOGIN\nSUSPICIOUS LOGIN\n"
    evidence = client.post("/api/evidence/upload", files={"file": ("sample.log", content, "text/plain")}).json()
    evidence_id = evidence["id"]
    registered = client.post(f"/api/evidence/{evidence_id}/register")
    assert registered.status_code == 200
    assert registered.json()["transaction_hash"].startswith("0x")
    verified = client.post(f"/api/evidence/{evidence_id}/verify")
    assert verified.json()["result"] == "VERIFIED"
    storage = settings.upload_dir / evidence["storage_reference"]
    storage.write_bytes(content + b"X")
    mismatch = client.post(f"/api/evidence/{evidence_id}/verify")
    assert mismatch.json()["result"] == "INTEGRITY MISMATCH"
    assert mismatch.json()["original_hash"] != mismatch.json()["current_hash"]
    assert client.get(f"/api/evidence/{evidence_id}/timeline").status_code == 200
