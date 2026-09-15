# SecureProof 2:30 Demo

1. **00:00** Explain that investigation files can be copied or changed without a visible signal. SecureProof anchors a cryptographic proof without putting raw evidence on-chain.
2. **00:20** Upload `evidence/sample-auth-incident.log` from the Evidence view.
3. **00:35** Show the labeled Demo / Rule-Based Analysis result: repeated failed logins, suspicious login activity, and a privilege escalation indicator.
4. **00:50** Point to the complete SHA-256 fingerprint and use the copy control.
5. **01:05** Select Register proof. In the default offline profile, call out that the development ledger is explicitly labeled. With a deployed RPC profile, show the returned transaction hash, network, contract address, and block number.
6. **01:25** Select Verify current bytes and show `VERIFIED`.
7. **01:40** Stop the API, append one byte to the stored demo evidence as a controlled test, and restart it.
8. **01:50** Verify again. Show original and current hashes side by side.
9. **02:00** Show `INTEGRITY MISMATCH` and read the precise message: the bytes no longer match the registered proof; SecureProof does not claim who changed them or when.
10. **02:15** Explain the audit timeline and why a shared proof anchor helps teams compare evidence state across handoffs.
11. **02:30** Close with future work: authentication, encrypted object storage, real RPC deployment, and provider-backed AI with strict structured-output validation.
