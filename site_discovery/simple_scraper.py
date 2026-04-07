"""Simple CLI web scraper that extracts a page title and links."""

from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin

from .fetcher import WebsiteFetcher


class _SimpleHTMLExtractor(HTMLParser):
    """Extract a title and anchor links from HTML."""

    def __init__(self, *, base_url: str, max_links: int) -> None:
        super().__init__(convert_charrefs=True)
        self._base_url = base_url
        self._max_links = max_links
        self._in_title = False
        self._title_chunks: list[str] = []
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title":
            self._in_title = True
            return

        if tag.lower() == "a" and len(self.links) < self._max_links:
            attr_map = dict(attrs)
            href = attr_map.get("href")
            if href:
                self.links.append(urljoin(self._base_url, href))

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            cleaned = data.strip()
            if cleaned:
                self._title_chunks.append(cleaned)

    @property
    def title(self) -> str | None:
        if not self._title_chunks:
            return None
        return " ".join(self._title_chunks)


def extract_page_data(html: str, *, base_url: str, max_links: int) -> dict:
    """Parse HTML into a simple structured payload."""
    parser = _SimpleHTMLExtractor(base_url=base_url, max_links=max_links)
    parser.feed(html)
    return {
        "title": parser.title,
        "links": parser.links,
        "link_count": len(parser.links),
    }


def scrape_url(url: str, *, timeout: float = 10.0, max_links: int = 20) -> dict:
    """Fetch one URL and return extracted data."""
    fetcher = WebsiteFetcher(timeout=timeout)
    fetch_result = fetcher.fetch(url)

    payload = {
        "input_url": url,
        "normalized_url": fetch_result.normalized_url,
        "final_url": fetch_result.final_url,
        "is_reachable": fetch_result.reachable,
        "status_code": fetch_result.status_code,
        "error": fetch_result.error,
        "title": None,
        "links": [],
        "link_count": 0,
    }

    if fetch_result.ok and fetch_result.html:
        payload.update(
            extract_page_data(
                fetch_result.html,
                base_url=fetch_result.final_url or fetch_result.normalized_url,
                max_links=max_links,
            )
        )

    return payload


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="simple-web-scraper",
        description="Scrape a single web page and return title + links as JSON.",
    )
    parser.add_argument("url", help="URL to scrape (example: https://example.com)")
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Network timeout in seconds (default: 10.0).",
    )
    parser.add_argument(
        "--max-links",
        type=int,
        default=20,
        help="Maximum number of links to include (default: 20).",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        help="Optional path to write JSON output instead of stdout.",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(list(argv) if argv is not None else None)
    payload = scrape_url(args.url, timeout=args.timeout, max_links=args.max_links)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output_file:
        args.output_file.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
