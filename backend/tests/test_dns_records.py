import dns.resolver
import pytest

from app.checks.dns_records import check_dns


class _FakeTXT:
    def __init__(self, text: str):
        self.strings = [text.encode()]


class _FakeMX:
    def __init__(self, host: str):
        self.exchange = host + "."


def _patch_resolve(monkeypatch, routes: dict):
    def fake_resolve(self, qname, rdtype):
        key = (qname, rdtype)
        if key not in routes:
            raise dns.resolver.NXDOMAIN()
        return routes[key]

    monkeypatch.setattr(dns.resolver.Resolver, "resolve", fake_resolve)


def test_full_hygiene_present(monkeypatch):
    routes = {
        ("good.example", "TXT"): [_FakeTXT("v=spf1 include:_spf.example.com ~all")],
        ("_dmarc.good.example", "TXT"): [_FakeTXT("v=DMARC1; p=reject;")],
        ("good.example", "MX"): [_FakeMX("mail.good.example")],
    }
    _patch_resolve(monkeypatch, routes)
    result = check_dns("good.example")
    assert result["spf"]["present"] is True
    assert result["dmarc"]["present"] is True
    assert result["dmarc"]["policy"] == "reject"
    assert result["dmarc"]["policy_is_weak"] is False
    assert result["mx"]["present"] is True


def test_weak_dmarc_policy_flagged(monkeypatch):
    routes = {
        ("good.example", "TXT"): [],
        ("_dmarc.good.example", "TXT"): [_FakeTXT("v=DMARC1; p=none;")],
        ("good.example", "MX"): [],
    }
    _patch_resolve(monkeypatch, routes)
    result = check_dns("good.example")
    assert result["dmarc"]["policy"] == "none"
    assert result["dmarc"]["policy_is_weak"] is True


def test_missing_records_reported_absent(monkeypatch):
    _patch_resolve(monkeypatch, {})
    result = check_dns("nothing.example")
    assert result["spf"]["present"] is False
    assert result["dmarc"]["present"] is False
    assert result["mx"]["present"] is False
