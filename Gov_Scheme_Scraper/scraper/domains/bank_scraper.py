import requests
from bs4 import BeautifulSoup
import re
from scraper.html_scraper import scrape_html
from utils.helpers import extract_kv_from_soup, parse_date_str, parse_currency, parse_age_range, normalize_text_field

def scrape_bank(url, base_scheme=None):
    scheme = base_scheme or scrape_html(url)

    # Override defaults for banking schemes
    scheme["category"] = "Banking/Financial Scheme"
    scheme["department"] = "Finance/Banking Department"
    scheme["state"] = "Maharashtra"
    scheme["target_group"] = "Citizens"

    # If we already have a base HTML scrape, avoid fetching again
    if base_scheme is None:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
    else:
        # Try to reuse parsed HTML if available in base_scheme (not provided currently)
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

    # Helper: recursively extract text from nested tags
    def extract_nested_text(tag):
        return tag.get_text(" ", strip=True) if tag else ""

    # Collect text from headings, paragraphs, lists, divs, spans, and tables
    elements = soup.find_all(["h2","h3","p","li","strong","td","tr","div","span","ul"])
    current_section = "details"

    for el in elements:
        text = extract_nested_text(el)
        lower = text.lower()

        # Expanded keyword detection (prioritize application/process over documents)
        if any(k in lower for k in ("how to apply", "application process", "procedure to apply", "apply online", "how to apply online")):
            current_section = "application_process"
        elif "objective" in lower or "overview" in lower or "features" in lower:
            current_section = "details"
        elif "beneficiary" in lower or "who can apply" in lower or "eligibility" in lower:
            current_section = "eligibility"
        elif "benefit" in lower or "stipend" in lower or "financial provision" in lower:
            current_section = "benefits"
        elif any(k in lower for k in ("document", "documents required", "important documents", "necessary documents")):
            current_section = "documents_required"
        elif "exclusion" in lower:
            current_section = "exclusion"

        # Store text into the right field
        if current_section == "details":
            scheme["details"] = (scheme["details"] or "") + text + "\n"
        elif current_section == "eligibility":
            scheme["eligibility"] = (scheme["eligibility"] or "") + text + "\n"
        elif current_section == "benefits":
            scheme["benefits"] = (scheme["benefits"] or "") + text + "\n"
        elif current_section == "documents_required":
            scheme["documents_required"] = (scheme["documents_required"] or "") + text + "\n"
        elif current_section == "application_process":
            scheme["application_process"] = (scheme["application_process"] or "") + text + "\n"
        elif current_section == "exclusion":
            scheme["exclusion"] = (scheme["exclusion"] or "") + text + "\n"

    # 🔹 Fallbacks for details
    if not scheme["details"]:
        # Try UL lists
        ul = soup.find("ul")
        if ul:
            scheme["details"] = "\n".join([extract_nested_text(li) for li in ul.find_all("li")])

    if not scheme["details"]:
        # Try main content divs
        main = soup.find("div", class_="scheme-content") or soup.find("div", class_="entry-content") or soup.find("div", id="content")
        if main:
            scheme["details"] = extract_nested_text(main)[:3000]

    if not scheme["details"]:
        # Try tables
        rows = soup.find_all("tr")
        if rows:
            scheme["details"] = "\n".join([extract_nested_text(row) for row in rows[:5]])

    if not scheme["details"]:
        # Last fallback: first few paragraphs
        paras = soup.find_all("p")
        if paras:
            scheme["details"] = "\n".join([extract_nested_text(p) for p in paras[:3]])

    # Structured KV extraction
    kv = extract_kv_from_soup(soup)
    for k, v in kv.items():
        if "department" in k:
            scheme["department"] = scheme.get("department") or normalize_text_field(v)
        if any(x in k for x in ("how to apply", "application process", "procedure to apply", "apply online", "how to apply online", "method of application")):
            scheme["application_process"] = scheme.get("application_process") or normalize_text_field(v)
        if any(x in k for x in ("last date", "last date to apply", "last date of application")):
            scheme["last_date_to_apply"] = scheme.get("last_date_to_apply") or parse_date_str(v)
        if "start date" in k:
            scheme["start_date"] = scheme.get("start_date") or parse_date_str(v)
        if "end date" in k or "valid until" in k:
            scheme["end_date"] = scheme.get("end_date") or parse_date_str(v)
        if "eligib" in k:
            scheme["eligibility"] = scheme.get("eligibility") or normalize_text_field(v)
        if "benefit" in k or "amount" in k:
            scheme["benefits"] = scheme.get("benefits") or normalize_text_field(v)
        if "age" in k:
            a_min, a_max = parse_age_range(v)
            scheme["min_age"] = scheme.get("min_age") or a_min
            scheme["max_age"] = scheme.get("max_age") or a_max
        if "income" in k:
            n = parse_currency(v)
            scheme["min_income"] = scheme.get("min_income") or n

    # Deduplicate repeated lines in text fields
    from utils.helpers import dedupe_preserve_order

    for fld in ("details", "eligibility", "benefits", "documents_required", "application_process", "exclusion"):
        if scheme.get(fld):
            scheme[fld] = dedupe_preserve_order(scheme[fld])

    return scheme
