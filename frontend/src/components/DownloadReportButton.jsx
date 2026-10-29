// Builds the report entirely client-side from whatever is already in
// React state, then triggers a browser download. The server never sees
// this assembled object — it only ever answered individual check requests.
export default function DownloadReportButton({ passiveResult, portResult }) {
  function handleDownload() {
    const report = {
      generated_at: new Date().toISOString(),
      domain: passiveResult.domain,
      passive: {
        tls: passiveResult.tls,
        headers: passiveResult.headers,
        dns: passiveResult.dns,
        summary: passiveResult.summary,
      },
      ports: portResult ? { ports: portResult.ports, summary: portResult.summary } : null,
    };
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${passiveResult.domain}-security-report.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return <button onClick={handleDownload}>Download JSON report</button>;
}
