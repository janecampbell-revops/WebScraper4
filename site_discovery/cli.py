"""Command-line interface for website discovery scanning."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

from .scanner import scan_urls


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="website-discovery",
        description=(
            "Check website availability and detect conversion events, ecommerce "
            "engines, and affiliate program signals."
        ),
    )
    parser.add_argument(
        "urls",
        nargs="*",
        help="Website URLs to scan (example: https://example.com).",
    )
    parser.add_argument(
        "--input-file",
        type=Path,
        help="Text file with one URL per line (supports comments with '#').",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Network timeout in seconds per request (default: 10.0).",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        help="Optional JSON output file. Defaults to stdout.",
    )
    return parser.parse_args(argv)


def _load_urls_from_file(input_file: Path) -> list[str]:
    urls: list[str] = []
    for raw in input_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        urls.append(line)
    return urls


def _collect_urls(args: argparse.Namespace) -> list[str]:
    urls: list[str] = []
    if args.input_file:
        if not args.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {args.input_file}")
        urls.extend(_load_urls_from_file(args.input_file))
    urls.extend(args.urls)

    # Preserve order while deduplicating.
    deduped: list[str] = []
    seen: set[str] = set()
    for url in urls:
        key = url.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(key)
    return deduped


def _emit_output(payload: dict, output_file: Path | None) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True)
    if output_file:
        output_file.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(list(argv) if argv is not None else None)

    try:
        urls = _collect_urls(args)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not urls:
        print(
            "No URLs provided. Use positional arguments or --input-file.",
            file=sys.stderr,
        )
        return 2

    report = scan_urls(urls=urls, timeout=args.timeout)
    _emit_output(report, args.output_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
