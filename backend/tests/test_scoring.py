from app.scoring import score_passive, score_ports


def test_perfect_passive_scores_100():
    tls = {"reachable": True, "expired": False, "expiring_soon": False}
    headers = {"reachable": True, "missing_count": 0}
    dns = {"spf": {"present": True}, "dmarc": {"present": True, "policy_is_weak": False}}
    result = score_passive(tls, headers, dns)
    assert result["score"] == 100
    assert result["grade"] == "A"
    assert result["findings"] == []


def test_expired_cert_is_penalized_and_flagged():
    tls = {"reachable": True, "expired": True, "expiring_soon": False}
    headers = {"reachable": True, "missing_count": 0}
    dns = {"spf": {"present": True}, "dmarc": {"present": True, "policy_is_weak": False}}
    result = score_passive(tls, headers, dns)
    assert result["score"] == 75
    assert any("expired" in f for f in result["findings"])


def test_score_never_goes_below_zero():
    tls = {"reachable": False}
    headers = {"reachable": False}
    dns = {"spf": {"present": False}, "dmarc": {"present": False}}
    result = score_passive(tls, headers, dns)
    assert result["score"] >= 0


def test_ports_perfect_when_only_expected_open():
    port_result = {
        "open_ports": [{"port": 443, "service": "HTTPS", "unexpected": False}],
        "unexpected_open_count": 0,
    }
    result = score_ports(port_result)
    assert result["score"] == 100
    assert result["grade"] == "A"


def test_ports_penalized_for_unexpected_open_port():
    port_result = {
        "open_ports": [{"port": 3389, "service": "RDP", "unexpected": True}],
        "unexpected_open_count": 1,
    }
    result = score_ports(port_result)
    assert result["score"] == 80
    assert "RDP" in result["findings"][0]
