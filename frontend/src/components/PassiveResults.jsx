import ScoreBadge from "./ScoreBadge.jsx";

export default function PassiveResults({ result }) {
  const { tls, headers, dns, summary } = result;

  return (
    <section className="results-card">
      <header className="results-header">
        <h2>Passive checks — {result.domain}</h2>
        <ScoreBadge score={summary.score} grade={summary.grade} />
      </header>

      {summary.findings.length > 0 && (
        <ul className="findings">
          {summary.findings.map((f) => (
            <li key={f}>{f}</li>
          ))}
        </ul>
      )}

      <div className="checks-grid">
        <div className="check-block">
          <h3>TLS Certificate</h3>
          {tls.reachable ? (
            <ul>
              <li>Protocol: {tls.protocol}</li>
              <li>Issuer: {tls.issuer}</li>
              <li>Expires: {new Date(tls.expires_at).toLocaleDateString()}</li>
              <li>Days remaining: {tls.days_until_expiry}</li>
            </ul>
          ) : (
            <p className="error-text">Not reachable over HTTPS: {tls.error}</p>
          )}
        </div>

        <div className="check-block">
          <h3>Security Headers</h3>
          {headers.reachable ? (
            <ul>
              {Object.entries(headers.headers).map(([key, h]) => (
                <li key={key} className={h.present ? "pass" : "fail"} title={h.why_it_matters}>
                  {h.present ? "✓" : "✗"} {h.label}
                </li>
              ))}
            </ul>
          ) : (
            <p className="error-text">Could not fetch headers: {headers.error}</p>
          )}
        </div>

        <div className="check-block">
          <h3>Email / DNS Hygiene</h3>
          <ul>
            <li className={dns.spf.present ? "pass" : "fail"}>
              {dns.spf.present ? "✓" : "✗"} SPF
            </li>
            <li className={dns.dmarc.present ? "pass" : "fail"}>
              {dns.dmarc.present ? "✓" : "✗"} DMARC
              {dns.dmarc.present && ` (policy: ${dns.dmarc.policy})`}
            </li>
            <li className={dns.mx.present ? "pass" : "fail"}>
              {dns.mx.present ? "✓" : "✗"} MX records
            </li>
          </ul>
        </div>
      </div>
    </section>
  );
}
