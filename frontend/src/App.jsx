import { useState } from "react";
import DomainForm from "./components/DomainForm.jsx";
import PassiveResults from "./components/PassiveResults.jsx";
import VerifyPanel from "./components/VerifyPanel.jsx";
import DownloadReportButton from "./components/DownloadReportButton.jsx";
import { scanPassive } from "./api.js";

// No login, no database, no localStorage. Everything lives in this
// component's state and is gone the moment the tab is closed or refreshed.
export default function App() {
  const [passiveResult, setPassiveResult] = useState(null);
  const [portResult, setPortResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleScan(domain) {
    setLoading(true);
    setError(null);
    setPassiveResult(null);
    setPortResult(null);
    try {
      const data = await scanPassive(domain);
      setPassiveResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <h1>Security Posture Scanner</h1>
      <p className="muted">
        Stateless — nothing you scan here is saved. Enter any public domain for the
        passive checks; port scanning requires proving you own it.
      </p>

      <DomainForm onSubmit={handleScan} loading={loading} />
      {error && <p className="error-text">{error}</p>}

      {passiveResult && (
        <>
          <PassiveResults result={passiveResult} />
          <VerifyPanel domain={passiveResult.domain} onPortResult={setPortResult} />
          <DownloadReportButton passiveResult={passiveResult} portResult={portResult} />
        </>
      )}
    </main>
  );
}
