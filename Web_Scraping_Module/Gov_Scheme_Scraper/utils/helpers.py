import re
from datetime import datetime
from typing import Optional, Tuple, Any, Dict


# =========================================================
# BASIC TEXT CLEANING
# =========================================================

def _collapse_spaces(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def _collapse_newlines(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [ln.rstrip() for ln in text.splitlines()]
    return "\n".join(lines).strip()


def normalize_text_field(text: Any, preserve_paragraphs: bool = False) -> Optional[str]:
    if text is None:
        return None
    if not isinstance(text, str):
        text = str(text)

    text = text.strip()
    if not text:
        return None

    if preserve_paragraphs:
        text = _collapse_spaces(text)
        text = _collapse_newlines(text)
    else:
        text = _collapse_spaces(text)
        text = text.replace("\n", " ")

    return text or None


def normalize_link(url: str) -> Optional[str]:
    if not url:
        return None
    url = url.strip()
    url = url.split("#")[0]
    if url.endswith("/") and len(url) > 1:
        url = url[:-1]
    return url


# =========================================================
# NOISE DETECTION (much stronger)
# =========================================================

def is_noise_text(text: str) -> bool:
    if not text:
        return True

    t = re.sub(r"\s+", " ", text.strip().lower())

    # Very short or pure symbols
    if len(t) <= 3:
        return True

    NOISE_PATTERNS = [
        r"share on (facebook|twitter|linkedin|whatsapp|x)",
        r"share of x",
        r"skip to (main )?content",
        r"screen reader",
        r"accessibility (tools|statement)",
        r"visitor count",
        r"last updated",
        r"copyright",
        r"all rights reserved",
        r"privacy policy",
        r"website policies",
        r"feedback",
        r"dashboard",
        r"site map",
        r"contact us",
        r"rti",
        r"^date\s*:?\s*$",
        r"^home\s*>",
        r"breadcrumb",
        r"print this page",
        r"download pdf",
        r"click here",
        r"^more$",
        r"^read more$",
        r"^view details$",
        r"^apply now$",
        r"^login$",
        r"^register$",
        r"©",
        r"powered by",
        r"developed by",
        r"ministry of",
        r"government of india",
        r"government of maharashtra",
    ]

    for p in NOISE_PATTERNS:
        if re.search(p, t):
            return True

    # Pure navigation-like short phrases
    if len(t.split()) <= 2 and re.match(r"^[a-z\s]+$", t):
        return True

    return False


def dedupe_preserve_order(text: Optional[str]) -> Optional[str]:
    if not text:
        return text

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    seen = set()
    out = []
    for ln in lines:
        if ln in seen:
            continue
        seen.add(ln)
        out.append(ln)
    return "\n".join(out)


# =========================================================
# MAIN CONTENT FINDER
# =========================================================

def find_main_content(soup, title_text=None):
    candidates = []

    selectors = [
        "main",
        "article",
        "div[role=main]",
        "div.scheme-content",
        "div.entry-content",
        "div#content",
        "div.content",
        "div#main-content",
        "section.scheme-details",
        "div.page-content",
    ]

    for sel in selectors:
        c = soup.select_one(sel)
        if c:
            candidates.append(c)

    if not candidates:
        return soup.body or soup

    if title_text:
        for c in candidates:
            h1 = c.find("h1")
            if h1 and title_text.strip().lower() in h1.get_text(strip=True).lower():
                return c

    # Choose the container that has the most meaningful paragraphs
    best = None
    best_score = -1
    for c in candidates:
        paras = c.find_all("p")
        score = sum(1 for p in paras if len(p.get_text(strip=True)) > 40)
        if score > best_score:
            best_score = score
            best = c

    return best or candidates[0]


# =========================================================
# DATE HELPERS (much more robust)
# =========================================================

def parse_date_str(text: Any) -> Optional[str]:
    """Return YYYY-MM-DD or None"""
    if not text or not isinstance(text, str):
        return None

    text = text.strip()

    # Already ISO
    m = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    if m:
        return m.group(1)

    # DD/MM/YYYY or DD-MM-YYYY
    m = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})", text)
    if m:
        s = m.group(1)
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%m-%d-%Y"):
            try:
                return datetime.strptime(s, fmt).date().isoformat()
            except Exception:
                continue

    # 15th August 2019 / 15 August 2019
    m = re.search(r"(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})", text)
    if m:
        day, month, year = m.groups()
        for fmt in ("%d %B %Y", "%d %b %Y"):
            try:
                return datetime.strptime(f"{day} {month} {year}", fmt).date().isoformat()
            except Exception:
                continue

    return None


def parse_date_range(text: Any) -> Tuple[Optional[str], Optional[str]]:
    if not text or not isinstance(text, str):
        return None, None

    txt = text.replace("\u2013", "-").replace("\u2014", "-").replace("–", "-")

    m = re.search(
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s*[-to]+\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})",
        txt,
        flags=re.I,
    )
    if m:
        return parse_date_str(m.group(1)), parse_date_str(m.group(2))

    # Fallback – take first two dates found
    candidates = re.findall(
        r"\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}\s+[A-Za-z]+\s+\d{4}",
        txt,
    )
    if len(candidates) >= 2:
        return parse_date_str(candidates[0]), parse_date_str(candidates[1])
    if len(candidates) == 1:
        return parse_date_str(candidates[0]), None

    return None, None


# =========================================================
# AGE & INCOME PARSERS (safe)
# =========================================================

def parse_age_range(text: Any) -> Tuple[Optional[int], Optional[int]]:
    if not text or not isinstance(text, str):
        return None, None

    text = text.lower()

    # 18-60 years / 18 to 60 years
    m = re.search(r"(\d{1,2})\s*(?:-|to)\s*(\d{1,2})\s*(?:years?|yrs?)?", text)
    if m:
        return int(m.group(1)), int(m.group(2))

    # above 18 / below 60 / up to 35
    m = re.search(r"(?:above|over|more than|from)\s*(\d{1,2})", text)
    if m:
        return int(m.group(1)), None

    m = re.search(r"(?:below|under|upto|up to|less than)\s*(\d{1,2})", text)
    if m:
        return None, int(m.group(1))

    # single number with "years"
    m = re.search(r"(\d{1,2})\s*(?:years?|yrs?)", text)
    if m:
        age = int(m.group(1))
        if 5 <= age <= 100:
            return age, age

    return None, None


def parse_currency(text: Any) -> Optional[float]:
    """Extract a meaningful income/amount. Avoids page numbers."""
    if not text or not isinstance(text, str):
        return None

    text = text.replace(",", "").replace("₹", " ").replace("Rs.", " ").replace("Rs", " ")

    # Look for patterns like 2.5 lakh, 50000, 1 crore etc.
    m = re.search(r"(\d+(?:\.\d+)?)\s*(lakh|lac|crore|cr)?", text, re.I)
    if m:
        num = float(m.group(1))
        unit = (m.group(2) or "").lower()
        if unit in ("lakh", "lac"):
            num *= 100000
        elif unit in ("crore", "cr"):
            num *= 10000000

        # Sanity check – ignore very small numbers that are probably not income
        if num < 100 and "income" not in text.lower() and "lakh" not in text.lower():
            return None
        return round(num, 2)

    return None


# =========================================================
# KEY-VALUE EXTRACTION FROM TABLES / DL / COLON TEXT
# =========================================================

def extract_kv_from_soup(soup) -> Dict[str, str]:
    kv = {}

    # 1. Definition lists
    for dl in soup.find_all("dl"):
        dts = dl.find_all("dt")
        dds = dl.find_all("dd")
        for dt, dd in zip(dts, dds):
            k = dt.get_text(" ", strip=True)
            v = dd.get_text(" ", strip=True)
            if k and v and not is_noise_text(k):
                kv[k] = v

    # 2. Simple tables
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = row.find_all(["th", "td"])
            if len(cells) == 2:
                k = cells[0].get_text(" ", strip=True)
                v = cells[1].get_text(" ", strip=True)
                if k and v and not is_noise_text(k):
                    kv[k] = v

    # 3. Colon separated paragraphs / strong tags
    for tag in soup.find_all(["p", "li", "div", "span"]):
        text = tag.get_text(" ", strip=True)
        if ":" in text and len(text) < 300:
            parts = text.split(":", 1)
            if len(parts) == 2:
                k, v = parts[0].strip(), parts[1].strip()
                if k and v and len(k) < 60 and not is_noise_text(k):
                    kv[k] = v

    return kv


# =========================================================
# FINAL CLEANING BEFORE DATABASE
# =========================================================

def process_scheme(scheme: dict) -> dict:
    """
    Normalize + force correct types so MySQL never gets garbage.
    Call this right before insert/update.
    """
    if not isinstance(scheme, dict):
        return scheme

    # Text fields that can have paragraphs
    for k in ["details", "application_process", "documents_required", "exclusion", "eligibility", "benefits"]:
        if k in scheme:
            scheme[k] = normalize_text_field(scheme.get(k), preserve_paragraphs=True)

    # Short text fields
    for k in ["title", "department", "category", "state", "target_group", "gender", "status"]:
        if k in scheme:
            scheme[k] = normalize_text_field(scheme.get(k), preserve_paragraphs=False)

    # Force numeric fields
    for numf in ["min_age", "max_age"]:
        v = scheme.get(numf)
        if v is None or (isinstance(v, str) and not v.strip()):
            scheme[numf] = None
        else:
            try:
                scheme[numf] = int(float(v))
            except Exception:
                scheme[numf] = None

    for numf in ["min_income", "max_income"]:
        v = scheme.get(numf)
        if v is None or (isinstance(v, str) and not v.strip()):
            scheme[numf] = None
        else:
            try:
                val = float(v)
                # Reject absurdly small values that are clearly wrong
                if val < 50:
                    scheme[numf] = None
                else:
                    scheme[numf] = round(val, 2)
            except Exception:
                scheme[numf] = None

    # Force proper date fields
    for datef in ["start_date", "end_date", "launch_date", "last_date_to_apply"]:
        v = scheme.get(datef)
        if v:
            parsed = parse_date_str(str(v))
            scheme[datef] = parsed
        else:
            scheme[datef] = None

    # Application link
    if "application_link" in scheme:
        scheme["application_link"] = normalize_link(scheme.get("application_link"))

    # Default values
    scheme.setdefault("state", "Maharashtra")
    scheme.setdefault("gender", "All")
    scheme.setdefault("status", "Unknown")
    scheme.setdefault("category", "Government Scheme")

    return scheme