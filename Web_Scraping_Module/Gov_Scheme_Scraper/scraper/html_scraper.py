import requests
from bs4 import BeautifulSoup
import re
from utils.helpers import (
    extract_kv_from_soup,
    parse_date_str,
    parse_date_range,
    parse_currency,
    parse_age_range,
    normalize_text_field,
    is_noise_text,
    dedupe_preserve_order,
    find_main_content,
)


def scrape_html(url: str) -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or "utf-8"
    except Exception as e:
        print(f"[html_scraper] Request failed for {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # -------------------------
    # TITLE
    # -------------------------
    title = None
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(" ", strip=True)
    if not title:
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(" ", strip=True).split("|")[0].split("-")[0].strip()

    title = normalize_text_field(title)

    # -------------------------
    # MAIN CONTENT
    # -------------------------
    content_div = find_main_content(soup, title)

    # Remove common noise elements
    for bad_sel in [
        ".breadcrumb", "nav", ".nav", ".site-nav", "header",
        ".breadcrumbs", ".page-links", "footer", ".footer",
        ".skip-link", ".skip-to-content", ".share", ".social-share",
        ".sidebar", ".widget", ".related-posts", ".comments"
    ]:
        for el in content_div.select(bad_sel):
            try:
                el.decompose()
            except Exception:
                pass

   
         # -------------------------
    # SECTION EXTRACTION (Final Strong Version)
    # -------------------------
    details = None
    eligibility = None
    benefits = None
    documents_required = None
    application_process = None
    exclusion = None

    SECTION_MAP = [
        (["how to apply", "application process", "procedure to apply", "apply online",
          "application procedure", "steps to apply", "method of application",
          "online application", "application form"], "application_process"),

        (["eligibility criteria", "who can apply", "eligibility", "who is eligible",
          "eligible", "beneficiary", "applicant criteria", "eligibility conditions"], "eligibility"),

        (["documents required", "important documents", "necessary documents",
          "mandatory documents", "required documents", "list of documents",
          "documents to be submitted"], "documents_required"),

        (["scheme benefits", "financial assistance", "benefits", "benefit",
          "subsidy", "incentive", "support provided", "assistance provided"], "benefits"),

        (["exclusion", "not eligible", "ineligible", "who cannot apply", "exceptions"], "exclusion"),

        (["overview", "objective", "purpose", "about the scheme", "introduction",
          "scheme details", "description", "about"], "details"),
    ]

    current_section = "details"
    elements = content_div.find_all(["h1", "h2", "h3", "h4", "p", "li", "strong", "div", "span"])

    def detect_section(text: str):
        """Return (section_name, is_pure_heading)"""
        lower = text.lower().strip()
        word_count = len(text.split())

        for keywords, section_name in SECTION_MAP:
            for kw in keywords:
                # Case 1: pure heading
                if lower == kw or lower == kw + ":":
                    return section_name, True

                # Case 2: starts with heading keyword (most important fix)
                if lower.startswith(kw) and word_count <= 12:
                    return section_name, True

                # Case 3: short text containing the keyword
                if kw in lower and word_count <= 6:
                    return section_name, True

        return None, False

    for el in elements:
        text = el.get_text(" ", strip=True)
        if not text or len(text) < 3:
            continue

        matched_section, is_heading = detect_section(text)

        if matched_section:
            current_section = matched_section
            # Never store pure headings
            if is_heading:
                continue

        if is_noise_text(text):
            continue

        if len(text.split()) <= 2 and current_section != "documents_required":
            continue

        # Store content
        if current_section == "details":
            details = (details or "") + text + "\n"
        elif current_section == "eligibility":
            eligibility = (eligibility or "") + text + "\n"
        elif current_section == "benefits":
            benefits = (benefits or "") + text + "\n"
        elif current_section == "documents_required":
            documents_required = (documents_required or "") + text + "\n"
        elif current_section == "application_process":
            application_process = (application_process or "") + text + "\n"
        elif current_section == "exclusion":
            exclusion = (exclusion or "") + text + "\n"

    # ---------- SAFETY CLEANING (very important) ----------
    def clean_wrong_section(text, forbidden_starts):
        if not text:
            return text
        lower = text.lower().strip()
        for start in forbidden_starts:
            if lower.startswith(start):
                return None
        return text

    benefits = clean_wrong_section(benefits, ["how to apply", "application process", "eligibility", "documents required"])
    eligibility = clean_wrong_section(eligibility, ["how to apply", "application process", "benefits", "documents required"])
    application_process = clean_wrong_section(application_process, ["benefits", "eligibility", "documents required"])
    documents_required = clean_wrong_section(documents_required, ["how to apply", "benefits", "eligibility"])

    # Clean duplicates
    details = dedupe_preserve_order(details)
    eligibility = dedupe_preserve_order(eligibility)
    benefits = dedupe_preserve_order(benefits)
    documents_required = dedupe_preserve_order(documents_required)
    application_process = dedupe_preserve_order(application_process)
    exclusion = dedupe_preserve_order(exclusion)

    # Fallback for details
    if not details:
        paras = []
        for p in content_div.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if txt and not is_noise_text(txt) and len(txt.split()) >= 6:
                paras.append(txt)
            if len(paras) >= 5:
                break
        details = "\n".join(paras) if paras else None
    # -------------------------
    # STRUCTURED KEY-VALUE EXTRACTION
    # -------------------------
    kv = extract_kv_from_soup(soup)

    # -------------------------
    # SMART NUMERIC / DATE EXTRACTION
    # -------------------------
    all_text = " ".join(filter(None, [
        details, eligibility, benefits, application_process, documents_required
    ]))

    min_age, max_age = parse_age_range(all_text)
    min_income = parse_currency(all_text)   # will return None if suspicious

    # Status detection
    status = "Unknown"
    lower_all = all_text.lower()
    if re.search(r"\b(active|ongoing|currently implemented|open)\b", lower_all):
        status = "Active"
    elif re.search(r"\b(closed|discontinued|expired|inactive)\b", lower_all):
        status = "Inactive"

    # -------------------------
    # BUILD FINAL SCHEME DICT
    # -------------------------
    scheme = {
        "title": title,
        "details": details[:4000] if details else None,
        "eligibility": eligibility[:2000] if eligibility else None,
        "benefits": benefits[:2000] if benefits else None,
        "exclusion": exclusion[:1500] if exclusion else None,
        "documents_required": documents_required[:2000] if documents_required else None,
        "application_process": application_process[:2000] if application_process else None,

        "category": "Government Scheme",
        "state": "Maharashtra",
        "department": None,
        "status": status,

        "start_date": None,
        "end_date": None,
        "launch_date": None,

        "min_income": min_income,
        "max_income": None,

        "gender": "All",
        "min_age": min_age,
        "max_age": max_age,

        "target_group": "Citizens",
        "last_date_to_apply": None,

        "application_link": url
    }

    # Map useful key-value pairs
    if kv:
        for k, v in kv.items():
            lower_k = k.lower().strip()

            if any(x in lower_k for x in ("last date", "closing date", "last date to apply", "last date of application")):
                scheme["last_date_to_apply"] = scheme.get("last_date_to_apply") or parse_date_str(v)

            if any(x in lower_k for x in ("start date", "commencement", "from date")):
                scheme["start_date"] = scheme.get("start_date") or parse_date_str(v)

            if any(x in lower_k for x in ("end date", "valid until", "upto", "to date")):
                scheme["end_date"] = scheme.get("end_date") or parse_date_str(v)

            if lower_k in ("date", "scheme date") or lower_k.startswith("date"):
                s_dt, e_dt = parse_date_range(v)
                if s_dt and e_dt:
                    scheme["start_date"] = scheme.get("start_date") or s_dt
                    scheme["end_date"] = scheme.get("end_date") or e_dt
                elif s_dt:
                    scheme["start_date"] = scheme.get("start_date") or s_dt

            if "department" in lower_k:
                scheme["department"] = scheme.get("department") or normalize_text_field(v)

            if any(x in lower_k for x in ("how to apply", "application process", "procedure")):
                scheme["application_process"] = scheme.get("application_process") or normalize_text_field(v, preserve_paragraphs=True)

            if "eligib" in lower_k or "who can" in lower_k:
                scheme["eligibility"] = scheme.get("eligibility") or normalize_text_field(v, preserve_paragraphs=True)

            if any(x in lower_k for x in ("benefit", "subsidy", "assistance", "amount")):
                scheme["benefits"] = scheme.get("benefits") or normalize_text_field(v, preserve_paragraphs=True)

            if any(x in lower_k for x in ("document", "documents required")):
                scheme["documents_required"] = scheme.get("documents_required") or normalize_text_field(v, preserve_paragraphs=True)

            if "age" in lower_k:
                a_min, a_max = parse_age_range(v)
                scheme["min_age"] = scheme.get("min_age") or a_min
                scheme["max_age"] = scheme.get("max_age") or a_max

            if "income" in lower_k or "annual income" in lower_k:
                val = parse_currency(v)
                if val:
                    scheme["min_income"] = scheme.get("min_income") or val

    return scheme