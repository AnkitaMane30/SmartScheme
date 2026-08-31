from scraper.html_scraper import scrape_html
from utils.helpers import normalize_text_field, parse_age_range
import re


def scrape_social(url: str, base_scheme: dict = None) -> dict:
    scheme = base_scheme or scrape_html(url)

    if not scheme:
        return None

    # ---------- Domain defaults ----------
    scheme["category"] = "Social Welfare"
    scheme["department"] = "Social Justice and Special Assistance Department"
    scheme["state"] = "Maharashtra"
    scheme["target_group"] = "Scheduled Castes, Neo-Buddhists and Weaker Sections"

    title = (scheme.get("title") or "").lower()
    details = (scheme.get("details") or "").lower()

    # Better target group based on title
    if "scholarship" in title:
        scheme["category"] = "Scholarship / Education"
        scheme["target_group"] = "SC / Backward Class Students"
    elif "hostel" in title:
        scheme["target_group"] = "SC / Neo-Buddhist Students"
    elif "senior" in title or "old age" in title:
        scheme["target_group"] = "Senior Citizens"
    elif "transgender" in title:
        scheme["target_group"] = "Transgender Persons"
    elif "housing" in title or "ramai" in title:
        scheme["category"] = "Housing"
        scheme["target_group"] = "SC / Neo-Buddhist Families"
    elif "de-addiction" in title or "nasha" in title or "drug" in title:
        scheme["category"] = "Health / De-addiction"
        scheme["target_group"] = "Persons affected by substance abuse"

    # ---------- Clean weak / placeholder text ----------
    weak_phrases = [
        "as mentioned above",
        "mentioned above",
        "as above",
        "refer above",
        "see above",
        "link mentioned above",
        "contact the relevant department",
        "contact the department"
    ]

    for field in ["eligibility", "benefits", "documents_required", "application_process", "exclusion"]:
        value = scheme.get(field)
        if value:
            lower_val = value.lower().strip()
            # If the whole field is just a weak phrase → clear it
            if any(p == lower_val or lower_val.startswith(p) for p in weak_phrases):
                scheme[field] = None
            else:
                # Remove weak phrases from inside the text
                for p in weak_phrases:
                    value = re.sub(re.escape(p), "", value, flags=re.IGNORECASE)
                scheme[field] = normalize_text_field(value, preserve_paragraphs=True)

    # ---------- Strict Age Extraction ----------
    # Only keep age if it clearly appears as an eligibility condition
    age_text = " ".join(filter(None, [
        scheme.get("eligibility"),
        scheme.get("details")
    ]))

    min_age, max_age = None, None

    if age_text:
        # Only accept age if words like "age", "years", "aged" are present nearby
        age_patterns = [
            r"(?:age|aged|years?)\s*(?:of\s*)?(\d{1,2})\s*(?:-|to|–)\s*(\d{1,2})",
            r"(\d{1,2})\s*(?:-|to|–)\s*(\d{1,2})\s*years?",
            r"(?:above|over|more than|from)\s*(\d{1,2})\s*years?",
            r"(?:below|under|upto|up to|less than)\s*(\d{1,2})\s*years?",
        ]

        for pattern in age_patterns:
            match = re.search(pattern, age_text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 2 and groups[0] and groups[1]:
                    min_age = int(groups[0])
                    max_age = int(groups[1])
                elif len(groups) == 1:
                    # Decide min or max based on words
                    if re.search(r"(above|over|more than|from)", match.group(0), re.I):
                        min_age = int(groups[0])
                    else:
                        max_age = int(groups[0])
                break

    scheme["min_age"] = min_age
    scheme["max_age"] = max_age

    # ---------- Final clean ----------
    for field in ["eligibility", "benefits", "documents_required", "application_process", "details"]:
        if scheme.get(field):
            scheme[field] = normalize_text_field(scheme[field], preserve_paragraphs=True)

    return scheme