# WebScraper4

This project includes two CLI tools:

- **`simple-web-scraper`**: scrape one URL and extract its page title + links.
- **`website-discovery`**: scan many sites for availability and marketing/ecommerce signals.

## Quick start

### 1) Create a virtual environment and install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 2) Use the simple scraper (single URL)

```bash
simple-web-scraper https://example.com
```

Example output:

```json
{
  "error": null,
  "final_url": "https://example.com",
  "input_url": "https://example.com",
  "is_reachable": true,
  "link_count": 1,
  "links": ["https://www.iana.org/domains/example"],
  "normalized_url": "https://example.com",
  "status_code": 200,
  "title": "Example Domain"
}
```

Options:

```bash
simple-web-scraper https://example.com --max-links 10 --output-file page.json
```

### 3) Run discovery scan against URLs directly

```bash
website-discovery https://www.shopify.com https://example.com
```

### 4) Run discovery scan against a file

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

## Discovery output shape

The `website-discovery` CLI outputs JSON:

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
