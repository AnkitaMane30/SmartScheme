import requests
from bs4 import BeautifulSoup
import re
from scraper.html_scraper import scrape_html

def scrape_social(url, base_scheme=None):
    scheme = base_scheme or scrape_html(url)

    # Override defaults for social welfare schemes
    scheme["category"] = "Social Welfare Scheme"
    scheme["department"] = "Social Welfare Department"
    scheme["state"] = "Maharashtra"
    scheme["target_group"] = "Citizens"

    # If needed, fetch page for additional parsing
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

        # Expanded keyword detection for social welfare schemes (prioritize application keywords)
        if any(k in lower for k in ("how to apply", "application process", "procedure to apply", "apply online", "how to apply online")):
            current_section = "application_process"
        elif "objective" in lower or "overview" in lower or "features" in lower or "government resolution" in lower or "key conditions" in lower:
            current_section = "details"
        elif "beneficiary" in lower or "who can apply" in lower or "eligibility" in lower:
            current_section = "eligibility"
        elif "benefit" in lower or "stipend" in lower or "financial provision" in lower or "nature of benefits" in lower:
            current_section = "benefits"
        elif any(k in lower for k in ("document", "important documents", "documents required", "necessary documents")):
            current_section = "documents_required"
        elif "contact" in lower:
            current_section = "application_process"
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

    # Deduplicate repeated lines
    from utils.helpers import dedupe_preserve_order

    for fld in ("details", "eligibility", "benefits", "documents_required", "application_process", "exclusion"):
        if scheme.get(fld):
            scheme[fld] = dedupe_preserve_order(scheme[fld])

    return scheme
