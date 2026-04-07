from site_discovery.detectors import (
    detect_affiliate_programs,
    detect_conversion_events,
    detect_ecommerce_engines,
)


def test_detect_conversion_events() -> None:
    html = """
    <html>
      <script src="https://www.googletagmanager.com/gtag/js?id=G-ABC"></script>
      <script>fbq('track', 'Purchase');</script>
      <button onclick="ttq.track('CompleteRegistration')">Submit</button>
    </html>
    """
    found = detect_conversion_events(html)
    assert "Google Analytics / gtag" in found
    assert "Meta Pixel" in found
    assert "TikTok Pixel" in found


def test_detect_ecommerce_engines() -> None:
    html = """
    <html>
      <script src="https://cdn.shopify.com/s/files/app.js"></script>
      <div data-wf-commerce="true"></div>
    </html>
    """
    found = detect_ecommerce_engines(html)
    assert "Shopify" in found
    assert "Webflow Ecommerce" in found


def test_detect_affiliate_programs() -> None:
    html = """
    <html>
      <a href="https://www.awin1.com/cread.php?awinaffid=1234">Deal</a>
      <script src="https://cdn.impact.com/s.js"></script>
    </html>
    """
    found = detect_affiliate_programs(html)
    assert "Awin" in found
    assert "Impact" in found
