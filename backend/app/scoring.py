"""Turns raw check output into a single score + letter grade."""
from __future__ import annotations

from typing import Any

MAX_SCORE = 100


def score_passive(tls: dict[str, Any], headers: dict[str, Any], dns: dict[str, Any]) -> dict[str, Any]:
    score = MAX_SCORE
    findings: list[str] = []

    if not tls.get("reachable"):
        score -= 30
        findings.append("Site did not respond over HTTPS.")
    else:
        if tls.get("expired"):
            score -= 25
            findings.append("TLS certificate has expired.")
        elif tls.get("expiring_soon"):
            score -= 10
            findings.append("TLS certificate expires within 14 days.")

    if headers.get("reachable"):
        missing = headers.get("missing_count", 0)
        score -= missing * 6
        if missing:
            findings.append(f"{missing} recommended security header(s) missing.")
    else:
        score -= 15
        findings.append("Could not fetch HTTP headers.")

    if not dns.get("spf", {}).get("present"):
        score -= 8
        findings.append("No SPF record — email spoofing is easier.")
    if not dns.get("dmarc", {}).get("present"):
        score -= 8
        findings.append("No DMARC record — spoofed mail won't be reported/rejected.")
    elif dns.get("dmarc", {}).get("policy_is_weak"):
        score -= 4
        findings.append("DMARC policy is 'none' — monitoring only, no enforcement.")

    score = max(0, min(MAX_SCORE, score))
    return {"score": score, "grade": _grade(score), "findings": findings}


def score_ports(port_result: dict[str, Any]) -> dict[str, Any]:
    unexpected = port_result.get("unexpected_open_count", 0)
    score = max(0, MAX_SCORE - unexpected * 20)
    findings = []
    if unexpected:
        names = [p["service"] for p in port_result["open_ports"] if p["unexpected"]]
        findings.append(f"Unexpected open port(s): {', '.join(names)}.")
    return {"score": score, "grade": _grade(score), "findings": findings}


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"
