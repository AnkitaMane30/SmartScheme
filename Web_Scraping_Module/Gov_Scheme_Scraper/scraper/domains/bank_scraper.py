from scraper.html_scraper import scrape_html
from utils.helpers import normalize_text_field
import re


def scrape_bank(url: str, base_scheme: dict = None) -> dict:
    scheme = base_scheme or scrape_html(url)

    if not scheme:
        return None

    # ---------- Domain defaults ----------
    scheme["category"] = "Financial Inclusion / Banking"
    scheme["department"] = "Finance / Cooperative / Agriculture Department"
    scheme["state"] = "Maharashtra"
    scheme["target_group"] = "Citizens, Farmers, Women, Small Entrepreneurs"

    title = (scheme.get("title") or "").lower()

    if any(x in title for x in ["kisan", "credit card", "kcc"]):
        scheme["category"] = "Agriculture Credit"
        scheme["target_group"] = "Farmers"
        scheme["department"] = "Agriculture / Animal Husbandry Department"
    elif any(x in title for x in ["mahila", "women", "samriddhi"]):
        scheme["target_group"] = "Women / Women Entrepreneurs"
    elif any(x in title for x in ["pmjdy", "jan dhan"]):
        scheme["target_group"] = "All Citizens (especially unbanked)"
    elif any(x in title for x in ["vayoshree", "senior", "old age"]):
        scheme["target_group"] = "Senior Citizens"
        scheme["category"] = "Social Security / Senior Citizen"
    elif any(x in title for x in ["yuva", "karya", "prashikshan", "cmykpy"]):
        scheme["category"] = "Skill Development / Training"
        scheme["target_group"] = "Youth (18-35 years)"
        scheme["department"] = "Skill Development, Employment & Entrepreneurship"

    # ---------- Clean weak placeholder text ----------
    weak_phrases = [
        "as mentioned above", "mentioned above", "as above", "refer above",
        "see above", "link mentioned above", "contact the relevant department",
        "contact the department", "details as above", "as per scheme guidelines"
    ]

    for field in ["eligibility", "benefits", "documents_required", "application_process", "exclusion", "details"]:
        value = scheme.get(field)
        if value:
            lower_val = value.lower().strip()
            if any(p == lower_val or lower_val.startswith(p) for p in weak_phrases):
                scheme[field] = None
            else:
                cleaned = value
                for p in weak_phrases:
                    cleaned = re.sub(re.escape(p), "", cleaned, flags=re.IGNORECASE)
                scheme[field] = normalize_text_field(cleaned, preserve_paragraphs=True)

    # ---------- Extra: Rescue Eligibility if it is still empty ----------
    if not scheme.get("eligibility") and scheme.get("details"):
        details = scheme["details"]
        # Look for eligibility block inside details
        match = re.search(
            r"(?:eligibility criteria|for candidates|eligibility)[:\s]*(.*?)(?:contact information|for industries|benefits|how to apply|$)",
            details,
            flags=re.IGNORECASE | re.DOTALL
        )
        if match:
            elig_text = match.group(1).strip()
            if len(elig_text) > 30:
                scheme["eligibility"] = normalize_text_field(elig_text, preserve_paragraphs=True)

    # ---------- Final clean ----------
    for field in ["eligibility", "benefits", "documents_required", "application_process", "details"]:
        if scheme.get(field):
            scheme[field] = normalize_text_field(scheme[field], preserve_paragraphs=True)

    return scheme