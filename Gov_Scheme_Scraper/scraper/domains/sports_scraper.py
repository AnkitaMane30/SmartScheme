import re
import requests
from bs4 import BeautifulSoup

from scraper.html_scraper import scrape_html
from utils.helpers import (
    dedupe_preserve_order,
    is_noise_text,
    find_main_content
)


def scrape_sport(url, base_scheme=None):

    scheme = base_scheme or scrape_html(url)

    # =========================================================
    # DEFAULT METADATA
    # =========================================================

    scheme["category"] = "Sports Scheme"
    scheme["department"] = "Sports and Youth Services Department"
    scheme["state"] = "Maharashtra"
    scheme["target_group"] = "Citizens / Athletes"

    # =========================================================
    # INITIALIZE FIELDS
    # =========================================================

    fields = [
        "details",
        "eligibility",
        "benefits",
        "documents_required",
        "application_process",
        "exclusion",
        "date"
    ]

    for field in fields:

        if field not in scheme or scheme[field] is None:
            scheme[field] = ""

    # =========================================================
    # FETCH PAGE
    # =========================================================

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=20
    )

    soup = BeautifulSoup(response.text, "html.parser")

    # =========================================================
    # HELPER
    # =========================================================

    def extract_nested_text(tag):

        if not tag:
            return ""

        return tag.get_text(" ", strip=True)

    # =========================================================
    # DATE EXTRACTION
    # =========================================================

    page_text = soup.get_text(" ", strip=True)

    date_pattern = (
        r"\d{2}[/-]\d{2}[/-]\d{4}"
        r"\s*(?:-|to)\s*"
        r"\d{2}[/-]\d{2}[/-]\d{4}"
    )

    date_match = re.search(
        date_pattern,
        page_text,
        flags=re.I
    )

    if date_match:
        scheme["date"] = date_match.group(0).strip()

    # =========================================================
    # FIND MAIN CONTENT ONLY
    # =========================================================

    main_content = find_main_content(
        soup,
        scheme.get("title")
    )

    # =========================================================
    # EXTRACT CONTENT ELEMENTS
    # =========================================================

    elements = main_content.find_all([
        "h1",
        "h2",
        "h3",
        "h4",
        "p",
        "li",
        "td",
        "strong"
    ])

    current_section = "details"

    # =========================================================
    # NOISE KEYWORDS
    # =========================================================

    noise_keywords = [
        "share on facebook",
        "share on linkedin",
        "share of x",
        "formerly twitter",
        "skip to main content",
        "screen reader",
        "site map",
        "dashboard",
        "rti",
        "privacy policy",
        "copyright",
        "all rights reserved",
        "feedback",
        "accessibility",
        "visitor count",
        "home",
        "central government"
    ]

    # =========================================================
    # MAIN LOOP
    # =========================================================

    for el in elements:

        text = extract_nested_text(el)

        if not text:
            continue

        text = text.strip()

        lower = text.lower()

        # =====================================================
        # SKIP NOISE
        # =====================================================

        if is_noise_text(text):
            continue

        if any(k in lower for k in noise_keywords):
            continue

        # Skip isolated dates
        if re.fullmatch(
            r"\d{2}[/-]\d{2}[/-]\d{4}",
            text
        ):
            continue

        # Remove date line
        text = re.sub(
            r"date\s*:\s*"
            r"\d{2}[/-]\d{2}[/-]\d{4}"
            r"\s*(?:-|to)\s*"
            r"\d{2}[/-]\d{2}[/-]\d{4}",
            "",
            text,
            flags=re.I
        ).strip()

        if not text:
            continue

        # Skip tiny garbage text
        if len(text) <= 2:
            continue

        # =====================================================
        # SECTION DETECTION
        # =====================================================

        if any(k in lower for k in [
            "how to apply",
            "application process",
            "procedure to apply",
            "apply online",
            "online application"
        ]):

            current_section = "application_process"
            continue

        elif any(k in lower for k in [
            "eligibility",
            "beneficiary",
            "who can apply"
        ]):

            current_section = "eligibility"
            continue

        elif any(k in lower for k in [
            "benefits",
            "nature of benefits",
            "financial benefits",
            "stipend"
        ]):

            current_section = "benefits"
            continue

        elif any(k in lower for k in [
            "documents required",
            "necessary documents",
            "important documents",
            "required documents"
        ]):

            current_section = "documents_required"
            continue

        elif any(k in lower for k in [
            "overview",
            "objective",
            "purpose",
            "features"
        ]):

            current_section = "details"
            continue

        elif "exclusion" in lower:

            current_section = "exclusion"
            continue

        # =====================================================
        # STORE CONTENT
        # =====================================================

        # Skip heading-only text
        if lower in [
            "benefits",
            "eligibility",
            "documents required",
            "application process",
            "overview",
            "details"
        ]:
            continue

        # DETAILS
        if current_section == "details":

            # avoid single-word garbage
            if len(text.split()) >= 4:
                scheme["details"] += text + "\n"

        # ELIGIBILITY
        elif current_section == "eligibility":

            if len(text.split()) >= 2:
                scheme["eligibility"] += text + "\n"

        # BENEFITS
        elif current_section == "benefits":

            if len(text.split()) >= 2:
                scheme["benefits"] += text + "\n"

        # DOCUMENTS
        elif current_section == "documents_required":

            invalid_doc_keywords = [
                "rti",
                "privacy",
                "copyright",
                "share on",
                "dashboard"
            ]

            if (
                len(text.split()) >= 3
                and not any(
                    k in lower
                    for k in invalid_doc_keywords
                )
            ):
                scheme["documents_required"] += text + "\n"

        # APPLICATION PROCESS
        elif current_section == "application_process":

            invalid_app_keywords = [
                "share on",
                "home",
                "central government"
            ]

            if not any(
                k in lower
                for k in invalid_app_keywords
            ):

                if len(text.split()) >= 3:
                    scheme["application_process"] += text + "\n"

        # EXCLUSION
        elif current_section == "exclusion":

            scheme["exclusion"] += text + "\n"

    # =========================================================
    # FALLBACK DETAILS EXTRACTION
    # =========================================================

    if not scheme["details"]:

        # Look for paragraphs nested in divs
        paras = main_content.find_all("p")

        collected = []

        for p in paras:

            txt = extract_nested_text(p)

            if not txt:
                continue

            lower = txt.lower()

            # Skip noise text
            if is_noise_text(txt):
                continue

            # Skip paragraphs containing social sharing keywords
            if any(k in lower for k in [
                "share on facebook",
                "share on linkedin",
                "share on twitter",
                "share of x",
                "share",
            ]):
                continue

            # Skip noise keywords
            if any(k in lower for k in noise_keywords):
                continue

            # Skip section headers
            is_section_header = any(k in lower for k in [
                "how to apply",
                "application process",
                "procedure to apply",
                "apply online",
                "online application",
                "eligibility",
                "beneficiary",
                "who can apply",
                "benefits",
                "nature of benefits",
                "financial benefits",
                "stipend",
                "documents required",
                "necessary documents",
                "important documents",
                "required documents",
                "overview",
                "objective",
                "purpose",
                "features",
                "exclusion"
            ])

            if is_section_header:
                continue

            # Only include paragraphs with meaningful content
            if len(txt.split()) >= 4:
                collected.append(txt)

        scheme["details"] = "\n".join(collected)

    # =========================================================
    # CLEANUP
    # =========================================================

    for fld in [
        "details",
        "eligibility",
        "benefits",
        "documents_required",
        "application_process",
        "exclusion"
    ]:

        if scheme.get(fld):

            # Remove duplicates
            scheme[fld] = dedupe_preserve_order(
                scheme[fld]
            )

            # Remove extra blank lines
            scheme[fld] = re.sub(
                r"\n+",
                "\n",
                scheme[fld]
            ).strip()

    # =========================================================
    # REMOVE INVALID DOCUMENTS FIELD
    # =========================================================

    doc = scheme.get(
        "documents_required",
        ""
    ).lower()

    invalid_doc_words = [
        "share on",
        "rti",
        "privacy",
        "dashboard"
    ]

    if (
        len(doc.strip()) < 10
        or any(w in doc for w in invalid_doc_words)
    ):
        scheme["documents_required"] = None

    # =========================================================
    # REMOVE INVALID APPLICATION PROCESS
    # =========================================================

    app = scheme.get(
        "application_process",
        ""
    ).lower()

    invalid_app_words = [
        "share on facebook",
        "share on linkedin",
        "home central government"
    ]

    if any(w in app for w in invalid_app_words):
        scheme["application_process"] = None

    # =========================================================
    # FINAL CLEANUP
    # =========================================================

    for key, value in scheme.items():

        if isinstance(value, str):

            value = value.strip()

            if value.lower() in [
                "none",
                "null",
                ""
            ]:
                scheme[key] = None

    return scheme