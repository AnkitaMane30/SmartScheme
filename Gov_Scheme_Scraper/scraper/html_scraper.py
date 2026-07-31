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

def scrape_html(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    # -------------------------
    # BASIC FIELDS
    # -------------------------
    title = soup.find("h1")
    title = title.text.strip() if title else None

    # prefer main/article/content containers to avoid header/footer/sidebar noise
    content_div = find_main_content(soup, title)

    # remove common navigation/breadcrumb/footer nodes inside content_div
    for bad in content_div.select(".breadcrumb, nav, .nav, .site-nav, header, .breadcrumbs, .page-links, footer, .footer, .skip-link, .skip-to-content"):
        try:
            bad.decompose()
        except Exception:
            pass

    # Initialize as None (not empty string)
    details = None
    eligibility = None
    benefits = None
    documents_required = None
    application_process = None
    exclusion = None

    if content_div:
        elements = content_div.find_all(["h2", "h3", "p", "li", "strong"])
        current_section = "details"

        def collapse_duplicate_lines(text: str) -> str:
            # prefer helper dedupe function which preserves order
            return dedupe_preserve_order(text)

        for el in elements:
            text = el.get_text(" ", strip=True)
            if not text:
                continue
            lower = text.lower()

            # Section detection (prioritize application/process keywords before documents)
            if any(k in lower for k in ("how to apply", "application process", "procedure to apply", "apply online", "how to apply online", "how to apply:")):
                current_section = "application_process"
                continue
            if "eligibility" in lower or "who can apply" in lower:
                current_section = "eligibility"
                continue
            elif "benefit" in lower:
                current_section = "benefits"
                continue
            elif any(k in lower for k in ("document", "documents required", "important documents", "documents to be submitted", "necessary documents")):
                current_section = "documents_required"
                continue
            elif "application" in lower and "process" in lower:
                current_section = "application_process"
                continue
            elif "exclusion" in lower or "not eligible" in lower:
                current_section = "exclusion"
                continue

            # Skip known noise
            if is_noise_text(text):
                continue

            # Store text (avoid duplicates)
            if current_section == "details":
                prev = details or ""
                if text not in prev:
                    details = prev + ("\n" if prev else "") + text
            elif current_section == "eligibility":
                prev = eligibility or ""
                if text not in prev:
                    eligibility = prev + ("\n" if prev else "") + text
            elif current_section == "benefits":
                prev = benefits or ""
                if text not in prev:
                    benefits = prev + ("\n" if prev else "") + text
            elif current_section == "documents_required":
                prev = documents_required or ""
                if text not in prev:
                    documents_required = prev + ("\n" if prev else "") + text
            elif current_section == "application_process":
                prev = application_process or ""
                if text not in prev:
                    application_process = prev + ("\n" if prev else "") + text
            elif current_section == "exclusion":
                prev = exclusion or ""
                if text not in prev:
                    exclusion = prev + ("\n" if prev else "") + text

        # Collapse duplicate lines for multi-line fields
        if details:
            details = collapse_duplicate_lines(details)
        if eligibility:
            eligibility = collapse_duplicate_lines(eligibility)
        if benefits:
            benefits = collapse_duplicate_lines(benefits)
        if documents_required:
            documents_required = collapse_duplicate_lines(documents_required)
        if application_process:
            application_process = collapse_duplicate_lines(application_process)
        if exclusion:
            exclusion = collapse_duplicate_lines(exclusion)

    # -------------------------
    # SMART EXTRACTION (REGEX)
    # -------------------------
    min_age = max_age = None
    min_income = max_income = None
    last_date = None

    text_all = (details or "") + (eligibility or "") + (benefits or "") + (application_process or "")

    # Age detection
    age_match = re.findall(r'(\d{2})\s*-\s*(\d{2})\s*years', text_all)
    if age_match:
        min_age, max_age = age_match[0]

    # Income detection
    income_match = re.findall(r'₹?\s*(\d+[,0-9]*)', text_all)
    if income_match:
        min_income = income_match[0]

    # Date detection (basic)
    date_match = re.search(r'(\d{2}/\d{2}/\d{4})', text_all)
    if date_match:
        last_date = date_match.group(1)

    # -------------------------
    # STATUS DETECTION
    # -------------------------
    status = None
    if re.search(r'\b(active|ongoing|currently implemented)\b', text_all.lower()):
        status = "Active"
    elif re.search(r'\b(closed|discontinued|expired|inactive)\b', text_all.lower()):
        status = "Inactive"
    else:
        status = "Unknown"

    # -------------------------
    # DEFAULT / FIXED VALUES
    # -------------------------
    # Try to extract structured key/value pairs (tables, dl, colon-paragraphs)
    kv = extract_kv_from_soup(soup)

    scheme = {
        "title": title,
        "details": details[:3000] if details else None,
        "eligibility": eligibility[:1500] if eligibility else None,
        "benefits": benefits[:1500] if benefits else None,
        "exclusion": exclusion[:1000] if exclusion else None,
        "documents_required": documents_required[:1500] if documents_required else None,
        "application_process": application_process[:1500] if application_process else None,

        "category": "Government Scheme",
        "state": "Maharashtra",
        "department": None,   # Neutral here, overridden in domain-specific scrapers
        "status": status,     # Dynamic detection

        "start_date": None,
        "end_date": None,
        "launch_date": None,

        "min_income": min_income,
        "max_income": max_income,

        "gender": "All",
        "min_age": min_age,
        "max_age": max_age,

        "target_group": "Citizens",
        "last_date_to_apply": last_date,

        "application_link": url
    }

    # Map common KV fields into scheme when present
    if kv:
        for k, v in kv.items():
            lower_k = k.lower()
            if any(x in lower_k for x in ("last date", "last date to apply", "last date of application", "closing date", "closing on")):
                scheme["last_date_to_apply"] = scheme.get("last_date_to_apply") or parse_date_str(v)
            if "start date" in lower_k or "commenc" in lower_k or "from" == lower_k.strip():
                scheme["start_date"] = scheme.get("start_date") or parse_date_str(v)
            if "end date" in lower_k or "valid until" in lower_k or "upto" in lower_k:
                scheme["end_date"] = scheme.get("end_date") or parse_date_str(v)
            # handle generic 'date' fields that may contain a range like '05/06/2025 - 30/06/2026'
            if "date" == lower_k or lower_k.strip().startswith("date"):
                s_dt, e_dt = parse_date_range(v)
                if s_dt and e_dt:
                    scheme["start_date"] = scheme.get("start_date") or s_dt
                    scheme["end_date"] = scheme.get("end_date") or e_dt
                elif s_dt:
                    # single date: prefer last_date_to_apply if it mentions closing, else set start_date
                    scheme["start_date"] = scheme.get("start_date") or s_dt
            if "department" in k:
                scheme["department"] = scheme.get("department") or normalize_text_field(v)
            # application process / how to apply mapping (priority)
            if any(x in lower_k for x in ("how to apply", "application process", "procedure to apply", "apply online", "how to apply online", "method of application", "how to apply:")):
                scheme["application_process"] = scheme.get("application_process") or normalize_text_field(v)
            if "eligib" in k or "who can" in k:
                scheme["eligibility"] = scheme.get("eligibility") or normalize_text_field(v)
            if "benefit" in k or "amount" in k:
                scheme["benefits"] = scheme.get("benefits") or normalize_text_field(v)
            if any(x in lower_k for x in ("document", "documents required", "important documents", "documents to be submitted", "necessary documents")):
                scheme["documents_required"] = scheme.get("documents_required") or normalize_text_field(v)
            if "age" in k:
                a_min, a_max = parse_age_range(v)
                scheme["min_age"] = scheme.get("min_age") or a_min
                scheme["max_age"] = scheme.get("max_age") or a_max
            if "income" in k or "annual income" in k:
                n = parse_currency(v)
                scheme["min_income"] = scheme.get("min_income") or n

    return scheme
