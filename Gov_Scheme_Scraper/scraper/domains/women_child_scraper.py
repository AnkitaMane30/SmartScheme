import re
import requests
from bs4 import BeautifulSoup

from scraper.html_scraper import scrape_html
from utils.helpers import (
    extract_kv_from_soup,
    find_main_content,
    normalize_text_field,
    parse_date_str,
    parse_currency,
    parse_age_range,
    dedupe_preserve_order,
    is_noise_text,
)

SECTION_TITLES = {
    "application_process": [
        "how to apply",
        "application process",
        "procedure to apply",
        "apply online",
        "online application",
        "submit application",
        "application form",
        "how to avail",
        "how to access",
        "mode of application",
        "process to apply",
    ],
    "eligibility": [
        "eligibility",
        "who can apply",
        "beneficiary",
        "applicant",
        "qualification",
        "age limit",
        "age group",
        "income limit",
        "target group",
    ],
    "benefits": [
        "benefit",
        "benefits",
        "assistance",
        "support",
        "incentive",
        "stipend",
        "grant",
        "financial assistance",
        "amount",
        "scheme benefit",
        "what you get",
    ],
    "documents_required": [
        "document",
        "documents required",
        "mandatory documents",
        "required documents",
        "proof",
        "documents to be submitted",
    ],
    "exclusion": [
        "exclusion",
        "not eligible",
        "ineligible",
        "not covered",
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
    ],
}

HEADING_TOKENS = set([
    "details",
    "overview",
    "objective",
    "purpose",
    "about",
    "eligibility",
    "benefits",
    "documents required",
    "application process",
    "how to apply",
    "exclusion",
])


def _clean_paragraph(text: str):

    if not text:
        return None

    text = normalize_text_field(
        text,
        preserve_paragraphs=True
    )

    if not text:
        return None

    if is_noise_text(text):
        return None

    if len(text.strip()) < 3:
        return None

    return text


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
    ]

    for suffix in bad_suffixes:
        if title.endswith(suffix):
            title = title.replace(suffix, "").strip()

    return normalize_text_field(title)


def _is_noise_element(el, text):

    if not text:
        return True

    lower = text.lower().strip()

    if len(lower) < 3:
        return True

    noise_keywords = [
        "skip to content",
        "main menu",
        "navigation",
        "search",
        "home",
        "login",
        "register",
        "accessibility",
        "screen reader",
        "toggle navigation",
        "quick links",
        "copyright",
        "all rights reserved",
        "facebook",
        "twitter",
        "instagram",
        "youtube",
        "breadcrumb",
        "previous",
        "next",
        "top",
        "back",
        "menu",
    ]

    if lower in noise_keywords:
        return True

    classes = " ".join(
        el.get("class", [])
    ).lower()

    bad_classes = [
        "sidebar",
        "menu",
        "nav",
        "navbar",
        "breadcrumb",
        "footer",
        "header",
        "social",
        "share",
        "topbar",
    ]

    if any(c in classes for c in bad_classes):
        return True

    style = (el.get("style") or "").lower()

    if "display:none" in style:
        return True

    return False


def _detect_section(text: str, current_section: str):

    lower = text.lower().strip()

    # Only small heading-like text
    # should change section
    if len(lower) > 80:
        return current_section

    for section, keywords in SECTION_TITLES.items():

        for keyword in keywords:

            if (
                lower == keyword
                or lower.startswith(keyword + ":")
                or lower.startswith(keyword + " ")
            ):
                return section

    return current_section


def _append_section(
    scheme: dict,
    field: str,
    text: str
):

    text = _clean_paragraph(text)

    if not text:
        return

    current = scheme.get(field) or ""

    if text in current:
        return

    scheme[field] = (
        current
        + ("\n" if current else "")
        + text
    )


def _extract_title(soup, scheme: dict):

    # Existing title
    if scheme.get("title"):
        return _clean_title(
            scheme.get("title")
        )

    # ----------------------------------
    # Meta titles
    # ----------------------------------
    meta_candidates = [
        ("meta", {"property": "og:title"}),
        ("meta", {"name": "title"}),
        ("meta", {"name": "twitter:title"}),
    ]

    for tag_name, attrs in meta_candidates:

        tag = soup.find(
            tag_name,
            attrs=attrs
        )

        if tag and tag.get("content"):

            text = _clean_title(
                tag["content"]
            )

            if text and len(text) > 5:
                return text

    # ----------------------------------
    # JSON-LD structured data
    # ----------------------------------
    for script in soup.find_all(
        "script",
        type="application/ld+json"
    ):

        try:
            content = script.string

            if not content:
                continue

            match = re.search(
                r'"name"\s*:\s*"([^"]+)"',
                content
            )

            if match:

                text = _clean_title(
                    match.group(1)
                )

                if text and len(text) > 5:
                    return text

        except Exception:
            pass

    # ----------------------------------
    # Heading tags
    # ----------------------------------
    for heading in ["h1", "h2", "h3"]:

        tags = soup.find_all(heading)

        for tag in tags:

            text = _clean_title(
                tag.get_text(
                    " ",
                    strip=True
                )
            )

            if not text:
                continue

            lower = text.lower()

            skip_words = [
                "home",
                "menu",
                "search",
                "read more",
                "benefits",
                "documents required",
                "eligibility",
                "application process",
                "overview",
            ]

            if any(
                word in lower
                for word in skip_words
            ):
                continue

            if len(text) > 8:
                return text

    # ----------------------------------
    # Common title selectors
    # ----------------------------------
    selectors = [
        ".scheme-title",
        ".page-title",
        ".entry-title",
        ".post-title",
        ".hero-title",
        ".main-title",
        ".title",
    ]

    for selector in selectors:

        tag = soup.select_one(selector)

        if tag:

            text = _clean_title(
                tag.get_text(
                    " ",
                    strip=True
                )
            )

            if text and len(text) > 5:
                return text

    # ----------------------------------
    # HTML title fallback
    # ----------------------------------
    if soup.title:

        text = _clean_title(
            soup.title.get_text(
                " ",
                strip=True
            )
        )

        if text:

            text = re.sub(
                r"\s*[-|–]\s*(MyScheme|Government.*|WCD.*|Maharashtra.*)$",
                "",
                text,
                flags=re.I,
            )

            text = _clean_title(text)

            if text and len(text) > 5:
                return text

    return None


def _extract_from_soup(
    soup,
    scheme: dict
):

    if not soup:
        return scheme

    title = _extract_title(
        soup,
        scheme
    )

    if title:
        scheme["title"] = title

    content_div = find_main_content(
        soup,
        scheme.get("title")
    )

    if not content_div:
        content_div = soup.body or soup

    # Remove noisy elements
    for bad in content_div.select(
        """
        nav,
        header,
        footer,
        script,
        style,
        noscript,
        .breadcrumb,
        .breadcrumbs,
        .sidebar,
        .menu,
        .navbar,
        .nav,
        .footer,
        .header,
        .social,
        .share,
        .topbar,
        .topStripWrap,
        .topStrip,
        .skip-link,
        .skip-to-content,
        .page-links,
        .wp-block-group,
        .wp-block-image
        """
    ):

        try:
            bad.decompose()
        except Exception:
            pass

    elements = content_div.find_all([
        "h1",
        "h2",
        "h3",
        "h4",
        "p",
        "li",
        "td",
        "th",
    ])

    current_section = "details"

    for el in elements:

        text = el.get_text(
            " ",
            strip=True
        )

        if not text:
            continue

        text = normalize_text_field(text)

        if _is_noise_element(el, text):
            continue

        if len(text) < 4:
            continue

        lower = text.lower()

        # Skip duplicate title
        if (
            scheme.get("title")
            and lower == scheme["title"].lower()
        ):
            continue

        # Heading token detection
        if lower in HEADING_TOKENS:

            current_section = _detect_section(
                text,
                current_section
            )

            continue

        candidate_section = _detect_section(
            text,
            current_section
        )

        # Change section only for headings
        if el.name in [
            "h1",
            "h2",
            "h3",
            "h4",
        ]:

            if candidate_section != current_section:

                current_section = candidate_section
                continue

        # Append content
        if current_section == "details":

            _append_section(
                scheme,
                "details",
                text
            )

        elif current_section == "eligibility":

            _append_section(
                scheme,
                "eligibility",
                text
            )

        elif current_section == "benefits":

            _append_section(
                scheme,
                "benefits",
                text
            )

        elif current_section == "documents_required":

            _append_section(
                scheme,
                "documents_required",
                text
            )

        elif current_section == "application_process":

            _append_section(
                scheme,
                "application_process",
                text
            )

        elif current_section == "exclusion":

            _append_section(
                scheme,
                "exclusion",
                text
            )

    return scheme


def _map_kv_fields(
    soup,
    scheme: dict
):

    if not soup:
        return scheme

    kv = extract_kv_from_soup(soup)

    if not kv:
        return scheme

    for k, v in kv.items():

        lower_k = k.lower()

        value = normalize_text_field(
            v,
            preserve_paragraphs=True
        )

        if not value:
            continue

        # Dates
        if any(x in lower_k for x in [
            "last date",
            "closing date",
            "last date to apply",
            "application last date",
        ]):

            scheme["last_date_to_apply"] = (
                scheme.get(
                    "last_date_to_apply"
                )
                or parse_date_str(value)
            )

        if any(x in lower_k for x in [
            "start date",
            "commence",
            "from",
        ]):

            scheme["start_date"] = (
                scheme.get("start_date")
                or parse_date_str(value)
            )

        if any(x in lower_k for x in [
            "end date",
            "valid until",
            "upto",
            "till",
        ]):

            scheme["end_date"] = (
                scheme.get("end_date")
                or parse_date_str(value)
            )

        # Department
        if "department" in lower_k:

            scheme["department"] = (
                scheme.get("department")
                or normalize_text_field(value)
            )

        # Application process
        if any(x in lower_k for x in [
            "how to apply",
            "application process",
            "procedure to apply",
            "apply online",
            "method of application",
        ]):

            scheme["application_process"] = (
                scheme.get(
                    "application_process"
                )
                or value
            )

        # Eligibility
        if any(x in lower_k for x in [
            "eligib",
            "who can",
            "beneficiary",
            "applicant",
        ]):

            scheme["eligibility"] = (
                scheme.get("eligibility")
                or value
            )

        # Benefits
        if any(x in lower_k for x in [
            "benefit",
            "subsidy",
            "amount",
            "support",
            "assistance",
        ]):

            scheme["benefits"] = (
                scheme.get("benefits")
                or value
            )

        # Documents
        if any(x in lower_k for x in [
            "document",
            "documents required",
            "important documents",
            "necessary documents",
        ]):

            scheme["documents_required"] = (
                scheme.get(
                    "documents_required"
                )
                or value
            )

        # Age
        if "age" in lower_k:

            a_min, a_max = parse_age_range(
                value
            )

            scheme["min_age"] = (
                scheme.get("min_age")
                or a_min
            )

            scheme["max_age"] = (
                scheme.get("max_age")
                or a_max
            )

        # Income
        if "income" in lower_k:

            income = parse_currency(value)

            scheme["min_income"] = (
                scheme.get("min_income")
                or income
            )

    return scheme


def scrape_women_child(
    url,
    base_scheme=None
):

    scheme = base_scheme or scrape_html(url)

    # Default metadata
    scheme["category"] = (
        "Women and Child Development Scheme"
    )

    scheme["department"] = (
        scheme.get("department")
        or "Women and Child Development Department"
    )

    scheme["state"] = "Maharashtra"

    scheme["target_group"] = (
        "Women and Children"
    )

    scheme["gender"] = (
        scheme.get("gender")
        or "All"
    )

    soup = None

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/122.0 Safari/537.36"
        )
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        body_text = (
            soup.body.get_text(
                " ",
                strip=True
            )
            if soup.body
            else ""
        )

        # Detect invalid pages
        if (
            "something went wrong"
            in body_text.lower()
            or len(body_text) < 100
        ):
            soup = None

    except Exception as e:

        print(
            f"[women_child_scraper] "
            f"Error fetching {url}: {e}"
        )

        soup = None

    # Extract content
    if soup:

        scheme = _extract_from_soup(
            soup,
            scheme
        )

        scheme = _map_kv_fields(
            soup,
            scheme
        )

    # Fallback details
    if (
        not scheme.get("details")
        and soup
    ):

        paras = []

        for p in soup.find_all("p"):

            text = _clean_paragraph(
                p.get_text(
                    " ",
                    strip=True
                )
            )

            if text:
                paras.append(text)

        if paras:
            scheme["details"] = (
                "\n".join(paras[:5])
            )

    # Remove duplicates
    for field in [
        "details",
        "eligibility",
        "benefits",
        "documents_required",
        "application_process",
        "exclusion",
    ]:

        if scheme.get(field):

            scheme[field] = (
                dedupe_preserve_order(
                    scheme[field]
                )
            )

    return scheme