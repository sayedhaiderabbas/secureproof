# SecureProof

**AI-Assisted Cybersecurity Evidence Integrity & Blockchain Verification**

SecureProof is a cybersecurity evidence-control MVP for SOC, incident response, forensics, and audit workflows. It accepts safe text evidence, calculates an exact SHA-256 fingerprint, produces clearly labeled AI-assisted analysis, registers a cryptographic proof, and verifies whether the current bytes still match.

## Problem
Evidence moves between analysts, systems, and investigations. A file can change while its filename and general appearance remain the same. Teams need a repeatable way to detect whether the bytes they hold match an earlier registered proof.

## Solution
SecureProof keeps evidence off-chain and stores only a minimal cryptographic proof on-chain. Verification compares the current SHA-256 with the registered hash. The result is `VERIFIED` or `INTEGRITY MISMATCH`.

## Features

- Secure TXT, LOG, JSON, and CSV ingestion with size and content validation
- UUID-backed off-chain storage and duplicate detection
- Exact SHA-256 generation and copyable UI fingerprint
- Deterministic local rule-based analysis without an API key
- Minimal Solidity `EvidenceRegistry` contract with duplicate and input validation
- Registration metadata and verification APIs
- Audit timeline and text investigation report
- Dashboard metrics based only on stored data
- Explicit limitation language and threat model

## How It Works

1. Upload evidence.
2. Validate and store bytes under a generated internal reference.
3. Calculate SHA-256 and analyze content as untrusted data.
4. Register only the evidence ID and hash.
5. Recalculate the current hash during verification.
6. Compare current bytes with the registered proof and record the result.

## Technology Stack

- Frontend: React, TypeScript, Vite, Lucide icons, custom responsive CSS
- Backend: FastAPI, Pydantic, SQLAlchemy, SQLite, pytest
- Blockchain: Solidity, Hardhat, ethers.js test tooling
- Cryptography: Python standard-library SHA-256

## Installation

```powershell
Copy-Item .env.example .env
Push-Location backend
python -m pip install -r requirements.txt
Pop-Location
Push-Location blockchain
npm install
Pop-Location
Push-Location frontend
npm install
Pop-Location
```

## Running Locally

Backend:

```powershell
Push-Location backend
python -m uvicorn app.main:app --reload --port 8000
```

Frontend in another terminal:

```powershell
Push-Location frontend
npm run dev
```

Open the Vite URL, normally `http://localhost:5173`.

## Environment Variables

See `.env.example`. The default `BLOCKCHAIN_MODE=memory` is an explicit offline development ledger. It is not a public blockchain deployment. For a real deployment configure `BLOCKCHAIN_RPC_URL`, `BLOCKCHAIN_PRIVATE_KEY`, `CONTRACT_ADDRESS`, and `CHAIN_ID` in the backend environment only.

## Smart Contract Setup

```powershell
Push-Location blockchain
npm run compile
npm test
npm run node
```

The contract is `blockchain/contracts/EvidenceRegistry.sol`. Deployment scripts and an RPC signer adapter are intentionally separate follow-up work; no fake public deployment address is claimed by this repository.

## Testing

```powershell
Push-Location backend
python -m pytest -q
Pop-Location
Push-Location blockchain
npm test
Pop-Location
Push-Location frontend
npm run build
```

The backend end-to-end test uploads fictional authentication evidence, checks its real SHA-256, registers a development proof, verifies the original, changes one byte, and verifies the mismatch.

## Reports and Limitations

`GET /api/evidence/{id}/report` returns a report containing evidence metadata, analysis, proof, verification, and the required disclaimer. This MVP has no user authentication, encrypted storage, rate limiting, malware scanning, or production RPC deployment. It must not be used as a production evidence repository without those controls.

SecureProof provides cryptographic integrity verification and AI-assisted analysis. It does not independently establish attribution, authorship, intent, or the exact time an alteration occurred.

## Hackathon / Devpost

**Short description:** SecureProof gives security teams a transparent chain from evidence intake to AI-assisted review, cryptographic hashing, blockchain-backed proof, and byte-level tamper detection.

**Innovation:** Blockchain is used narrowly as a shared proof anchor, not as a raw evidence store. The project demonstrates the functional distinction between evidence and evidence integrity.

**Impact:** SOC analysts, incident responders, forensic teams, and auditors can verify whether a file still matches a previously registered cryptographic state.

**Future:** Authentication and RBAC, encrypted object storage, real RPC deployment with key custody, provider-backed structured AI, signed exports, and multi-party evidence handoff.
