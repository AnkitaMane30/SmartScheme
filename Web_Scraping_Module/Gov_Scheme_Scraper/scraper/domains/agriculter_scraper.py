from scraper.html_scraper import scrape_html
from scraper.dynamic_scraper import scrape_dynamic
from utils.helpers import normalize_text_field, is_noise_text
import re


def scrape_agriculture(url: str, base_scheme: dict = None) -> dict:
    scheme = base_scheme

    if not scheme:
        if "myscheme.gov.in" in url:
            scheme = scrape_dynamic(url)
        else:
            scheme = scrape_html(url)

    if not scheme:
        return None

    # ---------- Domain defaults ----------
    scheme["category"] = "Agriculture"
    scheme["department"] = "Agriculture Department"
    scheme["state"] = "Maharashtra"
    scheme["target_group"] = "Farmers"
    scheme["min_age"] = None
    scheme["max_age"] = None

    title = (scheme.get("title") or "").lower()

    if "irrigation" in title:
        scheme["category"] = "Agriculture - Irrigation"
    elif "horticulture" in title:
        scheme["category"] = "Horticulture"
    elif any(x in title for x in ["insurance", "apghat", "suraksha"]):
        scheme["category"] = "Farmer Insurance / Accident"
    elif any(x in title for x in ["sanman", "nidhi", "mahasanman"]):
        scheme["category"] = "Farmer Income Support"
    elif "pocra" in title:
        scheme["category"] = "Climate Resilient Agriculture"
    elif "gaikwad" in title or "sabalikaran" in title:
        scheme["category"] = "Land / Asset Support for SC / Neo-Buddhists"
        scheme["target_group"] = "Scheduled Caste / Neo-Buddhist Landless Families"
        scheme["department"] = "Social Justice and Special Assistance Department"

    # ---------- Strong cleaning for myScheme ----------
    if "myscheme.gov.in" in url:
        scheme = clean_myscheme_agriculture(scheme)

    # ---------- Final clean ----------
    for field in ["details", "eligibility", "benefits", "documents_required", "application_process", "exclusion"]:
        if scheme.get(field):
            scheme[field] = normalize_text_field(scheme[field], preserve_paragraphs=True)

    return scheme


def clean_myscheme_agriculture(scheme: dict) -> dict:
    """Final strong cleaner with strict section separation"""

    # 1. Hard cut FAQ
    def cut_faq(text):
        if not text:
            return text
        parts = re.split(
            r"frequently asked questions|what is the full form|what percentage of the scheme|who are the neo-buddhists|what are the objectives|is this a state funded|where can i find|is there an age-related|is there an income-related|where can i post my grievances|where can i find the format",
            text,
            flags=re.IGNORECASE
        )
        return parts[0].strip() if parts else text

    for field in ["details", "eligibility", "benefits", "documents_required", "application_process", "exclusion"]:
        scheme[field] = cut_faq(scheme.get(field) or "")

    # 2. Remove noise
    NOISE = [
        r"you're being redirected.*?(ok|cancel)",
        r"your mobile number will be shared.*?(ok|cancel)",
        r"something went wrong.*?ok",
        r"you have already submitted.*?ok",
        r"you need to sign in.*?sign in",
        r"it seems you have already initiated.*?",
        r"was this helpful\??",
        r"news and updates",
        r"no new news and updates available",
        r"check eligibility",
        r"sign in",
        r"cancel",
        r"apply now",
        r"share",
        r"sources and references",
        r"guidelines",
    ]

    def remove_noise(text):
        if not text:
            return ""
        for pat in NOISE:
            text = re.sub(pat, " ", text, flags=re.IGNORECASE | re.DOTALL)
        return text

    for field in ["details", "eligibility", "benefits", "documents_required", "application_process", "exclusion"]:
        scheme[field] = remove_noise(scheme.get(field) or "")

    # 3. Keep only useful lines
    def keep_useful(text):
        if not text:
            return None
        lines = []
        seen = set()
        for line in text.splitlines():
            line = line.strip()
            if not line or len(line) < 10:
                continue
            lower = line.lower()
            if lower in seen:
                continue
            if is_noise_text(line):
                continue
            if any(x in lower for x in [
                "was this helpful", "news and updates", "check eligibility",
                "sign in", "ok", "cancel", "frequently asked", "what is the",
                "what percentage", "who are the", "where can i", "is there an"
            ]):
                continue
            seen.add(lower)
            lines.append(line)
        return "\n".join(lines) if lines else None

    for field in ["details", "eligibility", "benefits", "documents_required", "application_process", "exclusion"]:
        scheme[field] = keep_useful(scheme.get(field))

    # 4. STRICT SEPARATION – Benefits must never contain Application Process
    benefits = scheme.get("benefits") or ""
    if benefits:
        # Cut anything that looks like application process
        parts = re.split(
            r"application process|how to apply|step 1:|offline step|online step|visit the district",
            benefits,
            flags=re.IGNORECASE
        )
        scheme["benefits"] = parts[0].strip() if parts else benefits

    # 5. STRICT SEPARATION – Eligibility must never contain Benefits or Application Process
    elig = scheme.get("eligibility") or ""
    if elig:
        # Remove benefit-like sentences
        lines = []
        for line in elig.splitlines():
            lower = line.lower()
            if any(k in lower for k in [
                "should be", "must be", "applicant should", "age group",
                "landless", "below poverty", "scheduled caste", "nav-buddhist",
                "citizen of india", "permanent resident"
            ]):
                if not any(b in lower for b in ["beneficiary is provided", "provided with", "2-acre", "4-acre", "subsidy and", "is loan"]):
                    lines.append(line)
        scheme["eligibility"] = "\n".join(lines) if lines else None

    # 6. STRICT SEPARATION – Application Process must not contain Benefits
    app = scheme.get("application_process") or ""
    if app:
        parts = re.split(
            r"benefits|the beneficiary is provided|financial assistance",
            app,
            flags=re.IGNORECASE
        )
        scheme["application_process"] = parts[0].strip() if parts else app

    return scheme