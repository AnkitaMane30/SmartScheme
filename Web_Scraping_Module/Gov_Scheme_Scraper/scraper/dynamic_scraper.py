from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
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
    parse_age_range,
)


def scrape_dynamic(url: str) -> dict:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)
        driver.get(url)

        # Wait for page to load meaningful content
        try:
            WebDriverWait(driver, 12).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
        except TimeoutException:
            pass

        # Scroll to load lazy content
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.8)
        except Exception:
            pass

        page_source = driver.page_source

        # Extract title
        title = None
        try:
            headings = driver.find_elements(By.TAG_NAME, "h1")
            for h in headings:
                t = h.text.strip()
                if t and len(t) > 5:
                    title = t
                    break
        except Exception:
            pass

        if not title:
            try:
                title = driver.title.strip().split("|")[0].split("-")[0].strip()
            except Exception:
                title = None

    except WebDriverException as e:
        print(f"[dynamic_scraper] Selenium error for {url}: {e}")
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    if not page_source:
        return None

    soup = BeautifulSoup(page_source, "html.parser")
    content_div = find_main_content(soup, title) or soup

    # Remove noise
    for bad_sel in [
        ".breadcrumb", "nav", ".nav", "header", "footer",
        ".share", ".social-share", ".sidebar", ".widget",
        ".related", ".comments", ".skip-link"
    ]:
        for el in content_div.select(bad_sel):
            try:
                el.decompose()
            except Exception:
                pass

    # -------------------------
    # SECTION EXTRACTION (same logic as html_scraper)
    # -------------------------
    details = None
    eligibility = None
    benefits = None
    documents_required = None
    application_process = None
    exclusion = None

    SECTION_KEYWORDS = {
        "application_process": [
            "how to apply", "application process", "procedure to apply",
            "apply online", "online application", "application form",
            "steps to apply", "method of application"
        ],
        "eligibility": [
            "eligibility", "who can apply", "eligible", "beneficiary",
            "who is eligible", "eligibility criteria"
        ],
        "benefits": [
            "benefit", "benefits", "financial assistance", "subsidy",
            "incentive", "support provided", "scheme benefits"
        ],
        "documents_required": [
            "document", "documents required", "important documents",
            "necessary documents", "mandatory documents", "required documents"
        ],
        "exclusion": [
            "exclusion", "not eligible", "ineligible", "who cannot apply"
        ],
        "details": [
            "overview", "objective", "purpose", "about the scheme",
            "introduction", "scheme details", "description", "about"
        ]
    }

    current_section = "details"
    elements = content_div.find_all([
        "h1", "h2", "h3", "h4", "p", "li", "strong", "td", "div", "span"
    ])

    for el in elements:
        text = el.get_text(" ", strip=True)
        if not text or len(text) < 4:
            continue

        lower = text.lower().strip()

        # Detect section heading
        matched_section = None
        for section, keywords in SECTION_KEYWORDS.items():
            if any(k in lower for k in keywords):
                if len(text.split()) <= 10:  # likely a heading
                    matched_section = section
                    break

        if matched_section:
            current_section = matched_section
            continue

        if is_noise_text(text):
            continue

        if len(text.split()) <= 2 and current_section != "documents_required":
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

    # Clean
    details = dedupe_preserve_order(details)
    eligibility = dedupe_preserve_order(eligibility)
    benefits = dedupe_preserve_order(benefits)
    documents_required = dedupe_preserve_order(documents_required)
    application_process = dedupe_preserve_order(application_process)
    exclusion = dedupe_preserve_order(exclusion)

    # Fallback for details
    if not details:
        paras = []
        for p in content_div.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if txt and not is_noise_text(txt) and len(txt.split()) >= 6:
                paras.append(txt)
            if len(paras) >= 5:
                break
        details = "\n".join(paras) if paras else None

    # Key-Value extraction
    kv = extract_kv_from_soup(soup)

    if kv:
        for k, v in kv.items():
            lower_k = k.lower()
            if any(x in lower_k for x in ("how to apply", "application process", "procedure")):
                application_process = application_process or normalize_text_field(v, preserve_paragraphs=True)
            if "eligib" in lower_k or "who can" in lower_k:
                eligibility = eligibility or normalize_text_field(v, preserve_paragraphs=True)
            if any(x in lower_k for x in ("benefit", "subsidy", "assistance")):
                benefits = benefits or normalize_text_field(v, preserve_paragraphs=True)
            if any(x in lower_k for x in ("document", "documents required")):
                documents_required = documents_required or normalize_text_field(v, preserve_paragraphs=True)

    # Build scheme
    scheme = {
        "title": normalize_text_field(title),
        "details": details,
        "eligibility": eligibility,
        "benefits": benefits,
        "documents_required": documents_required,
        "application_process": application_process,
        "exclusion": exclusion,
        "application_link": url,

        # Defaults (will be overridden by domain scrapers if needed)
        "category": "Government Scheme",
        "state": "Maharashtra",
        "department": None,
        "status": "Unknown",
        "gender": "All",
        "target_group": "Citizens",
        "min_age": None,
        "max_age": None,
        "min_income": None,
        "max_income": None,
        "start_date": None,
        "end_date": None,
        "launch_date": None,
        "last_date_to_apply": None,
    }

    # Try to extract age/income from all text
    all_text = " ".join(filter(None, [details, eligibility, benefits]))
    min_age, max_age = parse_age_range(all_text)
    scheme["min_age"] = min_age
    scheme["max_age"] = max_age
    scheme["min_income"] = parse_currency(all_text)

    return scheme