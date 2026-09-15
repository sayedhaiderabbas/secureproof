import hashlib
import json
import re
from pathlib import Path
from uuid import uuid4

from .config import settings

ALLOWED_EXTENSIONS = {".txt", ".log", ".json", ".csv"}


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def validate_upload(filename: str, content: bytes) -> str:
    suffix = Path(filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported evidence type. Use TXT, LOG, JSON, or CSV.")
    if not content:
        raise ValueError("Evidence file cannot be empty.")
    if len(content) > settings.max_upload_bytes:
        raise ValueError(f"Evidence exceeds the {settings.max_upload_bytes // (1024 * 1024)} MB limit.")
    if suffix == ".json":
        try:
            json.loads(content.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError("JSON evidence must contain valid UTF-8 JSON.") from error
    elif b"\x00" in content:
        raise ValueError("Binary content is not accepted for this evidence type.")
    return suffix.removeprefix(".").upper()


def store_evidence(content: bytes) -> str:
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    reference = f"{uuid4().hex}.bin"
    (settings.upload_dir / reference).write_bytes(content)
    return reference


def analyze_evidence(content: bytes) -> dict:
    text = content.decode("utf-8", errors="replace")
    lower = text.lower()
    indicators: list[str] = []
    recommendations: list[str] = []
    if len(re.findall(r"failed login", lower)) >= 2:
        indicators.append("Repeated failed login attempts")
        recommendations.append("Review authentication logs and consider account protection controls.")
    if "suspicious login" in lower or "unusual login" in lower:
        indicators.append("Suspicious or unusual authentication activity")
        recommendations.append("Validate source context, identity, and access timing with the analyst.")
    if "privilege escalation" in lower:
        indicators.append("Privilege escalation indicator")
        recommendations.append("Review privileged activity and correlate with approved change records.")
    if "sudo " in lower or "powershell" in lower or "cmd.exe" in lower:
        indicators.append("Suspicious command pattern")
        recommendations.append("Perform command-line review in a controlled forensic workflow.")
    risk = "HIGH" if len(indicators) >= 3 else "MEDIUM" if indicators else "LOW"
    category = "Authentication and privilege activity" if indicators else "Unclassified security evidence"
    return {
        "incident_category": category,
        "risk_level": risk,
        "confidence": min(95, 55 + len(indicators) * 10),
        "summary": "Demo / Rule-Based Analysis: potential indicators identified for analyst review." if indicators else "Demo / Rule-Based Analysis: no configured indicators detected.",
        "indicators": indicators,
        "recommendations": recommendations or ["Retain context and perform analyst-led review."],
    }
