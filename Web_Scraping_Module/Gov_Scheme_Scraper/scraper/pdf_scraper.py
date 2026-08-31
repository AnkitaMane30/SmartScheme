import io
import re
import requests
import pdfplumber
from utils.helpers import normalize_text_field, is_noise_text


def scrape_pdf(url: str) -> dict:
    """
    Download PDF → extract text → return structured scheme dict
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=25)
        resp.raise_for_status()
    except Exception as e:
        print(f"[pdf_scraper] Download failed: {e}")
        return None

    # Extract text from all pages
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
            pages = []
            for page in pdf.pages:
                try:
                    pages.append(page.extract_text() or "")
                except Exception:
                    pages.append("")
            text = "\n".join(pages)
    except Exception as e:
        print(f"[pdf_scraper] Text extraction failed: {e}")
        return None

    if not text or len(text.strip()) < 50:
        return None

    # Clean lines
    lines = []
    for ln in text.splitlines():
        ln = ln.strip()
        if ln and len(ln) > 2:
            lines.append(ln)

    if not lines:
        return None

    title = lines[0]

    # ---------- Strong Section Detection ----------
    SECTION_MAP = [
        (["how to apply", "application process", "procedure", "mode of application",
          "application procedure", "where to apply"], "application_process"),
        (["eligibility", "who can apply", "eligible persons", "beneficiary",
          "who is eligible", "eligibility criteria"], "eligibility"),
        (["documents required", "required documents", "list of documents",
          "documents to be submitted"], "documents_required"),
        (["benefits", "scheme benefits", "financial assistance", "compensation",
          "relief", "assistance provided"], "benefits"),
        (["exclusion", "not eligible", "ineligible"], "exclusion"),
        (["objective", "introduction", "about the scheme", "purpose",
          "scheme details", "overview"], "details"),
    ]

    details = eligibility = benefits = documents_required = application_process = exclusion = None
    current = "details"

    for line in lines[1:]:  # skip title
        lower = line.lower().strip()
        word_count = len(line.split())

        matched = None
        if word_count <= 10:
            for keywords, section in SECTION_MAP:
                for kw in keywords:
                    if lower == kw or lower.startswith(kw) or (kw in lower and word_count <= 6):
                        matched = section
                        break
                if matched:
                    break

        if matched:
            current = matched
            continue

        if is_noise_text(line):
            continue

        if current == "details":
            details = (details or "") + line + "\n"
        elif current == "eligibility":
            eligibility = (eligibility or "") + line + "\n"
        elif current == "benefits":
            benefits = (benefits or "") + line + "\n"
        elif current == "documents_required":
            documents_required = (documents_required or "") + line + "\n"
        elif current == "application_process":
            application_process = (application_process or "") + line + "\n"
        elif current == "exclusion":
            exclusion = (exclusion or "") + line + "\n"

    # Fallback: if details is empty, take first few paragraphs
    if not details:
        details = "\n".join(lines[1:15])

    scheme = {
        "title": title,
        "details": normalize_text_field(details, preserve_paragraphs=True) if details else None,
        "eligibility": normalize_text_field(eligibility, preserve_paragraphs=True) if eligibility else None,
        "benefits": normalize_text_field(benefits, preserve_paragraphs=True) if benefits else None,
        "documents_required": normalize_text_field(documents_required, preserve_paragraphs=True) if documents_required else None,
        "application_process": normalize_text_field(application_process, preserve_paragraphs=True) if application_process else None,
        "exclusion": normalize_text_field(exclusion, preserve_paragraphs=True) if exclusion else None,
        "category": "Government Scheme",
        "state": "Maharashtra",
        "department": None,
        "status": "Unknown",
        "start_date": None,
        "end_date": None,
        "launch_date": None,
        "min_income": None,
        "max_income": None,
        "gender": "All",
        "min_age": None,
        "max_age": None,
        "target_group": "Citizens",
        "last_date_to_apply": None,
        "application_link": url,
    }

    return scheme