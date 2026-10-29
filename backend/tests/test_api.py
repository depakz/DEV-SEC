from fastapi.testclient import TestClient

import app.main as main_mod
from app.main import app


def test_health():
    client = TestClient(app)
    assert client.get("/api/health").json() == {"status": "ok"}


def test_scan_passive_rejects_invalid_domain():
    client = TestClient(app)
    resp = client.post("/api/scan/passive", json={"domain": "not a domain"})
    assert resp.status_code == 400


def test_scan_passive_rejects_private_ip_target(monkeypatch):
    monkeypatch.setattr(
        "socket.getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("127.0.0.1", 0))]
    )
    client = TestClient(app)
    resp = client.post("/api/scan/passive", json={"domain": "internal.example"})
    assert resp.status_code == 400
    assert "public address" in resp.json()["detail"]


def test_port_scan_blocked_without_verification(monkeypatch):
    monkeypatch.setattr(
        "socket.getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("93.184.216.34", 0))]
    )
    monkeypatch.setattr(main_mod, "verify_ownership", lambda d, t: {"verified": False, "reason": "nope"})
    client = TestClient(app)
    resp = client.post("/api/scan/ports", json={"domain": "example.com", "token": "whatever"})
    assert resp.status_code == 403
    assert "nope" in resp.json()["detail"]


def test_port_scan_allowed_after_verification(monkeypatch):
    monkeypatch.setattr(
        "socket.getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("93.184.216.34", 0))]
    )
    monkeypatch.setattr(main_mod, "verify_ownership", lambda d, t: {"verified": True, "method": "dns"})
    monkeypatch.setattr(main_mod, "check_ports", lambda ip: {"scanned_ports": [], "open_ports": [], "unexpected_open_count": 0})
    client = TestClient(app)
    resp = client.post("/api/scan/ports", json={"domain": "example.com", "token": "whatever"})
    assert resp.status_code == 200
    assert resp.json()["summary"]["grade"] == "A"


def test_verify_start_returns_dns_and_file_instructions():
    client = TestClient(app)
    resp = client.post("/api/verify/start", json={"domain": "example.com"})
    body = resp.json()
    assert body["dns_record"]["name"] == "_scanverify.example.com"
    assert body["file_record"]["url"].endswith("/.well-known/scanner-verification.txt")
