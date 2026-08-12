from scraper.dynamic_scraper import scrape_dynamic
from scraper.html_scraper import scrape_html
from utils.helpers import normalize_text_field, is_noise_text
import re


def scrape_housing(url: str, base_scheme: dict = None) -> dict:
    scheme = base_scheme

    if not scheme:
        if "myscheme.gov.in" in url:
            scheme = scrape_dynamic(url)
        else:
            scheme = scrape_html(url)

    if not scheme:
        return None

    # Keep title safe
    original_title = scheme.get("title")

    # ---------- Domain defaults ----------
    scheme["category"] = "Housing & Shelter"
    scheme["department"] = "Housing / Rural Development / Urban Development"
    scheme["state"] = "Maharashtra"
    scheme["target_group"] = "Homeless / Economically Weaker Sections / Rural & Urban Poor"
    scheme["min_age"] = None
    scheme["max_age"] = None

    title = (original_title or "").lower()

    if any(x in title for x in ["pmay", "pradhan mantri awas"]):
        scheme["category"] = "PMAY - Housing for All"
        if "gramin" in title or "pmay-g" in title:
            scheme["target_group"] = "Rural Poor / Houseless Families"
        else:
            scheme["target_group"] = "Urban Poor / EWS / LIG"
    elif "ramai" in title:
        scheme["target_group"] = "SC / Neo-Buddhist Families"
    elif "janman" in title:
        scheme["target_group"] = "Particularly Vulnerable Tribal Groups (PVTGs)"
    elif any(x in title for x in ["shelter", "home", "hostel"]):
        scheme["target_group"] = "Homeless / Destitute / Working Women"
    elif "clss" in title or "credit linked":
        scheme["category"] = "Credit Linked Subsidy (CLSS)"
        scheme["target_group"] = "Middle Income Group / EWS / LIG"

    if "myscheme.gov.in" in url:
        scheme = clean_myscheme_housing(scheme)

    # Restore title if it got lost
    if not scheme.get("title") and original_title:
        scheme["title"] = original_title

    # Final clean
    for field in ["details", "eligibility", "benefits", "documents_required", "application_process", "exclusion"]:
        if scheme.get(field):
            scheme[field] = normalize_text_field(scheme[field], preserve_paragraphs=True)

    return scheme


def clean_myscheme_housing(scheme: dict) -> dict:
    """Balanced cleaner – removes FAQ but keeps real content"""

    def cut_faq(text):
        if not text:
            return text
        # Only cut when clear FAQ section starts
        parts = re.split(
            r"frequently asked questions|"
            r"was this helpful|"
            r"sources and references",
            text,
            flags=re.IGNORECASE
        )
        return parts[0].strip() if parts else text

    for field in ["details", "eligibility", "benefits", "documents_required", "application_process", "exclusion"]:
        scheme[field] = cut_faq(scheme.get(field) or "")

    # Remove obvious noise only
    NOISE = [
        r"you're being redirected.*?(ok|cancel)",
        r"your mobile number will be shared.*?(ok|cancel)",
        r"something went wrong.*?ok",
        r"you have already submitted.*?ok",
        r"you need to sign in.*?sign in",
        r"it seems you have already initiated.*?",
        r"was this helpful\??",
        r"news and updates.*?available",
        r"check eligibility",
        r"sign in",
        r"cancel ok",
        r"apply now",
    ]

    def remove_noise(text):
        if not text:
            return ""
        for pat in NOISE:
            text = re.sub(pat, " ", text, flags=re.IGNORECASE | re.DOTALL)
        return text.strip()

    for field in ["details", "eligibility", "benefits", "documents_required", "application_process", "exclusion"]:
        scheme[field] = remove_noise(scheme.get(field) or "")

    # Remove exact duplicate lines only
    def remove_exact_duplicates(text):
        if not text:
            return None
        lines = []
        seen = set()
        for line in text.splitlines():
            line = line.strip()
            if not line or len(line) < 15:
                continue
            lower = line.lower()
            if lower in seen:
                continue
            if is_noise_text(line):
                continue
            seen.add(lower)
            lines.append(line)
        return "\n".join(lines) if lines else None

    for field in ["details", "eligibility", "benefits", "documents_required", "application_process", "exclusion"]:
        scheme[field] = remove_exact_duplicates(scheme.get(field))

    # Light separation only
    details = scheme.get("details") or ""
    if details:
        # Stop at clear next section if present
        parts = re.split(r"\n\s*(Eligibility|Benefits|Documents Required|Application Process)\s*\n", details, flags=re.IGNORECASE)
        if len(parts) > 1:
            scheme["details"] = parts[0].strip()

    return scheme