
import re
import ipaddress
from urllib.parse import urlparse


URL_PATTERN = re.compile(
    r"""https?://[^\s<>"']+|www\.[^\s<>"']+""",
    re.IGNORECASE,
)

SHORTENER_DOMAINS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "ow.ly",
    "is.gd",
    "buff.ly",
    "rebrand.ly",
}


def analyze_urls(message):
    """
    Inspect URLs found in an SMS for potentially suspicious
    characteristics. This is heuristic analysis, not a
    malware scan or a guarantee that a URL is malicious.
    """

    urls = URL_PATTERN.findall(message or "")
    findings = []

    if not urls:
        return {
            "urls_found": False,
            "urls": [],
            "findings": [],
            "risk_level": "No URL detected",
        }

    for raw_url in urls:
        cleaned_url = raw_url.rstrip(".,!?;:)")
        normalized_url = (
            cleaned_url
            if cleaned_url.lower().startswith(("http://", "https://"))
            else "https://" + cleaned_url
        )

        parsed = urlparse(normalized_url)
        hostname = (parsed.hostname or "").lower()

        if not hostname:
            continue

        url_findings = []

        if parsed.scheme == "http":
            url_findings.append("Uses an unencrypted HTTP connection.")

        if hostname in SHORTENER_DOMAINS:
            url_findings.append("Uses a shortened URL that hides its destination.")

        if "@" in parsed.netloc:
            url_findings.append("Contains an unusual @ symbol in the URL.")

        if hostname.startswith("xn--") or ".xn--" in hostname:
            url_findings.append("Contains an internationalized domain that needs careful inspection.")

        try:
            ipaddress.ip_address(hostname)
            url_findings.append("Uses an IP address instead of a recognizable domain name.")
        except ValueError:
            pass

        if len(hostname) > 50:
            url_findings.append("Uses an unusually long domain name.")

        findings.extend(url_findings)

    if findings:
        risk_level = "Suspicious indicators found"
    else:
        risk_level = "No obvious URL indicators found"

    return {
        "urls_found": True,
        "urls": urls,
        "findings": findings,
        "risk_level": risk_level,
    }
