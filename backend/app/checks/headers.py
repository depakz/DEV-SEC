"""HTTP security header check — a plain GET, same as any browser sends."""
from __future__ import annotations

from typing import Any

import httpx

REQUEST_TIMEOUT_SECONDS = 6.0

# header name -> (human label, why it matters)
SECURITY_HEADERS: dict[str, tuple[str, str]] = {
    "strict-transport-security": (
        "HSTS",
        "Without it, a browser can be tricked into visiting the site over plain HTTP first.",
    ),
    "content-security-policy": (
        "Content-Security-Policy",
        "Without it, an injected script (XSS) can load/run with no restriction.",
    ),
    "x-content-type-options": (
        "X-Content-Type-Options",
        "Without 'nosniff', browsers may execute a file as a different type than declared.",
    ),
    "x-frame-options": (
        "X-Frame-Options",
        "Without it, the site can be framed by an attacker page (clickjacking).",
    ),
    "referrer-policy": (
        "Referrer-Policy",
        "Without it, the full URL (sometimes containing tokens) may leak to third parties.",
    ),
}


def check_headers(domain: str) -> dict[str, Any]:
    url = f"https://{domain}"
    try:
        response = httpx.get(
            url,
            timeout=REQUEST_TIMEOUT_SECONDS,
            follow_redirects=True,
            headers={"User-Agent": "security-posture-scanner/1.0 (passive header check)"},
        )
    except httpx.HTTPError as exc:
        return {"reachable": False, "error": str(exc)}

    present_lower = {k.lower(): v for k, v in response.headers.items()}
    results = {}
    for header_key, (label, reason) in SECURITY_HEADERS.items():
        results[header_key] = {
            "label": label,
            "present": header_key in present_lower,
            "value": present_lower.get(header_key),
            "why_it_matters": reason,
        }

    return {
        "reachable": True,
        "status_code": response.status_code,
        "final_url": str(response.url),
        "headers": results,
        "missing_count": sum(1 for h in results.values() if not h["present"]),
    }
