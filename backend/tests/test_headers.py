import httpx
import respx

from app.checks.headers import check_headers


@respx.mock
def test_detects_all_headers_present():
    respx.get("https://good.example").mock(
        return_value=httpx.Response(
            200,
            headers={
                "Strict-Transport-Security": "max-age=63072000",
                "Content-Security-Policy": "default-src 'self'",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "Referrer-Policy": "no-referrer",
            },
        )
    )
    result = check_headers("good.example")
    assert result["reachable"] is True
    assert result["missing_count"] == 0


@respx.mock
def test_detects_missing_headers():
    respx.get("https://bad.example").mock(return_value=httpx.Response(200, headers={}))
    result = check_headers("bad.example")
    assert result["missing_count"] == len(result["headers"])
    assert all(not h["present"] for h in result["headers"].values())


@respx.mock
def test_unreachable_site_reports_error():
    respx.get("https://down.example").mock(side_effect=httpx.ConnectError("refused"))
    result = check_headers("down.example")
    assert result["reachable"] is False
    assert "error" in result
