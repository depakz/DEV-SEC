import { useState } from "react";
import { scanPorts } from "../api.js";
import ScoreBadge from "./ScoreBadge.jsx";

// Runs the active port scan. Nothing here is persisted: the result lives
// only in this component's state and disappears on refresh.
export default function PortScanPanel({ domain, onPortResult }) {
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);
  const [portResult, setPortResult] = useState(null);

  async function handlePortScan() {
    setBusy(true);
    setError(null);
    try {
      const data = await scanPorts(domain);
      setPortResult(data);
      onPortResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="port-panel">
      <h2>Port scan</h2>
      <p className="muted">Only scan domains you are authorized to test.</p>

      {!portResult && (
        <button onClick={handlePortScan} disabled={busy}>
          {busy ? "Scanning ports…" : "Run port scan"}
        </button>
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
