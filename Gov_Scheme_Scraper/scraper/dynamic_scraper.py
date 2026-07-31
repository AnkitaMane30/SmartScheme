from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from utils.helpers import (
    find_main_content,
    is_noise_text,
    dedupe_preserve_order,
    extract_kv_from_soup,
    normalize_text_field,
    parse_date_str,
    parse_date_range,
    parse_currency,
    parse_age_range
)


def scrape_dynamic(url):
    options = Options()
    options.headless = True
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(4)

    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
    except Exception:
        pass

    page_source = driver.page_source

    title = None
    try:
        headings = driver.find_elements(By.TAG_NAME, "h1")
        for heading in headings:
            text = heading.text.strip()
            if text:
                title = text
                break
    except Exception:
        title = None

    if not title:
        try:
            title = driver.title.strip()
        except Exception:
            title = None

    driver.quit()

    soup = BeautifulSoup(page_source, "html.parser")
    content_div = find_main_content(soup, title) or soup

    def extract_nested_text(tag):
        return tag.get_text(" ", strip=True) if tag else ""

    details = None
    eligibility = None
    benefits = None
    documents_required = None
    application_process = None
    exclusion = None

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
            "submit application"
        )):
            current_section = "application_process"
            continue
        elif any(k in lower for k in (
            "eligibility",
            "who can apply",
            "beneficiary",
            "applicant",
            "qualification"
        )):
            current_section = "eligibility"
            continue
        elif any(k in lower for k in (
            "benefit",
            "subsidy",
            "incentive",
            "support",
            "assistance",
            "financial provision"
        )):
            current_section = "benefits"
            continue
        elif any(k in lower for k in (
            "document",
            "documents required",
            "important documents",
            "necessary documents",
            "mandatory documents",
            "proof"
        )):
            current_section = "documents_required"
            continue
        elif any(k in lower for k in (
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
        elif any(k in lower for k in (
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

    if not details:
        paras = content_div.find_all("p")
        collected = []
        for p in paras[:5]:
            txt = extract_nested_text(p)
            if txt and not is_noise_text(txt) and len(txt.split()) >= 4:
                collected.append(txt)
        details = "\n".join(collected) if collected else None

    kv = extract_kv_from_soup(soup)
    if kv:
        for k, v in kv.items():
            lower_k = k.lower()
            if any(x in lower_k for x in ("how to apply", "application process", "procedure to apply", "apply online", "application form")):
                application_process = application_process or normalize_text_field(v, preserve_paragraphs=True)
            if any(x in lower_k for x in ("eligib", "who can")):
                eligibility = eligibility or normalize_text_field(v, preserve_paragraphs=True)
            if any(x in lower_k for x in ("benefit", "subsidy", "amount", "support")):
                benefits = benefits or normalize_text_field(v, preserve_paragraphs=True)
            if any(x in lower_k for x in ("document", "documents required", "necessary documents")):
                documents_required = documents_required or normalize_text_field(v, preserve_paragraphs=True)

    details = dedupe_preserve_order(details) if details else details
    eligibility = dedupe_preserve_order(eligibility) if eligibility else eligibility
    benefits = dedupe_preserve_order(benefits) if benefits else benefits
    documents_required = dedupe_preserve_order(documents_required) if documents_required else documents_required
    application_process = dedupe_preserve_order(application_process) if application_process else application_process
    exclusion = dedupe_preserve_order(exclusion) if exclusion else exclusion

    scheme = {
        "title": title,
        "details": details,
        "eligibility": eligibility,
        "benefits": benefits,
        "documents_required": documents_required,
        "application_process": application_process,
        "exclusion": exclusion,
        "application_link": url
    }

    return scheme
