"""High-level scanning orchestration for website discovery."""

from __future__ import annotations

from typing import Iterable

from .detectors import (
    detect_affiliate_programs,
    detect_conversion_events,
    detect_ecommerce_engines,
)
from .fetcher import WebsiteFetcher


def scan_urls(urls: Iterable[str], timeout: float = 10.0) -> dict:
    """Scan websites and return a JSON-serializable report."""
    websites = [url.strip() for url in urls if url and url.strip()]
    results: list[dict] = []
    fetcher = WebsiteFetcher(timeout=timeout)

    for website in websites:
        fetch_result = fetcher.fetch(website)
        if not fetch_result.ok:
            results.append(
                {
                    "website": website,
                    "normalized_url": fetch_result.normalized_url,
                    "is_reachable": False,
                    "status_code": fetch_result.status_code,
                    "error": fetch_result.error,
                    "conversion_events": [],
                    "ecommerce_engines": [],
                    "affiliate_programs": [],
                }
            )
            continue

        html = fetch_result.html or ""
        results.append(
            {
                "website": website,
                "normalized_url": fetch_result.normalized_url,
                "is_reachable": True,
                "status_code": fetch_result.status_code,
                "error": None,
                "conversion_events": detect_conversion_events(html),
                "ecommerce_engines": detect_ecommerce_engines(html),
                "affiliate_programs": detect_affiliate_programs(html),
            }
        )

    summary = {
        "total_websites": len(websites),
        "reachable_websites": sum(1 for item in results if item["is_reachable"]),
        "unreachable_websites": sum(1 for item in results if not item["is_reachable"]),
    }
    return {"summary": summary, "results": results}

