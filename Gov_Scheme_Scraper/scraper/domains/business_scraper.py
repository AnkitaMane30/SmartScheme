import re
import requests
from bs4 import BeautifulSoup
from scraper.html_scraper import scrape_html
from utils.helpers import (
    extract_kv_from_soup,
    find_main_content,
    is_noise_text,
    dedupe_preserve_order,
    normalize_text_field
)


def scrape_business(url, base_scheme=None):
    scheme = base_scheme or scrape_html(url)

    scheme["category"] = "Business Scheme"
    scheme["department"] = "MSME / Industry Department"
    scheme["state"] = "India"
    scheme["target_group"] = "Entrepreneurs / MSMEs"

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception:
        soup = None

    if soup:
        def extract_nested_text(tag):
            return tag.get_text(" ", strip=True) if tag else ""

        content_div = find_main_content(soup, scheme.get("title")) or soup

        elements = content_div.find_all([
            "h1",
            "h2",
            "h3",
            "h4",
            "p",
            "li",
            "strong",
            "td",
            "tr",
            "div",
            "span",
            "ul",
            "ol"
        ])

        current_section = "details"

        for el in elements:
            text = extract_nested_text(el)

            if not text:
                continue

            lower = text.lower()

            if any(k in lower for k in (
                "how to apply",
                "application process",
                "procedure to apply",
                "apply online",
                "online application",
                "apply here",
                "application form",
                "submit application",
                "register"
            )):
                current_section = "application_process"
                continue

            if any(k in lower for k in (
                "eligibility",
                "who can apply",
                "beneficiary",
                "applicant",
                "qualification"
            )):
                current_section = "eligibility"
                continue

            if any(k in lower for k in (
                "benefit",
                "subsidy",
                "incentive",
                "support",
                "assistance",
                "financial provision",
                "loan"
            )):
                current_section = "benefits"
                continue

            if any(k in lower for k in (
                "document",
                "documents required",
                "important documents",
                "necessary documents",
                "mandatory documents",
                "proof"
            )):
                current_section = "documents_required"
                continue

            if any(k in lower for k in (
                "overview",
                "objective",
                "purpose",
                "about",
                "scope",
                "introduction",
                "scheme details"
            )):
                current_section = "details"
                continue

            if any(k in lower for k in (
                "exclusion",
                "not eligible",
                "ineligible"
            )):
                current_section = "exclusion"
                continue

            if is_noise_text(text):
                continue

            if len(text.split()) <= 2:
                continue

            if lower in (
                "benefits",
                "eligibility",
                "documents required",
                "application process",
                "overview",
                "details",
                "objective",
                "purpose",
                "about",
                "scope",
                "exclusion"
            ):
                continue

            if current_section == "details":
                scheme["details"] = (scheme.get("details") or "") + text + "\n"
            elif current_section == "eligibility":
                scheme["eligibility"] = (scheme.get("eligibility") or "") + text + "\n"
            elif current_section == "benefits":
                scheme["benefits"] = (scheme.get("benefits") or "") + text + "\n"
            elif current_section == "documents_required":
                scheme["documents_required"] = (scheme.get("documents_required") or "") + text + "\n"
            elif current_section == "application_process":
                scheme["application_process"] = (scheme.get("application_process") or "") + text + "\n"
            elif current_section == "exclusion":
                scheme["exclusion"] = (scheme.get("exclusion") or "") + text + "\n"

        if not scheme.get("details"):
            paras = content_div.find_all("p")
            collected = []
            for p in paras[:5]:
                txt = extract_nested_text(p)
                if txt and not is_noise_text(txt) and len(txt.split()) >= 4:
                    collected.append(txt)
            scheme["details"] = "\n".join(collected)

        kv = extract_kv_from_soup(soup)
        for k, v in kv.items():
            lower_k = k.lower()
            if any(x in lower_k for x in ("how to apply", "application process", "procedure to apply", "apply online", "application form")):
                scheme["application_process"] = scheme.get("application_process") or normalize_text_field(v, preserve_paragraphs=True)
            if any(x in lower_k for x in ("eligib", "who can")):
                scheme["eligibility"] = scheme.get("eligibility") or normalize_text_field(v, preserve_paragraphs=True)
            if any(x in lower_k for x in ("benefit", "subsidy", "amount", "support")):
                scheme["benefits"] = scheme.get("benefits") or normalize_text_field(v, preserve_paragraphs=True)
            if any(x in lower_k for x in ("document", "documents required", "necessary documents")):
                scheme["documents_required"] = scheme.get("documents_required") or normalize_text_field(v, preserve_paragraphs=True)

    for fld in ("details", "eligibility", "benefits", "documents_required", "application_process", "exclusion"):
        if scheme.get(fld):
            scheme[fld] = dedupe_preserve_order(scheme[fld])
            scheme[fld] = scheme[fld].strip() or None

    return scheme
