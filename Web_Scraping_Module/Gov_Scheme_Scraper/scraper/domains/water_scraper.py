from scraper.html_scraper import scrape_html
from bs4 import BeautifulSoup
import requests
from utils.helpers import normalize_text_field, is_noise_text


def scrape_water(url: str, base_scheme: dict = None) -> dict:
    scheme = base_scheme or scrape_html(url)

    if not scheme:
        return None

    # Domain defaults
    scheme["category"] = "Water & Sanitation"
    scheme["department"] = "Water Resources / Water Supply and Sanitation Department"
    scheme["state"] = "Maharashtra"
    scheme["target_group"] = "Rural and Urban Citizens"

    # --------------------------------------------------
    # Extra extraction for water.maharashtra.gov.in pages
    # --------------------------------------------------
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        # 1. Remove weak placeholder text from benefits / eligibility / process
        weak_phrases = [
            "as mentioned above",
            "link mentioned above",
            "mentioned above",
            "as above",
            "refer above",
            "see above"
        ]

        for field in ["benefits", "eligibility", "application_process", "documents_required"]:
            value = scheme.get(field)
            if value and any(p in value.lower() for p in weak_phrases):
                scheme[field] = None

        # 2. Extract useful text from tables (Progress / Components / Benefits style tables)
        table_texts = []
        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            if len(rows) < 2:
                continue

            for row in rows[1:]:  # skip header
                cells = [td.get_text(" ", strip=True) for td in row.find_all(["td", "th"])]
                cells = [c for c in cells if c and not is_noise_text(c)]
                if cells:
                    table_texts.append(" | ".join(cells))

        if table_texts:
            table_summary = "\n".join(table_texts[:15])  # limit size

            # If benefits is empty, put table summary there
            if not scheme.get("benefits"):
                scheme["benefits"] = table_summary
            else:
                # Append table info to details if benefits already has something
                current_details = scheme.get("details") or ""
                scheme["details"] = (current_details + "\n\nProgress / Components:\n" + table_summary).strip()

        # 3. Extra: Look for bullet points that look like benefits
        if not scheme.get("benefits"):
            benefit_candidates = []
            for li in soup.find_all("li"):
                text = li.get_text(" ", strip=True)
                if text and len(text) > 25 and not is_noise_text(text):
                    lower = text.lower()
                    if any(k in lower for k in ["fund", "₹", "rs.", "benefit", "assistance", "eligible", "provide", "support"]):
                        benefit_candidates.append(text)

            if benefit_candidates:
                scheme["benefits"] = "\n".join(benefit_candidates[:8])

    except Exception as e:
        print(f"[water_scraper] Extra extraction failed: {e}")

    # Final clean
    for field in ["benefits", "eligibility", "details", "application_process"]:
        if scheme.get(field):
            scheme[field] = normalize_text_field(scheme[field], preserve_paragraphs=True)

    return scheme