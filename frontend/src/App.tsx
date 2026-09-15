import { useEffect, useState } from "react";
import { Activity, CheckCircle2, Copy, FileCheck2, Fingerprint, LayoutDashboard, LockKeyhole, UploadCloud, ShieldAlert } from "lucide-react";

type Analysis = { incident_category: string; risk_level: string; confidence: number; summary: string; indicators: string[]; recommendations: string[] };
type Evidence = { id: string; original_filename: string; evidence_type: string; file_size: number; sha256_hash: string; created_at: string; status: string; analysis?: Analysis };
type Dashboard = { total_evidence: number; verified_evidence: number; integrity_mismatches: number; high_critical_risk: number; recent_evidence: Evidence[] };
type Verification = { result: string; message: string; original_hash: string; current_hash: string };
type Proof = { transaction_hash: string; network: string; contract_address: string; block_number: number; evidence_hash: string };
type Event = { event_type: string; description: string; timestamp: string; transaction_reference?: string };
type View = "Dashboard" | "Evidence" | "AI Analysis" | "Blockchain Proofs" | "Verification" | "Audit Timeline";
const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

export function App() {
  const [view, setView] = useState<View>("Dashboard");
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [selected, setSelected] = useState<Evidence | null>(null);
  const [notice, setNotice] = useState("Ready for evidence intake.");
  const [verification, setVerification] = useState<Verification | null>(null);
  const [proof, setProof] = useState<Proof | null>(null);
  const [timeline, setTimeline] = useState<Event[]>([]);

  async function refresh() {
    const [dash, list] = await Promise.all([fetch(`${API}/dashboard`), fetch(`${API}/evidence`)]);
    if (!dash.ok || !list.ok) throw new Error("API request failed");
    setDashboard(await dash.json()); setEvidence(await list.json());
  }
  async function loadEvidenceState(id: string) {
    const [proofResponse, verificationResponse, timelineResponse] = await Promise.all([fetch(`${API}/evidence/${id}/proof`), fetch(`${API}/evidence/${id}/verification`), fetch(`${API}/evidence/${id}/timeline`)]);
    setProof(proofResponse.ok ? await proofResponse.json() : null);
    setVerification(verificationResponse.ok ? await verificationResponse.json() : null);
    setTimeline(timelineResponse.ok ? await timelineResponse.json() : []);
  }
  useEffect(() => { refresh().catch(() => setNotice("API unavailable. Start the FastAPI service to connect the dashboard.")); }, []);
  async function upload(file: File) { const form = new FormData(); form.append("file", file); const response = await fetch(`${API}/evidence/upload`, { method: "POST", body: form }); if (!response.ok) throw new Error((await response.json()).detail); setNotice("Evidence accepted, hashed, and analyzed."); await refresh(); setView("Evidence"); }
  async function register() { if (!selected) return; const response = await fetch(`${API}/evidence/${selected.id}/register`, { method: "POST" }); const data = await response.json(); if (!response.ok) throw new Error(data.detail); setNotice(`Proof confirmed: ${data.transaction_hash}`); await refresh(); await loadEvidenceState(selected.id); setView("Blockchain Proofs"); }
  async function verify() { if (!selected) return; const response = await fetch(`${API}/evidence/${selected.id}/verify`, { method: "POST" }); const data = await response.json(); if (!response.ok) throw new Error(data.detail); setNotice(data.message); await refresh(); await loadEvidenceState(selected.id); setView("Verification"); }
  function choose(item: Evidence) { setSelected(item); setProof(null); setVerification(null); setTimeline([]); loadEvidenceState(item.id).catch(() => setNotice("Unable to load evidence audit state.")); }
  const active = selected || evidence[0];
  const nav = [[LayoutDashboard, "Dashboard"], [UploadCloud, "Evidence"], [Activity, "AI Analysis"], [LockKeyhole, "Blockchain Proofs"], [FileCheck2, "Verification"], [ShieldAlert, "Audit Timeline"]] as const;
  const card = (title: string, content: React.ReactNode) => <div className="panel detail"><div className="panel-head"><div><p className="eyebrow">SECUREPROOF MODULE</p><h2>{title}</h2></div></div>{content}</div>;
  const evidencePicker = <div className="panel evidence-list"><div className="panel-head"><div><p className="eyebrow">EVIDENCE REGISTER</p><h2>Recent evidence</h2></div><span className="count">{evidence.length} items</span></div>{evidence.length ? evidence.map(item => <button className={`evidence-row ${active?.id === item.id ? "active" : ""}`} onClick={() => choose(item)} key={item.id}><span className="file-icon"><FileCheck2 size={17}/></span><span className="row-copy"><b>{item.original_filename}</b><small>{item.evidence_type} · {item.file_size} bytes</small></span><span className={`risk ${item.analysis?.risk_level?.toLowerCase()}`}>{item.analysis?.risk_level || "PENDING"}</span></button>) : <div className="empty">No evidence yet. Upload a safe synthetic log to begin.</div>}</div>;
  let content: React.ReactNode = evidencePicker;
  if (view === "Dashboard") content = <><section className="metrics">{[["Total evidence", dashboard?.total_evidence ?? 0, "Captured artifacts"], ["Verified", dashboard?.verified_evidence ?? 0, "Proof matches"], ["Mismatches", dashboard?.integrity_mismatches ?? 0, "Requires review"], ["High risk", dashboard?.high_critical_risk ?? 0, "Analyst attention"]].map(([label, value, sub]) => <div className="metric" key={String(label)}><span>{label}</span><strong>{value}</strong><small>{sub}</small></div>)}</section><section className="workspace">{evidencePicker}{card("Security activity", <div className="empty">{timeline.length ? `${timeline.length} audit events for the selected evidence.` : "Select evidence to inspect its activity."}</div>)}</section></>;
  if (view === "Evidence") content = <section className="workspace">{evidencePicker}{card(active?.original_filename || "Evidence detail", active ? <><div className="hash-box"><div><span>SHA-256 fingerprint</span><code>{active.sha256_hash}</code></div><button title="Copy SHA-256" onClick={() => navigator.clipboard.writeText(active.sha256_hash)}><Copy size={16}/></button></div><p className="muted">{active.evidence_type} · {active.file_size} bytes · {new Date(active.created_at).toLocaleString()}</p><div className="actions"><button onClick={() => register().catch(error => setNotice(error.message))}><LockKeyhole size={16}/> Register proof</button><button className="secondary" onClick={() => verify().catch(error => setNotice(error.message))}><FileCheck2 size={16}/> Verify bytes</button></div></> : <div className="empty">Select evidence to inspect it.</div>)}</section>;
  if (view === "AI Analysis") content = card("AI-assisted analysis", active?.analysis ? <><div className="analysis-head"><span>{active.analysis.incident_category}</span><b>{active.analysis.risk_level} · {active.analysis.confidence}%</b></div><p>{active.analysis.summary}</p><div className="tags">{active.analysis.indicators.map(item => <span key={item}>{item}</span>)}</div><h3>Recommendations</h3><ul>{active.analysis.recommendations.map(item => <li key={item}>{item}</li>)}</ul></> : <div className="empty">Upload or select evidence to view analysis.</div>);
  if (view === "Blockchain Proofs") content = card("Blockchain proof", proof ? <><div className="hash-box"><div><span>Transaction hash</span><code>{proof.transaction_hash}</code></div></div><p>Network: {proof.network}</p><p>Contract: <code>{proof.contract_address}</code></p><p>Block: {proof.block_number}</p><p className="muted">Only the cryptographic proof is registered. Raw evidence remains off-chain.</p></> : <div className="empty">Select evidence and register its SHA-256 proof.</div>);
  if (view === "Verification") content = card("Verification result", verification ? <div className={`verification ${verification.result === "VERIFIED" ? "good" : "bad"}`}><strong>{verification.result === "VERIFIED" ? "✓ VERIFIED" : "⚠ INTEGRITY MISMATCH"}</strong><p>{verification.message}</p><div className="compare"><code>{verification.original_hash}</code><code>{verification.current_hash}</code></div></div> : <><div className="empty">No verification requested for the selected evidence.</div><button className="secondary" onClick={() => verify().catch(error => setNotice(error.message))}><FileCheck2 size={16}/> Verify current bytes</button></>);
  if (view === "Audit Timeline") content = card("Audit timeline", timeline.length ? <div className="timeline">{timeline.map(item => <div className="timeline-item" key={`${item.timestamp}-${item.event_type}`}><strong>{item.event_type}</strong><span>{new Date(item.timestamp).toLocaleString()}</span><p>{item.description}</p>{item.transaction_reference && <code>{item.transaction_reference}</code>}</div>)}</div> : <div className="empty">Select evidence to load its audit events.</div>);
  return <div className="shell"><aside><div className="brand"><div className="brand-mark"><Fingerprint size={22}/></div><div><strong>SecureProof</strong><span>Evidence integrity</span></div></div><nav>{nav.map(([Icon, label]) => <button className={view === label ? "active" : ""} onClick={() => setView(label)} key={label}><Icon size={17}/>{label}</button>)}</nav><div className="side-note"><LockKeyhole size={16}/><span>Evidence stays off-chain.<br/><b>Proof travels on-chain.</b></span></div></aside><main><header><div><p className="eyebrow">SECURITY OPERATIONS / EVIDENCE CONTROL</p><h1>{view === "Dashboard" ? "Integrity command center" : view}</h1><p className="muted">A clear chain from analyst intake to cryptographic verification.</p></div><label className="upload"><UploadCloud size={18}/> Upload evidence<input type="file" accept=".txt,.log,.json,.csv" onChange={e => e.target.files?.[0] && upload(e.target.files[0]).catch(error => setNotice(error.message))}/></label></header><div className="notice">{notice}</div>{content}</main></div>;
}
