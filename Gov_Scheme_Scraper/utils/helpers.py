import re
from datetime import datetime


def _collapse_spaces(text: str) -> str:
    # Replace non-breaking spaces, then collapse multiple spaces
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def _collapse_newlines(text: str) -> str:
    # Collapse 3+ newlines to two, and strip
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Trim spaces at line ends
    lines = [ln.rstrip() for ln in text.splitlines()]

    return "\n".join(lines).strip()


def normalize_text_field(text: str, preserve_paragraphs: bool = False) -> str:

    if text is None:
        return None

    if not isinstance(text, str):
        text = str(text)

    text = text.strip()

    if preserve_paragraphs:
        text = _collapse_spaces(text)
        text = _collapse_newlines(text)
    else:
        text = _collapse_spaces(text)
        text = text.replace("\n", " ")

    return text or None


def normalize_link(url: str) -> str:

    if not url:
        return None

    url = url.strip()

    # Remove fragment
    url = url.split('#')[0]

    # Remove trailing slash
    if url.endswith('/') and len(url) > 1:
        url = url[:-1]

    return url


def process_scheme(scheme: dict) -> dict:
    """
    Normalize and clean scheme fields
    """

    if not isinstance(scheme, dict):
        return scheme

    text_fields_paragraphs = [
        "details",
        "application_process",
        "documents_required",
        "exclusion",
    ]

    text_fields_inline = [
        "title",
        "eligibility",
        "benefits",
        "department",
        "category",
        "state",
        "target_group",
        "gender",
        "last_date_to_apply",
    ]

    for k in text_fields_paragraphs:

        if k in scheme:
            scheme[k] = normalize_text_field(
                scheme.get(k),
                preserve_paragraphs=True
            )

    for k in text_fields_inline:

        if k in scheme:
            scheme[k] = normalize_text_field(
                scheme.get(k),
                preserve_paragraphs=False
            )

    # Numeric fields
    for numf in (
        "min_age",
        "max_age",
        "min_income",
        "max_income"
    ):

        v = scheme.get(numf)

        if isinstance(v, str) and not v.strip():
            scheme[numf] = None

    # Normalize link
    if "application_link" in scheme:
        scheme["application_link"] = normalize_link(
            scheme.get("application_link")
        )

    return scheme


# =========================================================
# GLOBAL HELPER FUNCTIONS
# =========================================================

def is_noise_text(text: str) -> bool:

    if not text:
        return True

    t = re.sub(r"\s+", " ", text.strip().lower())

    NOISE_PATTERNS = [
        r"search accessibility tools",
        r"feedback website policies",
        r"dashboard",
        r"share on facebook",
        r"share of x",
        r"close",
        r"privacy policy",
        r"copyright",
        r"all rights reserved",
        r"skip to main content",
        r"screen reader",
        r"site map",
        r"contact us",
        r"visitor count",
        r"accessibility statement",
        r"rti"
    ]

    for p in NOISE_PATTERNS:

        if re.search(p, t):
            return True

    # very short nav-like fragments
    if len(t) <= 4 and re.match(r"^[a-z]+$", t):
        return True

    return False


def dedupe_preserve_order(text: str) -> str:
    """
    Remove duplicate lines while preserving order
    """

    if not text:
        return text

    lines = [
        ln.strip()
        for ln in text.splitlines()
        if ln.strip()
    ]

    seen = set()
    out = []

    for ln in lines:

        if ln in seen:
            continue

        seen.add(ln)
        out.append(ln)

    return "\n".join(out)


def find_main_content(soup, title_text=None):
    """
    Return the most likely main content container
    """

    candidates = []

    for sel in (
        "main",
        "article",
        "div[role=main]",
        "div.scheme-content",
        "div.entry-content",
        "div#content"
    ):

        c = soup.select_one(sel)

        if c:
            candidates.append(c)

    # fallback
    if not candidates:
        return soup.body or soup

    # Prefer container with title
    if title_text:

        for c in candidates:

            h1 = c.find("h1")

            if (
                h1 and
                title_text.strip().lower()
                in h1.get_text(strip=True).lower()
            ):
                return c

    # Choose container with most paragraphs
    best = None
    best_count = -1

    for c in candidates:

        cnt = len(c.find_all("p"))

        if cnt > best_count:
            best_count = cnt
            best = c

    return best or candidates[0]


# =========================================================
# DATE HELPERS
# =========================================================

def parse_date_str(text: str):
    """
    Extract first date and return YYYY-MM-DD
    """

    if not text or not isinstance(text, str):
        return None

    text = text.strip()

    # ISO format
    m = re.search(r"(\d{4}-\d{2}-\d{2})", text)

    if m:
        return m.group(1)

    # Numeric dates
    m = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})", text)

    if m:

        s = m.group(1)

        for fmt in (
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%m/%d/%Y"
        ):

            try:
                return datetime.strptime(
                    s,
                    fmt
                ).date().isoformat()

            except Exception:
                continue

    # Textual dates
    m = re.search(
        r"(\d{1,2}\s+[A-Za-z]+\s+\d{4})",
        text
    )

    if m:

        s = m.group(1)

        for fmt in (
            "%d %B %Y",
            "%d %b %Y"
        ):

            try:
                return datetime.strptime(
                    s,
                    fmt
                ).date().isoformat()

            except Exception:
                continue

    return None


def parse_date_range(text: str):
    """
    Extract date range and return (start, end)
    """

    if not text or not isinstance(text, str):
        return (None, None)

    txt = (
        text.replace('\u2013', '-')
        .replace('\u2014', '-')
        .replace('–', '-')
    )

    # Explicit range
    m = re.search(
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s*[-to]+\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})",
        txt,
        flags=re.I
    )

    if m:

        a = parse_date_str(m.group(1))
        b = parse_date_str(m.group(2))

        return (a, b)

    # Fallback
    candidates = re.findall(
        r"\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}\s+[A-Za-z]+\s+\d{4}",
        txt
    )

    parsed = [parse_date_str(c) for c in candidates]
    parsed = [p for p in parsed if p]

    if len(parsed) >= 2:
        return (parsed[0], parsed[1])

    if len(parsed) == 1:
        return (parsed[0], None)

    return (None, None)


# =========================================================
# OTHER PARSERS
# =========================================================

def parse_currency(text: str):

    if not text or not isinstance(text, str):
        return None

    m = re.search(
        r"(\d+[\,\d]*\.?\d*)",
        text.replace('\u20b9', '')
    )

    if not m:
        return None

    num = m.group(1).replace(',', '')

    try:
        return f"{float(num):.2f}"

    except Exception:
        return None


def parse_age_range(text: str):

    if not text or not isinstance(text, str):
        return (None, None)

    m = re.search(
        r"(\d{1,2})\s*-\s*(\d{1,3})\s*years",
        text.lower()
    )

    if m:
        return (
            int(m.group(1)),
            int(m.group(2))
        )

    m = re.search(
        r"minimum age[:\s]*(\d{1,2})",
        text.lower()
    )

    if m:
        return (int(m.group(1)), None)

    return (None, None)


# =========================================================
# KV EXTRACTION
# =========================================================

def extract_kv_from_soup(soup):

    kv = {}

    if not soup:
        return kv

    # Tables
    tables = soup.find_all('table')

    for table in tables:

        for tr in table.find_all('tr'):

            tds = tr.find_all(['td', 'th'])

            if len(tds) >= 2:

                key = tds[0].get_text(
                    ' ',
                    strip=True
                ).lower()

                val = tds[1].get_text(
                    ' ',
                    strip=True
                )

                if key:
                    kv[key] = val

    # Definition lists
    for dl in soup.find_all('dl'):

        dts = dl.find_all('dt')

        for dt in dts:

            dd = dt.find_next_sibling('dd')

            if dd:

                key = dt.get_text(
                    ' ',
                    strip=True
                ).lower()

                val = dd.get_text(
                    ' ',
                    strip=True
                )

                kv[key] = val

    # Colon-separated paragraphs
    for p in soup.find_all(['p', 'li']):

        text = p.get_text(
            ' ',
            strip=True
        )

        if ':' in text:

            parts = text.split(':', 1)

            key = parts[0].strip().lower()
            val = parts[1].strip()

            if key and val:
                kv.setdefault(key, val)

    return kv