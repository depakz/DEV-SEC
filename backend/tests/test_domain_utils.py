import pytest

from app.domain_utils import InvalidDomainError, assert_publicly_routable, normalize_domain


def test_normalize_strips_scheme_and_path():
    assert normalize_domain("https://Example.com/path?x=1") == "example.com"


def test_normalize_strips_port():
    assert normalize_domain("example.com:8080") == "example.com"


@pytest.mark.parametrize("bad", ["", "not a domain", "-bad.com", "a" * 300 + ".com"])
def test_normalize_rejects_invalid_syntax(bad):
    with pytest.raises(InvalidDomainError):
        normalize_domain(bad)


def test_rejects_loopback(monkeypatch):
    monkeypatch.setattr(
        "socket.getaddrinfo",
        lambda *a, **k: [(2, 1, 6, "", ("127.0.0.1", 0))],
    )
    with pytest.raises(InvalidDomainError):
        assert_publicly_routable("localhost")


def test_rejects_cloud_metadata_ip(monkeypatch):
    monkeypatch.setattr(
        "socket.getaddrinfo",
        lambda *a, **k: [(2, 1, 6, "", ("169.254.169.254", 0))],
    )
    with pytest.raises(InvalidDomainError):
        assert_publicly_routable("metadata.internal")


def test_accepts_public_ip(monkeypatch):
    monkeypatch.setattr(
        "socket.getaddrinfo",
        lambda *a, **k: [(2, 1, 6, "", ("93.184.216.34", 0))],
    )
    assert assert_publicly_routable("example.com") == ["93.184.216.34"]


def test_accepts_nat64_wrapped_public_ip(monkeypatch):
    monkeypatch.setattr(
        "socket.getaddrinfo",
        lambda *a, **k: [(10, 1, 6, "", ("64:ff9b::d818:3901", 0, 0, 0))],
    )
    assert assert_publicly_routable("torkq.com") == ["64:ff9b::d818:3901"]


@pytest.mark.parametrize("wrapped", ["64:ff9b::7f00:1", "64:ff9b::a9fe:a9fe", "::ffff:10.0.0.1"])
def test_rejects_nat64_wrapped_private_ip(monkeypatch, wrapped):
    monkeypatch.setattr(
        "socket.getaddrinfo",
        lambda *a, **k: [(10, 1, 6, "", (wrapped, 0, 0, 0))],
    )
    with pytest.raises(InvalidDomainError):
        assert_publicly_routable("evil.example")
