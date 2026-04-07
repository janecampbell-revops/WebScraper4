from __future__ import annotations

from site_discovery.simple_scraper import extract_page_data, scrape_url


def test_extract_page_data_collects_title_and_links() -> None:
    html = """
    <html>
      <head><title>Example Site</title></head>
      <body>
        <a href="/about">About</a>
        <a href="https://other.example/contact">Contact</a>
      </body>
    </html>
    """
    data = extract_page_data(html, base_url="https://example.com", max_links=10)
    assert data["title"] == "Example Site"
    assert data["link_count"] == 2
    assert data["links"][0] == "https://example.com/about"
    assert data["links"][1] == "https://other.example/contact"


class DummyFetchResult:
    def __init__(
        self,
        *,
        normalized_url: str,
        final_url: str | None,
        reachable: bool,
        ok: bool,
        status_code: int | None,
        error: str | None,
        html: str,
    ) -> None:
        self.normalized_url = normalized_url
        self.final_url = final_url
        self.reachable = reachable
        self.ok = ok
        self.status_code = status_code
        self.error = error
        self.html = html


class DummyFetcher:
    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout

    def fetch(self, url: str) -> DummyFetchResult:
        if "up" in url:
            return DummyFetchResult(
                normalized_url="https://up.example",
                final_url="https://up.example/home",
                reachable=True,
                ok=True,
                status_code=200,
                error=None,
                html=(
                    "<html><head><title>Up</title></head><body>"
                    "<a href='/one'>one</a><a href='/two'>two</a>"
                    "</body></html>"
                ),
            )
        return DummyFetchResult(
            normalized_url="https://down.example",
            final_url=None,
            reachable=False,
            ok=False,
            status_code=None,
            error="URLError: timed out",
            html="",
        )


def test_scrape_url_handles_success(monkeypatch) -> None:
    monkeypatch.setattr("site_discovery.simple_scraper.WebsiteFetcher", DummyFetcher)
    payload = scrape_url("up.example", max_links=1)
    assert payload["is_reachable"] is True
    assert payload["status_code"] == 200
    assert payload["title"] == "Up"
    assert payload["link_count"] == 1
    assert payload["links"] == ["https://up.example/one"]


def test_scrape_url_handles_unreachable(monkeypatch) -> None:
    monkeypatch.setattr("site_discovery.simple_scraper.WebsiteFetcher", DummyFetcher)
    payload = scrape_url("down.example")
    assert payload["is_reachable"] is False
    assert payload["title"] is None
    assert payload["links"] == []
    assert payload["error"] == "URLError: timed out"
