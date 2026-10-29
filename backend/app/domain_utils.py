"""Shared domain validation/safety helpers.

Every check in this service eventually opens a socket or sends an HTTP
request to whatever the client typed into the "domain" box. Without the
checks below, the scanner itself becomes an SSRF (server-side request
forgery) tool: someone could ask it to "scan" 127.0.0.1, 169.254.169.254
(the cloud metadata endpoint), or a private 10.x address on the box it
runs on. Both the passive and active check modules import this before
doing any network I/O.
"""
from __future__ import annotations

import ipaddress
import re
import socket

_HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
    r"(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))+$"
)


class InvalidDomainError(ValueError):
    """Raised when a submitted domain fails syntax or safety checks."""


def normalize_domain(raw: str) -> str:
    """Strip scheme/path/port and lower-case, returning a bare hostname."""
    value = raw.strip().lower()
    value = re.sub(r"^https?://", "", value)
    value = value.split("/")[0]
    value = value.split(":")[0]
    if not value or not _HOSTNAME_RE.match(value):
        raise InvalidDomainError(f"'{raw}' is not a syntactically valid hostname")
    return value


def assert_publicly_routable(domain: str) -> list[str]:
    """Resolve `domain` and reject it if any address is non-public.

    Returns the list of resolved IPs on success. Blocks loopback, private,
    link-local (including the 169.254.169.254 cloud metadata address),
    multicast and reserved ranges.
    """
    try:
        infos = socket.getaddrinfo(domain, None)
    except socket.gaierror as exc:
        raise InvalidDomainError(f"could not resolve '{domain}': {exc}") from exc

    ips = sorted({info[4][0] for info in infos})
    if not ips:
        raise InvalidDomainError(f"'{domain}' did not resolve to any address")

    for ip_str in ips:
        ip = ipaddress.ip_address(ip_str)
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            raise InvalidDomainError(
                f"'{domain}' resolves to {ip}, which is not a public address"
            )
    return ips


def validate_domain(raw: str) -> tuple[str, list[str]]:
    """Normalize + resolve + safety-check in one call. Returns (domain, ips)."""
    domain = normalize_domain(raw)
    ips = assert_publicly_routable(domain)
    return domain, ips
