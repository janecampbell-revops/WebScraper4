# WebScraper4

CLI web scraper that:
- accepts a list of websites,
- checks whether each website works (HTTP 2xx/3xx),
- and, for reachable sites, detects likely:
  - conversion events/tools,
  - ecommerce engines,
  - affiliate program signals.

## Quick start

### 1) Create a virtual environment and install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 2) Run against URLs directly

```bash
website-discovery https://www.shopify.com https://example.com
```

### 3) Run against a file

Create `websites.txt`:

```txt
# One URL per line
https://www.shopify.com
https://www.woocommerce.com
example.com
```

Then:

```bash
website-discovery --input-file websites.txt --output-file report.json
```

## Output shape

The CLI outputs JSON:

```json
{
  "summary": {
    "total_websites": 2,
    "reachable_websites": 1,
    "unreachable_websites": 1
  },
  "results": [
    {
      "website": "https://example.com",
      "normalized_url": "https://example.com",
      "is_reachable": true,
      "status_code": 200,
      "error": null,
      "conversion_events": ["Google Analytics / gtag"],
      "ecommerce_engines": [],
      "affiliate_programs": []
    }
  ]
}
```

## Notes

- Detection is heuristic and pattern-based (HTML/script signatures).
- Some sites block bots or require JavaScript rendering for complete visibility.
- This tool intentionally does not bypass anti-bot protections.
