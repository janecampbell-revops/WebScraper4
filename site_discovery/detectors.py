"""Heuristic detectors for marketing/conversion tooling on websites."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PatternGroup:
    name: str
    regex: re.Pattern[str]


def _build_patterns(raw_patterns: list[tuple[str, str]]) -> list[PatternGroup]:
    return [PatternGroup(name=name, regex=re.compile(pattern, re.IGNORECASE)) for name, pattern in raw_patterns]


CONVERSION_EVENT_PATTERNS = _build_patterns(
    [
        ("Google Tag Manager", r"googletagmanager\.com/gtm\.js"),
        ("Google Analytics / gtag", r"googletagmanager\.com/gtag/js|gtag\("),
        ("Meta Pixel", r"connect\.facebook\.net/.*/fbevents\.js|fbq\("),
        ("TikTok Pixel", r"analytics\.tiktok\.com|ttq\.(track|load)"),
        ("LinkedIn Insight Tag", r"snap\.licdn\.com/li\.lms-analytics/insight\.min\.js|_linkedin_partner_id"),
        ("Hotjar", r"static\.hotjar\.com|hj\("),
        ("Segment Analytics", r"cdn\.segment\.com/analytics\.js|analytics\.load\("),
        ("Heap Analytics", r"heap\.js|heap\.load\("),
        ("Klaviyo Tracking", r"klaviyo|_learnq"),
        ("Conversion Event Keywords", r"(add_to_cart|begin_checkout|purchase|complete_registration|generate_lead)"),
        ("Form Submit Hooks", r"addEventListener\(['\"]submit['\"]|type=['\"]submit['\"]"),
    ]
)


ECOMMERCE_PATTERNS = _build_patterns(
    [
        ("Shopify", r"cdn\.shopify\.com|myshopify\.com|shopify\.theme"),
        ("WooCommerce", r"woocommerce|wp-content/plugins/woocommerce"),
        ("Magento / Adobe Commerce", r"mage\/|magento|cdn\.adobe\.com\/commerce"),
        ("BigCommerce", r"cdn\d*\.bigcommerce\.com|stencil-utils|bigcommerce"),
        ("Wix Stores", r"wixstores|parastorage\.com\/services\/wixstores"),
        ("Squarespace Commerce", r"squarespace.*commerce|commerce-cart"),
        ("PrestaShop", r"prestashop"),
        ("Salesforce Commerce Cloud", r"demandware|salesforce.*commerce"),
        ("OpenCart", r"index\.php\?route=(product|checkout|account)"),
        ("Ecwid", r"ecwid\.com\/script\.js|x-ecwid"),
        ("Webflow Ecommerce", r"data-wf-site|data-wf-commerce"),
    ]
)


AFFILIATE_PATTERNS = _build_patterns(
    [
        ("ShareASale", r"shareasale\.com"),
        ("Impact", r"impact\.com|impactradius\.com"),
        ("CJ Affiliate", r"cj\.com|commission-junction|kqzyfj\.com"),
        ("Rakuten Advertising", r"rakutenadvertising\.com|linksynergy\.com"),
        ("Awin", r"awin1\.com|awin\.com"),
        ("PartnerStack", r"partnerstack\.com"),
        ("Refersion", r"refersion\.com"),
        ("Rewardful", r"rewardful\.com"),
        ("FirstPromoter", r"firstpromoter\.com"),
        ("ClickBank", r"hop\.clickbank\.net"),
        ("Amazon Associates", r"amazon-adsystem\.com|amzn\.to"),
        ("Skimlinks", r"skimresources\.com"),
        ("Generic Affiliate Query Parameters", r"[?&](aff(?:iliate)?_?(?:id|source)?|ref(?:errer|id|code)?|utm_affiliate)="),
    ]
)


def _find_matches(page_content: str, groups: list[PatternGroup]) -> list[str]:
    found: list[str] = []
    for group in groups:
        if group.regex.search(page_content):
            found.append(group.name)
    return found


def detect_conversion_events(page_content: str) -> list[str]:
    """Detect likely conversion event tools/signals from a page's HTML."""
    return _find_matches(page_content, CONVERSION_EVENT_PATTERNS)


def detect_ecommerce_engines(page_content: str) -> list[str]:
    """Detect likely ecommerce engines/platforms from a page's HTML."""
    return _find_matches(page_content, ECOMMERCE_PATTERNS)


def detect_affiliate_programs(page_content: str) -> list[str]:
    """Detect likely affiliate networks/programs from a page's HTML."""
    return _find_matches(page_content, AFFILIATE_PATTERNS)
