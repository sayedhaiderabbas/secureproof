# Devpost Submission Package

## Project Title
SecureProof

## Tagline
AI-Assisted Cybersecurity Evidence Integrity & Blockchain Verification

## Short Description
SecureProof helps security teams detect whether investigation evidence still matches an earlier cryptographic proof, combining exact SHA-256 hashing, AI-assisted review, audit events, and a minimal blockchain registry without placing raw evidence on-chain.

## Long Description
Security evidence changes hands during incident response and forensic investigations. SecureProof creates a repeatable workflow: an analyst uploads a safe evidence artifact, the server validates it and calculates its exact SHA-256, a deterministic local analysis identifies potential indicators for analyst review, and the hash can be registered as a blockchain-backed proof. Later, SecureProof recalculates the current bytes and returns VERIFIED or INTEGRITY MISMATCH.

The design is deliberately privacy-conscious. Evidence stays off-chain. The Solidity contract stores only a non-sensitive identifier, cryptographic hash, timestamp, and registering address. The system does not claim that blockchain proves the truthfulness of evidence, who altered it, or when an alteration happened.

## Key Features

- Secure evidence ingestion and duplicate detection
- Real SHA-256 hashing
- Structured Demo / Rule-Based Analysis fallback
- Minimal Solidity proof registry
- Verification with original and current hashes
- Audit timeline and investigation report
- Professional responsive dashboard

## Technology Stack
React, TypeScript, Vite, FastAPI, Pydantic, SQLAlchemy, SQLite, Python hashlib, Solidity, Hardhat, ethers.js, pytest.

## Innovation
Blockchain is used for a narrow, functional purpose: a shared append-only reference for a cryptographic proof. Raw evidence and sensitive content remain off-chain.

## Cybersecurity Impact
The workflow is designed for SOC analysts, incident response teams, digital forensics workflows, and auditors who need an explicit answer to whether the bytes they hold match a previous registered state.

## Technical Challenges
The MVP balances exact byte handling, safe uploads, structured AI boundaries, privacy, persistence, and honest offline behavior. The local ledger makes the demo reproducible, while the contract and configuration document the path to a real RPC deployment.

## Future Development
Add authentication, RBAC, encrypted storage, malware scanning, rate limiting, signed report exports, real RPC adapters, provider-backed AI with schema validation, and multi-party custody workflows.
