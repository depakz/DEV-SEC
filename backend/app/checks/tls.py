"""TLS certificate check: expiry, issuer, protocol — all public info any
browser already reads when it visits the site over HTTPS."""
from __future__ import annotations

import datetime as dt
import socket
import ssl
from typing import Any

CERT_TIMEOUT_SECONDS = 5


def check_tls(domain: str, port: int = 443) -> dict[str, Any]:
    context = ssl.create_default_context()
    try:
        with socket.create_connection((domain, port), timeout=CERT_TIMEOUT_SECONDS) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as tls_sock:
                cert = tls_sock.getpeercert()
                protocol = tls_sock.version()
    except (socket.timeout, OSError, ssl.SSLError) as exc:
        return {"reachable": False, "error": str(exc)}

    not_after = dt.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(
        tzinfo=dt.timezone.utc
    )
    days_remaining = (not_after - dt.datetime.now(dt.timezone.utc)).days
    issuer = dict(x[0] for x in cert.get("issuer", []))

    return {
        "reachable": True,
        "protocol": protocol,
        "issuer": issuer.get("organizationName", "unknown"),
        "expires_at": not_after.isoformat(),
        "days_until_expiry": days_remaining,
        "expired": days_remaining < 0,
        "expiring_soon": 0 <= days_remaining <= 14,
    }
