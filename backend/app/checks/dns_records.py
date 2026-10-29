"""DNS hygiene check: SPF / DMARC / MX — all public DNS, same as `dig`."""
from __future__ import annotations

from typing import Any

import dns.resolver

DNS_TIMEOUT_SECONDS = 5.0


def _query_txt(name: str) -> list[str]:
    resolver = dns.resolver.Resolver()
    resolver.timeout = DNS_TIMEOUT_SECONDS
    resolver.lifetime = DNS_TIMEOUT_SECONDS
    try:
        answers = resolver.resolve(name, "TXT")
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.DNSException):
        return []
    # TXT records can arrive split into multiple quoted strings; join them.
    return ["".join(s.decode() if isinstance(s, bytes) else s for s in rec.strings) for rec in answers]


def check_dns(domain: str) -> dict[str, Any]:
    spf_records = [r for r in _query_txt(domain) if r.lower().startswith("v=spf1")]
    dmarc_records = [r for r in _query_txt(f"_dmarc.{domain}") if r.lower().startswith("v=dmarc1")]

    resolver = dns.resolver.Resolver()
    resolver.timeout = DNS_TIMEOUT_SECONDS
    resolver.lifetime = DNS_TIMEOUT_SECONDS
    try:
        mx_records = [str(r.exchange).rstrip(".") for r in resolver.resolve(domain, "MX")]
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.DNSException):
        mx_records = []

    dmarc_policy = None
    if dmarc_records:
        for part in dmarc_records[0].split(";"):
            part = part.strip()
            if part.lower().startswith("p="):
                dmarc_policy = part.split("=", 1)[1]

    return {
        "spf": {"present": bool(spf_records), "record": spf_records[0] if spf_records else None},
        "dmarc": {
            "present": bool(dmarc_records),
            "record": dmarc_records[0] if dmarc_records else None,
            "policy": dmarc_policy,
            "policy_is_weak": dmarc_policy in (None, "none"),
        },
        "mx": {"present": bool(mx_records), "records": mx_records},
    }
