import re
import json
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

# =========================================================
# SECTION KEYWORDS
# =========================================================

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
    ],
}

HEADING_TOKENS = set(
    token
    for tokens in SECTION_KEYWORDS.values()
    for token in tokens
)

# =========================================================
# NORMALIZE TEXT
# =========================================================

def _normalize_text(value):

    if not value:
        return None

    return normalize_text_field(
        value,
        preserve_paragraphs=True
    )

# =========================================================
# CLEAN TITLE
# =========================================================

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

            title = title.replace(
                suffix,
                ""
            ).strip()

    title = re.sub(r"\s+", " ", title)

    return title.strip()

# =========================================================
# BAD TITLE FILTER
# =========================================================

def _is_bad_title(text):

    if not text:
        return True

    lower = text.lower().strip()

    if len(lower) < 5:
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

    bad_contains = [
        "skip to content",
        "share on",
        "follow us",
        "latest news",
        "related links",
        "social media",
        "footer",
        "copyright",
    ]

    if any(x in lower for x in bad_contains):
        return True

    letters = sum(c.isalpha() for c in lower)

    if letters < 3:
        return True

    return False

# =========================================================
# TITLE EXTRACTION (REFINED)
# =========================================================

def _extract_title(soup, scheme=None, url=None):

    candidates = []

    # -----------------------------------------------------
    # Helper
    # -----------------------------------------------------

    def add_candidate(text, score=0, source=""):

        if not text:
            return

        text = _clean_title(text)

        if not text:
            return

        if _is_bad_title(text):
            return

        words = len(text.split())

        if words < 3:
            return

        if len(text) < 12:
            return

        candidates.append({
            "text": text,
            "score": score,
            "source": source,
        })

    # -----------------------------------------------------
    # Existing title
    # -----------------------------------------------------

    existing = scheme.get("title") if scheme else None

    if existing:

        add_candidate(
            existing,
            score=40,
            source="base_scraper"
        )

    # -----------------------------------------------------
    # Breadcrumbs
    # -----------------------------------------------------

    breadcrumb_selectors = [
        ".breadcrumb li",
        ".breadcrumbs li",
        ".breadcrumb-item",
        "[aria-label='breadcrumb'] li",
        ".page-breadcrumb li",
    ]

    for selector in breadcrumb_selectors:

        items = soup.select(selector)

        if items:

            last = items[-1].get_text(
                " ",
                strip=True
            )

            add_candidate(
                last,
                score=80,
                source="breadcrumb"
            )

    # -----------------------------------------------------
    # Meta Tags
    # -----------------------------------------------------

    meta_selectors = [
        ("meta", {"property": "og:title"}),
        ("meta", {"name": "twitter:title"}),
        ("meta", {"name": "title"}),
    ]

    for tag_name, attrs in meta_selectors:

        tag = soup.find(
            tag_name,
            attrs=attrs
        )

        if tag:

            content = tag.get("content")

            add_candidate(
                content,
                score=90,
                source="meta"
            )

    # -----------------------------------------------------
    # JSON-LD
    # -----------------------------------------------------

    for script in soup.find_all(
        "script",
        type="application/ld+json"
    ):

        try:

            content = script.string

            if not content:
                continue

            data = json.loads(content)

            if isinstance(data, dict):

                possible_fields = [
                    "name",
                    "headline",
                    "alternateName",
                ]

                for field in possible_fields:

                    if data.get(field):

                        add_candidate(
                            data.get(field),
                            score=95,
                            source="jsonld"
                        )

            elif isinstance(data, list):

                for item in data:

                    if isinstance(item, dict):

                        for field in [
                            "name",
                            "headline",
                        ]:

                            if item.get(field):

                                add_candidate(
                                    item.get(field),
                                    score=95,
                                    source="jsonld"
                                )

        except Exception:
            pass

    # -----------------------------------------------------
    # Main Heading Areas
    # -----------------------------------------------------

    priority_heading_selectors = [
        "main h1",
        "article h1",
        ".content h1",
        ".main-content h1",
        ".page-title",
        ".entry-title",
        ".post-title",
        ".hero-title",
        ".scheme-title",
        ".page-header h1",
    ]

    for selector in priority_heading_selectors:

        for tag in soup.select(selector):

            text = tag.get_text(
                " ",
                strip=True
            )

            add_candidate(
                text,
                score=100,
                source=f"selector:{selector}"
            )

    # -----------------------------------------------------
    # H1
    # -----------------------------------------------------

    for h1 in soup.find_all("h1"):

        text = h1.get_text(
            " ",
            strip=True
        )

        score = 85

        parent_class = " ".join(
            h1.parent.get("class", [])
        ).lower()

        if any(
            x in parent_class
            for x in [
                "header",
                "hero",
                "title",
                "banner",
            ]
        ):
            score += 10

        add_candidate(
            text,
            score=score,
            source="h1"
        )

    # -----------------------------------------------------
    # H2 fallback
    # -----------------------------------------------------

    for h2 in soup.find_all("h2"):

        text = h2.get_text(
            " ",
            strip=True
        )

        add_candidate(
            text,
            score=50,
            source="h2"
        )

    # -----------------------------------------------------
    # HTML title
    # -----------------------------------------------------

    if soup.title:

        title_text = soup.title.get_text(
            " ",
            strip=True
        )

        separators = [
            "|",
            "-",
            "::",
        ]

        for sep in separators:

            if sep in title_text:
                title_text = (
                    title_text
                    .split(sep)[0]
                    .strip()
                )

        add_candidate(
            title_text,
            score=70,
            source="html_title"
        )

    # -----------------------------------------------------
    # URL fallback
    # -----------------------------------------------------

    if url:

        slug = (
            url.rstrip("/")
            .split("/")[-1]
        )

        slug = slug.replace("-", " ")
        slug = slug.replace("_", " ")

        slug = normalize_text_field(slug)

        if slug:

            add_candidate(
                slug.title(),
                score=30,
                source="url_slug"
            )

    # -----------------------------------------------------
    # No candidates
    # -----------------------------------------------------

    if not candidates:
        return None

    # -----------------------------------------------------
    # Remove duplicates
    # -----------------------------------------------------

    unique = {}

    for item in candidates:

        key = item["text"].lower()

        if (
            key not in unique
            or item["score"] > unique[key]["score"]
        ):

            unique[key] = item

    candidates = list(unique.values())

    # -----------------------------------------------------
    # Final score tuning
    # -----------------------------------------------------

    for item in candidates:

        text = item["text"].lower()

        positive_keywords = [
            "scheme",
            "yojana",
            "mission",
            "program",
            "programme",
            "subsidy",
            "assistance",
            "welfare",
            "agriculture",
            "farmer",
        ]

        for kw in positive_keywords:

            if kw in text:
                item["score"] += 8

        negative_keywords = [
            "quick links",
            "benefits",
            "eligibility",
            "documents required",
            "application process",
            "read more",
            "latest updates",
            "contact us",
        ]

        for kw in negative_keywords:

            if kw in text:
                item["score"] -= 30

        words = len(text.split())

        if 4 <= words <= 14:
            item["score"] += 10

    # -----------------------------------------------------
    # Sort
    # -----------------------------------------------------

    candidates = sorted(
        candidates,
        key=lambda x: x["score"],
        reverse=True
    )

    best = candidates[0]

    return best["text"]

# =========================================================
# TEXT HELPERS
# =========================================================

def _extract_nested_text(tag):

    return (
        tag.get_text(
            " ",
            strip=True
        )
        if tag else ""
    )

def _is_noise_element(el, text):

    if not text:
        return True

    lower = text.lower().strip()

    noise_keywords = [
        "quick links",
        "useful links",
        "important links",
        "share on",
        "contact us",
        "latest updates",
        "navigation",
        "menu",
        "search",
        "skip to content",
        "login",
        "register",
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

    return False

# =========================================================
# SECTION DETECTION
# =========================================================

def _detect_section(text, current_section):

    lower = text.lower().strip()

    if len(lower) > 80:
        return current_section

    for section, keywords in SECTION_KEYWORDS.items():

        for keyword in keywords:

            if (
                lower == keyword
                or lower.startswith(keyword + ":")
                or lower.startswith(keyword + " ")
            ):
                return section

    return current_section

# =========================================================
# STORE TEXT
# =========================================================

def _apply_scheme_text(
    scheme,
    section,
    text
):

    if not text:
        return

    existing = scheme.get(section) or ""

    scheme[section] = (
        existing + "\n" + text
        if existing else text
    ).strip()

# =========================================================
# APPLICATION PROCESS VALIDATION
# =========================================================

def _is_valid_application_process(text):

    if not text:
        return False

    noise_phrases = [
        "share on",
        "quick links",
        "latest updates",
        "contact us",
        "news and updates",
    ]

    lower = text.lower()

    if any(
        phrase in lower
        for phrase in noise_phrases
    ):
        return False

    return True

# =========================================================
# MAIN SCRAPER
# =========================================================

def scrape_agriculture(
    url,
    base_scheme=None
):

    scheme = (
        base_scheme
        or scrape_html(url)
    )

    # -----------------------------------------------------
    # DEFAULT VALUES
    # -----------------------------------------------------

    scheme["category"] = "Agriculture Scheme"

    scheme["department"] = (
        scheme.get("department")
        or "Agriculture Department"
    )

    scheme["state"] = "Maharashtra"

    scheme["target_group"] = (
        scheme.get("target_group")
        or "Farmers / Agricultural Workers"
    )

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

    # -----------------------------------------------------
    # REQUEST
    # -----------------------------------------------------

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64)"
        )
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

    except Exception:
        return scheme

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    title = _extract_title(
        soup,
        scheme,
        url
    )

    if title:
        scheme["title"] = title

    # -----------------------------------------------------
    # MAIN CONTENT
    # -----------------------------------------------------

    content_div = (
        find_main_content(
            soup,
            scheme.get("title")
        )
        or soup.body
        or soup
    )

    # -----------------------------------------------------
    # REMOVE NOISE
    # -----------------------------------------------------

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
        .skip-link
        """
    ):

        try:
            bad.decompose()

        except Exception:
            pass

    # -----------------------------------------------------
    # CONTENT EXTRACTION
    # -----------------------------------------------------

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

        text = _extract_nested_text(el)

        if not text:
            continue

        if is_noise_text(text):
            continue

        text = normalize_text_field(text)

        if _is_noise_element(el, text):
            continue

        if len(text.split()) <= 2:
            continue

        lower = text.lower().strip()

        # -------------------------------------------------
        # Skip duplicate title
        # -------------------------------------------------

        if scheme.get("title"):

            title_lower = scheme["title"].lower()

            if (
                lower == title_lower
                or lower in title_lower
                or title_lower in lower
            ):
                continue

        # -------------------------------------------------
        # Section heading
        # -------------------------------------------------

        if lower in HEADING_TOKENS:

            current_section = _detect_section(
                text,
                current_section
            )

            continue

        next_section = _detect_section(
            text,
            current_section
        )

        if (
            el.name in [
                "h1",
                "h2",
                "h3",
                "h4",
            ]
            and next_section != current_section
        ):

            current_section = next_section
            continue

        if (
            current_section
            == "application_process"
        ):

            if not _is_valid_application_process(
                text
            ):
                continue

        _apply_scheme_text(
            scheme,
            current_section,
            text
        )

    # -----------------------------------------------------
    # FALLBACK DETAILS
    # -----------------------------------------------------

    if not scheme.get("details"):

        paras = content_div.find_all([
            "p",
            "li",
        ])

        scheme["details"] = "\n".join(
            [
                _extract_nested_text(p)
                for p in paras[:5]
                if p
                and not is_noise_text(
                    _extract_nested_text(p)
                )
            ]
        )

    # -----------------------------------------------------
    # KEY VALUE EXTRACTION
    # -----------------------------------------------------

    kv = extract_kv_from_soup(soup)

    for key, val in kv.items():

        lower_key = key.lower()

        # Eligibility
        if "eligibility" in lower_key:

            scheme["eligibility"] = (
                scheme["eligibility"]
                or normalize_text_field(val)
            )

        # Benefits
        if "benefit" in lower_key:

            scheme["benefits"] = (
                scheme["benefits"]
                or normalize_text_field(val)
            )

        # Documents
        if "document" in lower_key:

            scheme["documents_required"] = (
                scheme["documents_required"]
                or normalize_text_field(val)
            )

        # Application
        if (
            "apply" in lower_key
            or "application process" in lower_key
        ):

            scheme["application_process"] = (
                scheme["application_process"]
                or normalize_text_field(val)
            )

        # Dates
        if "last date" in lower_key:

            scheme["last_date_to_apply"] = (
                parse_date_str(val)
            )

        if "start date" in lower_key:

            scheme["start_date"] = (
                parse_date_str(val)
            )

        if "end date" in lower_key:

            scheme["end_date"] = (
                parse_date_str(val)
            )

        # Age
        if "age" in lower_key:

            min_age, max_age = (
                parse_age_range(val)
            )

            scheme["min_age"] = min_age
            scheme["max_age"] = max_age

        # Income
        if "income" in lower_key:

            scheme["min_income"] = (
                parse_currency(val)
            )

    # -----------------------------------------------------
    # CLEANUP
    # -----------------------------------------------------

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

            scheme[field] = _normalize_text(
                scheme[field]
            )

        else:
            scheme[field] = None

    return scheme

