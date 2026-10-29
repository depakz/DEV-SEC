"""Stateless domain-ownership verification.

The service has no database, so we can't just store "user X proved they
own domain Y" in a row somewhere. Instead we make the *token itself* carry
everything needed to re-check that claim later, cryptographically signed
so a client can't forge or tamper with it.

Flow:
  1. POST /api/verify/start {domain}
         -> server mints a signed token bound to (domain, expiry) and
            hands it back, along with where to publish it.
  2. The user publishes that exact token in ONE of two places they
     control only if they own the domain:
         - a DNS TXT record at  _scanverify.<domain>
         - a file at           https://<domain>/.well-known/scanner-verification.txt
  3. POST /api/verify/check {domain, token}
         -> server re-derives the signature from (domain, expiry) baked
            into the token and compares it (constant-time) to the
            signature the client sent back. If that matches, the token
            is genuine and still fresh. The server THEN does a live
            lookup of the TXT record / well-known file and checks the
            token text is actually published there.
  4. POST /api/scan/ports {domain, token}
         -> re-runs step 3 in full before scanning a single port.
            Nothing from step 1-3 is cached, so this re-check is not
            a formality — it is the only thing standing between "you
            verified a minute ago" and "you still control this domain
            right now."

Why the signature matters at all, given there's no secret the client
needs to know: it stops someone from skipping step 1 and just inventing
a token (e.g. claiming a fake expiry far in the future, or a token meant
for domain A against domain B). Only the server's HMAC key can produce a
signature that step 3 will accept, so a token is only ever valid for the
exact domain and expiry the server originally issued it for.

The actual "proof of ownership" is step 2 + the live lookup in step 3:
publishing the token requires DNS or webserver control over the domain,
which is the thing we're actually trying to establish.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import time
from typing import Any

import dns.resolver
import httpx

TOKEN_TTL_SECONDS = 15 * 60  # 15 minutes to publish + verify
DNS_TIMEOUT_SECONDS = 5.0
HTTP_TIMEOUT_SECONDS = 6.0

# In production this comes from an env var (set via Terraform/Key Vault,
# never committed). A dev default is provided purely so local `pytest`
# and `uvicorn` runs work out of the box.
_SECRET = os.environ.get("SCANNER_HMAC_SECRET", "dev-only-secret-not-for-production").encode()


def _sign(domain: str, expires_at: int) -> str:
    message = f"{domain}|{expires_at}".encode()
    return hmac.new(_SECRET, message, hashlib.sha256).hexdigest()


def issue_token(domain: str) -> dict[str, Any]:
    expires_at = int(time.time()) + TOKEN_TTL_SECONDS
    signature = _sign(domain, expires_at)
    payload = f"{domain}|{expires_at}|{signature}".encode()
    token = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    return {
        "token": token,
        "expires_at": expires_at,
        "dns_record": {
            "type": "TXT",
            "name": f"_scanverify.{domain}",
            "value": f"scanverify={token}",
        },
        "file_record": {
            "url": f"https://{domain}/.well-known/scanner-verification.txt",
            "contents": token,
        },
    }


class TokenInvalid(ValueError):
    pass


def _decode_and_check_signature(domain: str, token: str) -> None:
    padded = token + "=" * (-len(token) % 4)
    try:
        payload = base64.urlsafe_b64decode(padded.encode()).decode()
        claimed_domain, expires_at_str, signature = payload.split("|", 2)
        expires_at = int(expires_at_str)
    except (ValueError, UnicodeDecodeError) as exc:
        raise TokenInvalid("token is malformed") from exc

    if claimed_domain != domain:
        raise TokenInvalid("token was not issued for this domain")

    if time.time() > expires_at:
        raise TokenInvalid("token has expired — request a new one")

    expected_signature = _sign(claimed_domain, expires_at)
    if not hmac.compare_digest(expected_signature, signature):
        raise TokenInvalid("token signature does not match — it was tampered with")


def _published_at_dns(domain: str, token: str) -> bool:
    resolver = dns.resolver.Resolver()
    resolver.timeout = DNS_TIMEOUT_SECONDS
    resolver.lifetime = DNS_TIMEOUT_SECONDS
    try:
        answers = resolver.resolve(f"_scanverify.{domain}", "TXT")
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.DNSException):
        return False
    for rec in answers:
        text = "".join(s.decode() if isinstance(s, bytes) else s for s in rec.strings)
        if text.strip() == f"scanverify={token}":
            return True
    return False


def _published_at_well_known(domain: str, token: str) -> bool:
    url = f"https://{domain}/.well-known/scanner-verification.txt"
    try:
        response = httpx.get(url, timeout=HTTP_TIMEOUT_SECONDS, follow_redirects=True)
    except httpx.HTTPError:
        return False
    return response.status_code == 200 and response.text.strip() == token


def verify_ownership(domain: str, token: str) -> dict[str, Any]:
    """Full re-check: signature validity + live lookup. No state is read
    or written anywhere — every call re-derives everything from scratch."""
    try:
        _decode_and_check_signature(domain, token)
    except TokenInvalid as exc:
        return {"verified": False, "reason": str(exc)}

    via_dns = _published_at_dns(domain, token)
    via_file = _published_at_well_known(domain, token)

    if via_dns or via_file:
        return {"verified": True, "method": "dns" if via_dns else "well-known-file"}
    return {
        "verified": False,
        "reason": "token signature is valid but it was not found published at the DNS "
        "TXT record or the well-known file yet",
    }
