import re
import requests
from bs4 import BeautifulSoup
from scraper.html_scraper import scrape_html
from utils.helpers import (
    extract_kv_from_soup,
    find_main_content,
    is_noise_text,
    dedupe_preserve_order,
    normalize_text_field,
    parse_date_str,
    parse_age_range,
    parse_currency,
)

SECTION_KEYWORDS = {
    "application_process": [
        "how to apply",
        "application process",
        "procedure to apply",
        "apply online",
        "online application",
        "submit application",
        "application form",
        "mode of application",
        "registration",
        "apply here",
        "process to apply",
    ],
    "eligibility": [
        "eligibility",
        "who can apply",
        "beneficiary",
        "applicant",
        "qualification",
        "age limit",
        "income limit",
        "target group",
        "eligible",
    ],
    "benefits": [
        "benefit",
        "benefits",
        "subsidy",
        "incentive",
        "support",
        "assistance",
        "grant",
        "financial assistance",
        "amount",
        "scheme benefit",
        "allowance",
    ],
    "documents_required": [
        "document",
        "documents required",
        "mandatory documents",
        "required documents",
        "proof",
        "necessary documents",
    ],
    "exclusion": [
        "exclusion",
        "not eligible",
        "ineligible",
        "not covered",
        "exclusions",
    ],
    "details": [
        "overview",
        "objective",
        "purpose",
        "about",
        "scope",
        "background",
        "introduction",
        "scheme details",
        "key features",
        "highlights",
        "summary",
        "description",
    ],
}

HEADING_TOKENS = set(
    token
    for tokens in SECTION_KEYWORDS.values()
    for token in tokens
)

NOISE_TOKENS = [
    "check eligibility",
    "quick links",
    "useful links",
    "news and updates",
    "share",
    "powered by",
    "accessibility",
    "screen reader",
    "contact us",
    "terms & conditions",
    "disclaimer",
    "home",
    "dashboard",
    "created by",
    "last updated on",
    "skip to content",
    "menu",
    "login",
    "register",
    "footer",
    "all rights reserved",
]


def _normalize_text(value):
    if not value:
        return None
    return normalize_text_field(value, preserve_paragraphs=True)


def _clean_title(title):
    if not title:
        return None

    title = normalize_text_field(title)

    bad_suffixes = [
        "| MyScheme",
        "- MyScheme",
        "| Government of India",
        "- Government of India",
        "| Maharashtra Government",
        "- Maharashtra Government",
        "| MahaDBT",
        "- MahaDBT",
    ]

    for suffix in bad_suffixes:
        if title.endswith(suffix):
            title = title.replace(suffix, "").strip()

    title = re.sub(r"\s+", " ", title)
    return title.strip()


def _is_bad_title(text):
    if not text:
        return True

    lower = text.lower().strip()

    if len(lower) < 10:
        return True

    bad_exact = [
        "quick links",
        "useful links",
        "important links",
        "navigation",
        "menu",
        "home",
        "dashboard",
        "benefits",
        "eligibility",
        "documents required",
        "application process",
        "contact us",
        "share",
        "login",
        "register",
        "news",
        "updates",
        "overview",
        "details",
        "information",
        "click here",
        "read more",
    ]
    if lower in bad_exact:
        return True

    for token in NOISE_TOKENS:
        if token in lower:
            return True

    letters = sum(c.isalpha() for c in lower)
    if letters < 5:
        return True

    return False


def _extract_title(soup, scheme=None):
    if scheme and scheme.get("title") and not _is_bad_title(scheme.get("title")):
        return _clean_title(scheme["title"])

    candidates = []

    def try_candidate(text, score=0):
        if not text:
            return
        text = _clean_title(text)
        if not text or _is_bad_title(text):
            return
        candidates.append((score, text))

    # Prefer explicit page headers
    for tag_name, score in [("h1", 30), ("h2", 20), ("h3", 10)]:
        for tag in soup.find_all(tag_name):
            try_candidate(tag.get_text(" ", strip=True), score)

    # Meta and title tags as fallback
    title_tag = soup.title.string if soup.title and soup.title.string else None
    try_candidate(title_tag, 5)
    og_title = soup.select_one("meta[property='og:title']")
    if og_title and og_title.get("content"):
        try_candidate(og_title["content"], 5)

    if candidates:
        return sorted(candidates, key=lambda item: (-item[0], len(item[1])))[0][1]

    return None


def _detect_section(text):
    if not text:
        return None

    lower = text.lower().strip()
    if len(lower) > 120:
        return None

    for section, keywords in SECTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in lower:
                return section

    return None


def _is_navigation_text(text):
    if not text:
        return True
    lower = text.lower().strip()
    if lower in ["", "maharashtra", "check eligibility", "back", "next"]:
        return True
    if any(token in lower for token in NOISE_TOKENS):
        return True
    return False


def _is_valid_application_process(text):
    if not text:
        return False
    lower = text.lower().strip()
    if len(lower) < 15:
        return False
    if any(token in lower for token in [
        "check eligibility",
        "share on",
        "quick links",
        "useful links",
        "accessibility",
        "screen reader",
        "contact us",
        "terms & conditions",
        "news and updates",
        "powered by",
        "last updated on",
    ]):
        return False
    return True


def _extract_text(el):
    if not el:
        return None
    return el.get_text(" ", strip=True)


def scrape_education(url, base_scheme=None):
    scheme = base_scheme or scrape_html(url)

    scheme["category"] = "Education Scheme"
    scheme["department"] = scheme.get("department") or "Education Department"
    scheme["state"] = "Maharashtra"
    scheme["target_group"] = scheme.get("target_group") or "Students / Learners"
    scheme["application_link"] = url

    for field in [
        "details",
        "eligibility",
        "benefits",
        "documents_required",
        "application_process",
        "exclusion",
    ]:
        if scheme.get(field) is None:
            scheme[field] = ""

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=18)
        response.raise_for_status()
        html = response.text
    except Exception:
        html = None

    soup = BeautifulSoup(html, "html.parser") if html else None

    if soup is not None:
        title = _extract_title(soup, scheme=scheme)
        if title:
            scheme["title"] = title

        content_div = find_main_content(soup, scheme.get("title")) or soup
        elements = content_div.find_all([
            "h1",
            "h2",
            "h3",
            "h4",
            "p",
            "li",
            "td",
            "tr",
        ])

        current_section = "details"
        for el in elements:
            text = _extract_text(el)
            if not text:
                continue
            if is_noise_text(text) or _is_navigation_text(text):
                continue

            section = _detect_section(text)
            if section:
                current_section = section
                continue

            if current_section == "application_process" and not _is_valid_application_process(text):
                continue

            if len(text.split()) <= 5:
                continue

            if current_section in scheme:
                scheme[current_section] = (scheme.get(current_section) or "") + text + "\n"

        if not scheme["details"]:
            paragraphs = []
            for p in content_div.find_all("p")[:6]:
                text = _extract_text(p)
                if text and not is_noise_text(text) and not _is_navigation_text(text) and len(text.split()) >= 10:
                    paragraphs.append(text)
            scheme["details"] = "\n".join(paragraphs)

        kv = extract_kv_from_soup(soup)
        for key, val in kv.items():
            lower_key = key.lower()
            if any(x in lower_key for x in ("department", "dept")):
                scheme["department"] = scheme.get("department") or normalize_text_field(val)
            if any(x in lower_key for x in ("how to apply", "application process", "procedure to apply", "apply online", "application form", "registration")):
                if not scheme["application_process"]:
                    scheme["application_process"] = normalize_text_field(val, preserve_paragraphs=True)
            if any(x in lower_key for x in ("eligibility", "who can apply", "beneficiary", "applicant", "qualification")):
                if not scheme["eligibility"]:
                    scheme["eligibility"] = normalize_text_field(val, preserve_paragraphs=True)
            if any(x in lower_key for x in ("benefit", "subsidy", "incentive", "assistance", "amount")):
                if not scheme["benefits"]:
                    scheme["benefits"] = normalize_text_field(val, preserve_paragraphs=True)
            if any(x in lower_key for x in ("document", "documents required", "necessary documents", "proof")):
                if not scheme["documents_required"]:
                    scheme["documents_required"] = normalize_text_field(val, preserve_paragraphs=True)
            if any(x in lower_key for x in ("exclusion", "not eligible", "ineligible")):
                if not scheme["exclusion"]:
                    scheme["exclusion"] = normalize_text_field(val, preserve_paragraphs=True)
            if any(x in lower_key for x in ("last date", "closing date", "last date to apply", "deadline")):
                if not scheme.get("last_date_to_apply"):
                    scheme["last_date_to_apply"] = parse_date_str(val)
            if "start date" in lower_key or "from" == lower_key.strip():
                if not scheme.get("start_date"):
                    scheme["start_date"] = parse_date_str(val)
            if "end date" in lower_key or "valid until" in lower_key:
                if not scheme.get("end_date"):
                    scheme["end_date"] = parse_date_str(val)
            if "age" in lower_key:
                if not scheme.get("min_age") or not scheme.get("max_age"):
                    min_age, max_age = parse_age_range(val)
                    scheme["min_age"] = scheme.get("min_age") or min_age
                    scheme["max_age"] = scheme.get("max_age") or max_age
            if "income" in lower_key or "amount" in lower_key:
                if not scheme.get("min_income"):
                    scheme["min_income"] = scheme.get("min_income") or parse_currency(val)

    for field in [
        "details",
        "eligibility",
        "benefits",
        "documents_required",
        "application_process",
        "exclusion",
    ]:
        if scheme.get(field):
            scheme[field] = _normalize_text(dedupe_preserve_order(scheme[field]))
            if field == "application_process" and not _is_valid_application_process(scheme["application_process"]):
                scheme[field] = None
        else:
            scheme[field] = None

    return scheme
