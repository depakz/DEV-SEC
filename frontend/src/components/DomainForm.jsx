import { useState } from "react";

export default function DomainForm({ onSubmit, loading }) {
  const [domain, setDomain] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (domain.trim()) onSubmit(domain.trim());
  }

  return (
    <form className="domain-form" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="example.com"
        value={domain}
        onChange={(e) => setDomain(e.target.value)}
        aria-label="Domain to scan"
      />
      <button type="submit" disabled={loading || !domain.trim()}>
        {loading ? "Scanning…" : "Scan"}
      </button>
    </form>
  );
}
