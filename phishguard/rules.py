import re
from urllib.parse import urlparse
from email.utils import parseaddr


URL_PATTERN = re.compile(
    r"""(?i)\b(?:https?://|www\.)[^\s<>"']+"""
)

SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "t.co", "is.gd",
    "cutt.ly", "rb.gy", "shorturl.at", "ow.ly"
}

BRAND_DOMAINS = {
    "paypal": ("paypal.com",),
    "google": ("google.com", "google.co.uk"),
    "microsoft": ("microsoft.com", "live.com", "outlook.com"),
    "apple": ("apple.com",),
    "amazon": ("amazon.com", "amazon.co.uk"),
    "netflix": ("netflix.com",),
    "facebook": ("facebook.com", "fb.com"),
    "instagram": ("instagram.com",),
    "venmo": ("venmo.com",),
    "chase": ("chase.com",),
    "wells fargo": ("wellsfargo.com",),
}

URGENCY_TERMS = (
    "urgent", "immediately", "act now", "final warning",
    "account will be closed", "account suspended",
    "expire today", "within 24 hours", "verify now",
    "limited time", "action required", "legal action"
)

CREDENTIAL_TERMS = (
    "password", "passcode", "one-time code", "otp",
    "login credentials", "sign in to verify",
    "verify your account", "confirm your identity",
    "social security number", "ssn"
)

PAYMENT_TERMS = (
    "send money", "wire transfer", "gift card",
    "pay immediately", "payment required", "bank details",
    "credit card details", "crypto wallet",
    "bitcoin payment", "pay the fee"
)


def _normalise_url(value):
    value = value.strip().rstrip(".,;:!?)]}")
    if value.lower().startswith("www."):
        value = "http://" + value
    return value


def _domain_from_url(value):
    try:
        parsed = urlparse(_normalise_url(value))
        host = (parsed.hostname or "").lower().rstrip(".")
        return host
    except (ValueError, AttributeError):
        return ""


def _domain_matches(host, allowed_domains):
    return any(
        host == domain or host.endswith("." + domain)
        for domain in allowed_domains
    )


def analyze_message(sender="", subject="", body="", links=""):
    """
    Return a heuristic phishing risk score, verdict, and explanations.
    This score is not a calibrated probability or a guarantee of safety.
    """
    sender = str(sender or "").strip()
    subject = str(subject or "").strip()
    body = str(body or "").strip()
    links = str(links or "").strip()

    text = f"{subject}\n{body}".lower()
    combined = f"{sender}\n{subject}\n{body}\n{links}"
    findings = []
    score = 0

    def add_finding(points, message):
        nonlocal score
        score += points
        findings.append({
            "points": points,
            "reason": message
        })

    # Extract URLs from the message and the separate links field.
    found_urls = URL_PATTERN.findall(combined)
    if links:
        found_urls.extend(
            item.strip()
            for item in re.split(r"[\s,;]+", links)
            if item.strip()
        )

    urls = list(dict.fromkeys(
        _normalise_url(url) for url in found_urls
    ))

    # Sender display name versus email domain.
    display_name, email_address = parseaddr(sender)
    email_domain = ""
    if "@" in email_address:
        email_domain = email_address.rsplit("@", 1)[1].lower().rstrip(".")

    sender_lower = sender.lower()
    for brand, domains in BRAND_DOMAINS.items():
        brand_mentioned = brand in display_name.lower() or (
            not display_name and brand in sender_lower
        )
        if brand_mentioned and email_domain:
            if not _domain_matches(email_domain, domains):
                add_finding(
                    30,
                    f"The sender appears to represent {brand.title()}, "
                    "but the email domain does not match a known "
                    "official domain."
                )
                break

    # Suspicious URL characteristics.
    for url in urls:
        host = _domain_from_url(url)
        if not host:
            continue

        if host in SHORTENER_DOMAINS:
            add_finding(
                15,
                f"The link uses a URL-shortening service ({host}), "
                "which hides the final destination."
            )

        if re.fullmatch(r"(?:\d{1,3}\.){3}\d{1,3}", host):
            add_finding(
                25,
                "A link uses a raw IP address instead of a normal domain."
            )

        if host.startswith("xn--") or ".xn--" in host:
            add_finding(
                25,
                "A link contains an internationalized domain encoding "
                "that can sometimes be used to imitate other domains."
            )

        if "@" in urlparse(url).netloc:
            add_finding(
                25,
                "A link contains an @ symbol in its network location, "
                "which can obscure the actual destination."
            )

        if host.count(".") >= 4:
            add_finding(
                10,
                "A link has an unusually long subdomain structure."
            )

    # Language-based indicators.
    if any(term in text for term in URGENCY_TERMS):
        add_finding(
            15,
            "The message uses urgent or threatening language to pressure "
            "the recipient to act quickly."
        )

    if any(term in text for term in CREDENTIAL_TERMS):
        add_finding(
            25,
            "The message mentions passwords, account verification, "
            "or other sensitive identity information."
        )

    if any(term in text for term in PAYMENT_TERMS):
        add_finding(
            25,
            "The message mentions a payment, financial details, "
            "or an unusual payment method."
        )

    # A link combined with pressure is more concerning.
    if urls and any(term in text for term in URGENCY_TERMS):
        add_finding(
            10,
            "The message combines a link with urgent language."
        )

    score = min(score, 100)

    if score >= 70:
        verdict = "Dangerous"
    elif score >= 35:
        verdict = "Suspicious"
    else:
        verdict = "Safe"

    if not findings:
        findings.append({
            "points": 0,
            "reason": (
                "No configured warning patterns were detected. "
                "This does not prove the message is safe."
            )
        })

    return {
        "verdict": verdict,
        "risk_score": score,
        "findings": findings,
        "urls": urls,
        "disclaimer": (
            "This is a rule-based heuristic assessment, not a "
            "probability. Rules can miss attacks and flag legitimate "
            "messages. Verify unexpected requests independently."
        )
    }
