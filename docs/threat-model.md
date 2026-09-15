# Threat Model

| Threat | Impact | Mitigation | Residual risk |
|---|---|---|---|
| Evidence tampering | Verification can fail or analysts can be misled | Exact-byte SHA-256 and independently stored proof | Only detects mismatch after registration; does not identify actor |
| Malicious upload | Resource exhaustion or unsafe processing | Extension allow-list, size limit, text/binary checks, no execution | No antivirus or sandbox in MVP |
| Path traversal | Arbitrary file overwrite/read | UUID storage references and sanitized display name | Local filesystem permissions still matter |
| API abuse | Upload flooding or data exposure | Small upload limit, concise errors, configured CORS | No authentication, rate limits, or quotas |
| Unauthorized modification | Evidence or metadata may be changed | Database constraints and append-style timeline | No identity/access-control layer |
| Hash substitution | False proof could be registered | Hash generated server-side from stored bytes | Compromised backend can register incorrect data |
| Blockchain credential compromise | Attacker can register proofs | Private key is backend-only environment configuration | Key custody, rotation, and HSM are not included |
| AI prompt injection | Evidence text could influence an AI provider | Evidence is untrusted data; local rules do not follow instructions | External provider adapter needs independent testing |
| Sensitive data exposure | Evidence may contain private information | Off-chain boundary, no evidence in logs or chain | Local storage is not encrypted in MVP |
| Frontend compromise | UI could misrepresent state | Backend remains source of truth and returns actual values | Browser security headers/auth are deployment concerns |
