import time

from app.verify import issue_token, verify_ownership, _sign, _decode_and_check_signature, TokenInvalid
import app.verify as verify_mod
import pytest


def test_issue_token_contains_dns_and_file_instructions():
    result = issue_token("example.com")
    assert result["dns_record"]["name"] == "_scanverify.example.com"
    assert result["token"] in result["dns_record"]["value"]
    assert result["file_record"]["contents"] == result["token"]


def test_signature_rejects_tampered_domain():
    issued = issue_token("example.com")
    with pytest.raises(TokenInvalid):
        _decode_and_check_signature("not-example.com", issued["token"])


def test_signature_rejects_expired_token(monkeypatch):
    issued = issue_token("example.com")
    # fast-forward time past the TTL
    monkeypatch.setattr(time, "time", lambda: issued["expires_at"] + 10)
    with pytest.raises(TokenInvalid):
        _decode_and_check_signature("example.com", issued["token"])


def test_verify_ownership_fails_without_publication(monkeypatch):
    issued = issue_token("example.com")
    monkeypatch.setattr(verify_mod, "_published_at_dns", lambda d, t: False)
    monkeypatch.setattr(verify_mod, "_published_at_well_known", lambda d, t: False)
    result = verify_ownership("example.com", issued["token"])
    assert result["verified"] is False


def test_verify_ownership_succeeds_via_dns(monkeypatch):
    issued = issue_token("example.com")
    monkeypatch.setattr(verify_mod, "_published_at_dns", lambda d, t: True)
    monkeypatch.setattr(verify_mod, "_published_at_well_known", lambda d, t: False)
    result = verify_ownership("example.com", issued["token"])
    assert result == {"verified": True, "method": "dns"}


def test_verify_ownership_succeeds_via_well_known_file(monkeypatch):
    issued = issue_token("example.com")
    monkeypatch.setattr(verify_mod, "_published_at_dns", lambda d, t: False)
    monkeypatch.setattr(verify_mod, "_published_at_well_known", lambda d, t: True)
    result = verify_ownership("example.com", issued["token"])
    assert result == {"verified": True, "method": "well-known-file"}


def test_token_cannot_be_reused_for_a_different_domain(monkeypatch):
    issued = issue_token("example.com")
    monkeypatch.setattr(verify_mod, "_published_at_dns", lambda d, t: True)
    monkeypatch.setattr(verify_mod, "_published_at_well_known", lambda d, t: True)
    result = verify_ownership("evil.com", issued["token"])
    assert result["verified"] is False
