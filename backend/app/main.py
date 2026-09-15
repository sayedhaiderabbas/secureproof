import json
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from .blockchain import BlockchainUnavailable, blockchain_service
from .config import settings
from .database import Base, engine, get_db
from .models import Analysis, BlockchainProof, Evidence, IncidentEvent, Verification, utc_now
from .schemas import DashboardResponse, EventResponse, EvidenceResponse, ProofResponse, VerificationResponse
from .services import analyze_evidence, sha256_bytes, store_evidence, validate_upload

app = FastAPI(title="SecureProof API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):517[3-9]$",
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def event(db: Session, evidence_id: str, event_type: str, description: str, transaction_reference: str | None = None) -> None:
    db.add(IncidentEvent(evidence_id=evidence_id, event_type=event_type, description=description, transaction_reference=transaction_reference))


@app.on_event("startup")
def startup() -> None:
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    Path("./data").mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "secureproof"}


@app.get("/")
def root() -> dict[str, object]:
    return {
        "service": "secureproof",
        "status": "ok",
        "message": "SecureProof API is running. Open the frontend for the dashboard.",
        "frontend": "http://localhost:5173",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.post("/api/evidence/upload", response_model=EvidenceResponse, status_code=201)
async def upload_evidence(file: UploadFile = File(...), db: Session = Depends(get_db)) -> Evidence:
    content = await file.read(settings.max_upload_bytes + 1)
    try:
        evidence_type = validate_upload(file.filename or "", content)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    digest = sha256_bytes(content)
    duplicate = db.scalar(select(Evidence).where(Evidence.sha256_hash == digest))
    if duplicate:
        raise HTTPException(status_code=409, detail="Identical evidence has already been uploaded.")
    evidence = Evidence(original_filename=Path(file.filename or "evidence").name, evidence_type=evidence_type, file_size=len(content), sha256_hash=digest, storage_reference=store_evidence(content))
    db.add(evidence)
    db.flush()
    analysis = analyze_evidence(content)
    db.add(Analysis(evidence_id=evidence.id, incident_category=analysis["incident_category"], risk_level=analysis["risk_level"], confidence=analysis["confidence"], summary=analysis["summary"], indicators=json.dumps(analysis["indicators"]), recommendations=json.dumps(analysis["recommendations"])))
    event(db, evidence.id, "Evidence Uploaded", "Evidence accepted and stored off-chain with a generated storage reference.")
    event(db, evidence.id, "SHA-256 Generated", "SHA-256 was calculated from the exact uploaded bytes.")
    event(db, evidence.id, "AI Analysis Completed", "Deterministic rule-based analysis completed for analyst review.")
    db.commit()
    return db.scalar(select(Evidence).options(joinedload(Evidence.analysis)).where(Evidence.id == evidence.id))


@app.get("/api/evidence", response_model=list[EvidenceResponse])
def list_evidence(db: Session = Depends(get_db)) -> list[Evidence]:
    return list(db.scalars(select(Evidence).options(joinedload(Evidence.analysis)).order_by(Evidence.created_at.desc())).unique())


@app.get("/api/evidence/{evidence_id}", response_model=EvidenceResponse)
def get_evidence(evidence_id: str, db: Session = Depends(get_db)) -> Evidence:
    evidence = db.scalar(select(Evidence).options(joinedload(Evidence.analysis)).where(Evidence.id == evidence_id))
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found.")
    return evidence


@app.post("/api/evidence/{evidence_id}/register")
def register_evidence(evidence_id: str, db: Session = Depends(get_db)) -> dict:
    evidence = db.get(Evidence, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found.")
    if evidence.blockchain_proof:
        raise HTTPException(status_code=409, detail="Evidence already has a registered proof.")
    try:
        proof = blockchain_service.register(evidence.id, evidence.sha256_hash)
    except BlockchainUnavailable as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    db.add(BlockchainProof(evidence_id=evidence.id, evidence_hash=evidence.sha256_hash, network=proof.network, contract_address=proof.contract_address, transaction_hash=proof.transaction_hash, block_number=proof.block_number, timestamp=proof.timestamp))
    event(db, evidence.id, "Blockchain Proof Registered", "SHA-256 proof registered; raw evidence remains off-chain.", proof.transaction_hash)
    db.commit()
    return {"status": "CONFIRMED", "network": proof.network, "contract_address": proof.contract_address, "transaction_hash": proof.transaction_hash, "block_number": proof.block_number, "evidence_hash": evidence.sha256_hash, "timestamp": proof.timestamp}


@app.post("/api/evidence/{evidence_id}/verify", response_model=VerificationResponse)
def verify_evidence(evidence_id: str, db: Session = Depends(get_db)) -> VerificationResponse:
    evidence = db.get(Evidence, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found.")
    proof = db.scalar(select(BlockchainProof).where(BlockchainProof.evidence_id == evidence_id))
    if not proof:
        raise HTTPException(status_code=409, detail="Register a blockchain proof before verification.")
    storage_path = settings.upload_dir / evidence.storage_reference
    if not storage_path.is_file():
        raise HTTPException(status_code=500, detail="Stored evidence is unavailable.")
    current_hash = sha256_bytes(storage_path.read_bytes())
    result = "VERIFIED" if current_hash == proof.evidence_hash else "INTEGRITY MISMATCH"
    message = "The current evidence matches the cryptographic proof previously registered on-chain." if result == "VERIFIED" else "The current evidence does not match the previously registered cryptographic proof."
    verification = Verification(evidence_id=evidence.id, expected_hash=proof.evidence_hash, actual_hash=current_hash, result=result)
    db.add(verification)
    event(db, evidence.id, "Verification Requested", "Current evidence bytes were hashed and compared with the registered proof.")
    event(db, evidence.id, "Integrity Verified" if result == "VERIFIED" else "Integrity Mismatch", message)
    db.commit()
    return VerificationResponse(result=result, message=message, original_hash=proof.evidence_hash, current_hash=current_hash, verified_at=verification.verified_at)


@app.get("/api/evidence/{evidence_id}/proof", response_model=ProofResponse)
def get_proof(evidence_id: str, db: Session = Depends(get_db)) -> BlockchainProof:
    proof = db.scalar(select(BlockchainProof).where(BlockchainProof.evidence_id == evidence_id))
    if not proof:
        raise HTTPException(status_code=404, detail="Blockchain proof not found.")
    return proof


@app.get("/api/evidence/{evidence_id}/verification", response_model=VerificationResponse)
def get_latest_verification(evidence_id: str, db: Session = Depends(get_db)) -> VerificationResponse:
    verification = db.scalar(select(Verification).where(Verification.evidence_id == evidence_id).order_by(Verification.verified_at.desc()))
    if not verification:
        raise HTTPException(status_code=404, detail="No verification has been requested.")
    message = "The current evidence matches the cryptographic proof previously registered on-chain." if verification.result == "VERIFIED" else "The current evidence does not match the previously registered cryptographic proof."
    return VerificationResponse(result=verification.result, message=message, original_hash=verification.expected_hash, current_hash=verification.actual_hash, verified_at=verification.verified_at)


@app.get("/api/evidence/{evidence_id}/timeline", response_model=list[EventResponse])
def timeline(evidence_id: str, db: Session = Depends(get_db)) -> list[IncidentEvent]:
    if not db.get(Evidence, evidence_id):
        raise HTTPException(status_code=404, detail="Evidence not found.")
    return list(db.scalars(select(IncidentEvent).where(IncidentEvent.evidence_id == evidence_id).order_by(IncidentEvent.timestamp.asc())))


@app.get("/api/dashboard", response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db)) -> DashboardResponse:
    evidence = list(db.scalars(select(Evidence).options(joinedload(Evidence.analysis)).order_by(Evidence.created_at.desc())).unique())
    verified = db.scalar(select(func.count()).select_from(Verification).where(Verification.result == "VERIFIED")) or 0
    mismatches = db.scalar(select(func.count()).select_from(Verification).where(Verification.result == "INTEGRITY MISMATCH")) or 0
    high_risk = sum(1 for item in evidence if item.analysis and item.analysis.risk_level in {"HIGH", "CRITICAL"})
    return DashboardResponse(total_evidence=len(evidence), verified_evidence=verified, integrity_mismatches=mismatches, high_critical_risk=high_risk, recent_evidence=evidence[:8])


@app.get("/api/evidence/{evidence_id}/report", response_class=PlainTextResponse)
def report(evidence_id: str, db: Session = Depends(get_db)) -> str:
    evidence = db.scalar(select(Evidence).options(joinedload(Evidence.analysis), joinedload(Evidence.blockchain_proof)).where(Evidence.id == evidence_id))
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found.")
    latest = db.scalar(select(Verification).where(Verification.evidence_id == evidence_id).order_by(Verification.verified_at.desc()))
    analysis = evidence.analysis
    return "\n".join(["SECUREPROOF INVESTIGATION REPORT", f"Evidence ID: {evidence.id}", f"Filename: {evidence.original_filename}", f"Evidence Type: {evidence.evidence_type}", f"SHA-256: {evidence.sha256_hash}", f"AI Analysis: {analysis.summary if analysis else 'Unavailable'}", f"Risk: {analysis.risk_level if analysis else 'Unavailable'}", f"Indicators: {analysis.indicators if analysis else '[]'}", f"Recommendations: {analysis.recommendations if analysis else '[]'}", f"Transaction Hash: {evidence.blockchain_proof.transaction_hash if evidence.blockchain_proof else 'Not registered'}", f"Verification Result: {latest.result if latest else 'Not verified'}", "", "SecureProof provides cryptographic integrity verification and AI-assisted analysis. It does not independently establish attribution, authorship, intent, or the exact time an alteration occurred."])
