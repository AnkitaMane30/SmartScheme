from scraper.html_scraper import scrape_html
from utils.helpers import normalize_text_field
import re


def scrape_sport(url: str, base_scheme: dict = None) -> dict:
    scheme = base_scheme or scrape_html(url)

    if not scheme:
        return None

    # ---------- Domain defaults ----------
    scheme["category"] = "Sports & Youth Development"
    scheme["department"] = "Sports and Youth Services Department"
    scheme["state"] = "Maharashtra"
    scheme["target_group"] = "Athletes, Sportspersons and Youth"

    title = (scheme.get("title") or "").lower()

    if "scholarship" in title:
        scheme["category"] = "Sports Scholarship"
    elif "award" in title:
        scheme["category"] = "Sports Awards"
    elif any(x in title for x in ["self-defence", "swayamsiddha", "self defense"]):
        scheme["target_group"] = "Women and Girls"
    elif "khelo india" in title:
        scheme["category"] = "National Sports Scheme"
    elif any(x in title for x in ["olympic", "university", "training center", "complex"]):
        scheme["category"] = "Sports Infrastructure"

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

    # ---------- Rescue Benefits if it is empty ----------
    if not scheme.get("benefits") and scheme.get("details"):
        details = scheme["details"]

        # Try to extract benefits block from details
        match = re.search(
            r"(?:benefits|scheme benefits|financial assistance|incentive|support provided)[:\s]*(.*?)(?:eligibility|how to apply|application process|documents required|contact|$)",
            details,
            flags=re.IGNORECASE | re.DOTALL
        )
        if match:
            benefits_text = match.group(1).strip()
            if len(benefits_text) > 25:
                scheme["benefits"] = normalize_text_field(benefits_text, preserve_paragraphs=True)

    # ---------- Rescue Eligibility if it is empty ----------
    if not scheme.get("eligibility") and scheme.get("details"):
        details = scheme["details"]
        match = re.search(
            r"(?:eligibility|eligibility criteria|who can apply|who is eligible)[:\s]*(.*?)(?:benefits|how to apply|application process|documents required|contact|$)",
            details,
            flags=re.IGNORECASE | re.DOTALL
        )
        if match:
            elig_text = match.group(1).strip()
            if len(elig_text) > 25:
                scheme["eligibility"] = normalize_text_field(elig_text, preserve_paragraphs=True)

    # ---------- Final clean ----------
    for field in ["eligibility", "benefits", "documents_required", "application_process", "details"]:
        if scheme.get(field):
            scheme[field] = normalize_text_field(scheme[field], preserve_paragraphs=True)

    return scheme