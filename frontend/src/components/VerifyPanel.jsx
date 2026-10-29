import { useState } from "react";
import { verifyStart, verifyCheck, scanPorts } from "../api.js";
import ScoreBadge from "./ScoreBadge.jsx";

// Guides the user through proving domain ownership, then unlocks the
// active port scan. Nothing here is persisted: the token lives only in
// this component's state and disappears on refresh.
export default function VerifyPanel({ domain, onPortResult }) {
  const [step, setStep] = useState("idle"); // idle -> issued -> verified
  const [tokenInfo, setTokenInfo] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);
  const [portResult, setPortResult] = useState(null);

  async function handleStart() {
    setBusy(true);
    setError(null);
    try {
      const data = await verifyStart(domain);
      setTokenInfo(data);
      setStep("issued");
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleCheck() {
    setBusy(true);
    setError(null);
    try {
      const data = await verifyCheck(domain, tokenInfo.token);
      if (data.verified) {
        setStep("verified");
      } else {
        setError(data.reason || "Not verified yet — give DNS a minute to propagate.");
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function handlePortScan() {
    setBusy(true);
    setError(null);
    try {
      const data = await scanPorts(domain, tokenInfo.token);
      setPortResult(data);
      onPortResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="verify-panel">
      <h2>Unlock port scan (requires ownership proof)</h2>
      <p className="muted">
        Port scanning only runs on domains you can prove you control. Pick either method below.
      </p>

      {step === "idle" && (
        <button onClick={handleStart} disabled={busy}>
          {busy ? "Requesting…" : "Get verification token"}
        </button>
      )}

      {tokenInfo && step !== "verified" && (
        <div className="verify-instructions">
          <p>Publish this token using <strong>either</strong> option, then click "Check now":</p>
          <div className="instruction-block">
            <strong>Option A — DNS TXT record</strong>
            <code>{tokenInfo.dns_record.name}  TXT  "{tokenInfo.dns_record.value}"</code>
          </div>
          <div className="instruction-block">
            <strong>Option B — file on your webserver</strong>
            <code>{tokenInfo.file_record.url}</code>
            <p>containing exactly: <code>{tokenInfo.file_record.contents}</code></p>
          </div>
          <button onClick={handleCheck} disabled={busy}>
            {busy ? "Checking…" : "Check now"}
          </button>
        </div>
      )}

      {step === "verified" && !portResult && (
        <div>
          <p className="pass">✓ Ownership verified. You can now run the port scan.</p>
          <button onClick={handlePortScan} disabled={busy}>
            {busy ? "Scanning ports…" : "Run port scan"}
          </button>
        </div>
      )}

      {portResult && (
        <div className="results-card">
          <header className="results-header">
            <h3>Open ports</h3>
            <ScoreBadge score={portResult.summary.score} grade={portResult.summary.grade} />
          </header>
          {portResult.ports.open_ports.length === 0 ? (
            <p>No ports open from the checked list.</p>
          ) : (
            <ul>
              {portResult.ports.open_ports.map((p) => (
                <li key={p.port} className={p.unexpected ? "fail" : "pass"}>
                  {p.port} ({p.service}) {p.unexpected ? "— unexpected" : ""}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {error && <p className="error-text">{error}</p>}
    </section>
  );
}
