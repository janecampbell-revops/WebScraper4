from __future__ import annotations

import socket
import ssl
from dataclasses import dataclass
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (compatible; WebsiteDiscoveryBot/1.0; +https://example.invalid/bot)"
)


@dataclass(slots=True)
class FetchResult:
    input_url: str
    normalized_url: str
    final_url: str | None
    reachable: bool
    ok: bool
    status_code: Optional[int]
    error: Optional[str]
    html: str


def normalize_url(url: str) -> str:
    candidate = url.strip()
    if not candidate:
        return candidate
    parsed = urlparse(candidate)
    if parsed.scheme:
        return candidate
    return f"https://{candidate}"


class WebsiteFetcher:
    def __init__(self, timeout: float = 10.0, user_agent: str | None = None) -> None:
        self.timeout = timeout
        self.user_agent = user_agent or DEFAULT_USER_AGENT

    def fetch(self, url: str) -> FetchResult:
        normalized = normalize_url(url)
        if not normalized:
            return FetchResult(
                input_url=url,
                normalized_url="",
                final_url=None,
                reachable=False,
                ok=False,
                status_code=None,
                error="Empty URL",
                html="",
            )

        request = Request(
            normalized,
            headers={
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml",
            },
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                status_code = response.getcode()
                final_url = response.geturl()
                content_type = response.headers.get("Content-Type", "")
                content_bytes = response.read()
                encoding = response.headers.get_content_charset() or "utf-8"
                html = content_bytes.decode(encoding, errors="replace")
                if "html" not in content_type.lower() and "<html" not in html.lower():
                    html = ""

                is_ok = status_code is not None and 200 <= status_code < 400
                return FetchResult(
                    input_url=url,
                    normalized_url=normalized,
                    final_url=final_url,
                    reachable=True,
                    ok=is_ok,
                    status_code=status_code,
                    error=None,
                    html=html,
                )
        except HTTPError as exc:
            html = ""
            try:
                body = exc.read()
                encoding = (
                    exc.headers.get_content_charset()
                    if exc.headers is not None
                    else "utf-8"
                ) or "utf-8"
                html = body.decode(encoding, errors="replace")
            except Exception:
                html = ""

            return FetchResult(
                input_url=url,
                normalized_url=normalized,
                final_url=normalized,
                reachable=True,
                ok=False,
                status_code=exc.code,
                error=f"HTTPError: {exc.reason}",
                html=html,
            )
        except (URLError, socket.timeout, ssl.SSLError, ValueError, OSError) as exc:
            return FetchResult(
                input_url=url,
                normalized_url=normalized,
                final_url=None,
                reachable=False,
                ok=False,
                status_code=None,
                error=f"{type(exc).__name__}: {exc}",
                html="",
            )


def fetch_website(url: str, timeout: float = 10.0, user_agent: str | None = None) -> FetchResult:
    """Convenience wrapper around ``WebsiteFetcher`` for one-off fetches."""
    return WebsiteFetcher(timeout=timeout, user_agent=user_agent).fetch(url)
