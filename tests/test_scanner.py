from __future__ import annotations

from site_discovery.scanner import scan_urls


class DummyFetchResult:
    def __init__(
        self,
        *,
        normalized_url: str,
        ok: bool,
        status_code: int | None,
        error: str | None,
        html: str,
    ) -> None:
        self.normalized_url = normalized_url
        self.ok = ok
        self.status_code = status_code
        self.error = error
        self.html = html


class DummyFetcher:
    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout

    def fetch(self, url: str) -> DummyFetchResult:
        if "good" in url:
            return DummyFetchResult(
                normalized_url="https://good.example",
                ok=True,
                status_code=200,
                error=None,
                html=(
                    "<html><script src='https://www.googletagmanager.com/gtm.js'></script>"
                    "<script src='https://cdn.shopify.com/foo.js'></script>"
                    "<a href='https://www.awin1.com/?affid=123'>aff</a></html>"
                ),
            )
        return DummyFetchResult(
            normalized_url="https://bad.example",
            ok=False,
            status_code=503,
            error="HTTPError: Service Unavailable",
            html="",
        )


def test_scan_urls_detects_categories_for_reachable_sites(monkeypatch):
    monkeypatch.setattr("site_discovery.scanner.WebsiteFetcher", DummyFetcher)
    report = scan_urls(["good.example", "bad.example"])

    assert report["summary"] == {
        "total_websites": 2,
        "reachable_websites": 1,
        "unreachable_websites": 1,
    }
    first = report["results"][0]
    assert first["is_reachable"] is True
    assert "Google Tag Manager" in first["conversion_events"]
    assert "Shopify" in first["ecommerce_engines"]
    assert "Awin" in first["affiliate_programs"]

    second = report["results"][1]
    assert second["is_reachable"] is False
    assert second["conversion_events"] == []

