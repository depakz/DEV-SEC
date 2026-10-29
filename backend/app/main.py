"""Security Posture Scanner — API.

Stateless by design: nothing submitted here is written to a database,
a file, or a cache. Each request is handled and forgotten. The frontend
assembles the final report client-side from these responses and offers
it as a JSON download — the server never sees the assembled report.
"""
from __future__ import annotations

import asyncio
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.checks.dns_records import check_dns
from app.checks.headers import check_headers
from app.checks.ports import check_ports
from app.checks.tls import check_tls
from app.domain_utils import InvalidDomainError, validate_domain
from app.schemas import DomainRequest, PortScanRequest, VerifyCheckRequest
from app.scoring import score_passive, score_ports
from app.verify import issue_token, verify_ownership

app = FastAPI(
    title="Security Posture Scanner",
    description="Stateless passive + (verified) active security posture checks.",
    version="1.0.0",
)

allowed_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/scan/passive")
async def scan_passive(body: DomainRequest) -> dict:
    """TLS, header and DNS checks — public info, no ownership proof needed."""
    try:
        domain, _ips = validate_domain(body.domain)
    except InvalidDomainError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    tls_result, headers_result, dns_result = await asyncio.gather(
        asyncio.to_thread(check_tls, domain),
        asyncio.to_thread(check_headers, domain),
        asyncio.to_thread(check_dns, domain),
    )
    summary = score_passive(tls_result, headers_result, dns_result)

    return {
        "domain": domain,
        "tls": tls_result,
        "headers": headers_result,
        "dns": dns_result,
        "summary": summary,
    }


@app.post("/api/verify/start")
def verify_start(body: DomainRequest) -> dict:
    """Issue a signed, stateless verification token for this domain."""
    try:
        domain, _ips = validate_domain(body.domain)
    except InvalidDomainError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"domain": domain, **issue_token(domain)}


@app.post("/api/verify/check")
def verify_check(body: VerifyCheckRequest) -> dict:
    """Re-validate token signature + live DNS/file lookup. No state stored."""
    try:
        domain, _ips = validate_domain(body.domain)
    except InvalidDomainError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"domain": domain, **verify_ownership(domain, body.token)}


@app.post("/api/scan/ports")
def scan_ports(body: PortScanRequest) -> dict:
    """Active port check — gated behind a fresh ownership re-check."""
    try:
        domain, ips = validate_domain(body.domain)
    except InvalidDomainError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    verification = verify_ownership(domain, body.token)
    if not verification.get("verified"):
        raise HTTPException(
            status_code=403,
            detail=f"Ownership not verified: {verification.get('reason', 'unknown')}",
        )

    port_result = check_ports(ips[0])
    summary = score_ports(port_result)
    return {"domain": domain, "ports": port_result, "summary": summary}
