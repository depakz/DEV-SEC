from app.checks import ports


def test_only_expected_ports_open(monkeypatch):
    monkeypatch.setattr(ports, "_probe", lambda ip, port: port in ports.EXPECTED_OPEN)
    result = ports.check_ports("93.184.216.34")
    assert result["unexpected_open_count"] == 0
    assert {p["port"] for p in result["open_ports"]} == ports.EXPECTED_OPEN


def test_unexpected_open_port_is_flagged(monkeypatch):
    monkeypatch.setattr(ports, "_probe", lambda ip, port: port in (443, 3389))
    result = ports.check_ports("93.184.216.34")
    assert result["unexpected_open_count"] == 1
    flagged = [p for p in result["open_ports"] if p["unexpected"]]
    assert flagged[0]["service"] == "RDP"


def test_no_ports_open(monkeypatch):
    monkeypatch.setattr(ports, "_probe", lambda ip, port: False)
    result = ports.check_ports("93.184.216.34")
    assert result["open_ports"] == []
