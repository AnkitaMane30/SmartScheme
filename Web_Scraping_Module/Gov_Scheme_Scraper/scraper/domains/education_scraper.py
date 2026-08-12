from scraper.dynamic_scraper import scrape_dynamic
from scraper.html_scraper import scrape_html
from utils.helpers import normalize_text_field, is_noise_text
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re


def scrape_education(url: str, base_scheme: dict = None) -> dict:
    if "myscheme.gov.in" in url:
        scheme = scrape_myscheme_properly(url)
    else:
        scheme = base_scheme or scrape_html(url)

    if not scheme:
        return None

    # Domain defaults
    scheme["category"] = "Education & Scholarship"
    scheme["department"] = "School Education / Higher & Technical Education / Social Justice"
    scheme["state"] = "Maharashtra"
    scheme["target_group"] = "Students"
    scheme["min_age"] = None
    scheme["max_age"] = None
    scheme["gender"] = "All"

    title = (scheme.get("title") or "").lower()
    if "scholarship" in title:
        scheme["category"] = "Scholarship"
    if any(x in title for x in ["girl", "kanya"]):
        scheme["target_group"] = "Girl Students"
        scheme["gender"] = "Female"
    elif any(x in title for x in ["vjnt", "sbc", "obc", "nomadic"]):
        scheme["target_group"] = "VJNT / SBC / OBC Students"
    elif "sc" in title or "scheduled caste" in title:
        scheme["target_group"] = "Scheduled Caste Students"

    # Final clean
    for field in ["details", "eligibility", "benefits", "documents_required", "application_process", "exclusion"]:
        if scheme.get(field):
            scheme[field] = normalize_text_field(scheme[field], preserve_paragraphs=True)

    return scheme


def scrape_myscheme_properly(url: str) -> dict:
    """Dedicated extractor for myScheme.gov.in with strict section control"""

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)
        driver.get(url)

        WebDriverWait(driver, 12).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        time.sleep(2)

        # Scroll to load content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)

        page_source = driver.page_source
        title = driver.title.split("|")[0].strip() if driver.title else None

        # Try better title
        try:
            h1 = driver.find_element(By.TAG_NAME, "h1")
            if h1.text.strip():
                title = h1.text.strip()
        except:
            pass

    except Exception as e:
        print(f"[myscheme] Selenium error: {e}")
        return None
    finally:
        if driver:
            driver.quit()

    soup = BeautifulSoup(page_source, "html.parser")

    # Remove noise elements
    for sel in ["nav", "header", "footer", ".share", ".modal", ".popup", "script", "style"]:
        for tag in soup.select(sel):
            tag.decompose()

    # ---------- Strict Section Extraction ----------
    sections = {
        "details": [],
        "benefits": [],
        "eligibility": [],
        "exclusion": [],
        "application_process": [],
        "documents_required": []
    }

    current = "details"

    # myScheme uses these exact headings
    heading_map = {
        "details": "details",
        "benefits": "benefits",
        "eligibility": "eligibility",
        "exclusions": "exclusion",
        "exclusion": "exclusion",
        "application process": "application_process",
        "documents required": "documents_required",
        "frequently asked questions": None,   # we ignore FAQ
        "sources and references": None,
    }

    # Get all relevant elements
    elements = soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "div"])

    for el in elements:
        text = el.get_text(" ", strip=True)
        if not text or len(text) < 3:
            continue

        lower = text.lower().strip()

        # Detect heading
        matched = None
        for key, value in heading_map.items():
            if lower == key or lower.startswith(key + " ") or lower == key + ":":
                matched = value
                break

        if matched is not None:
            current = matched
            continue
        if matched is None and any(k in lower for k in ["frequently asked questions", "sources and references", "faq"]):
            current = None
            continue

        if current is None:
            continue

        # Skip noise
        if is_noise_text(text):
            continue
        if len(text.split()) <= 2:
            continue
        if any(x in lower for x in ["was this helpful", "check eligibility", "sign in", "cancel", "ok", "apply now"]):
            continue

        sections[current].append(text)

    # Build final scheme
    def join_clean(lst):
        if not lst:
            return None
        # Remove duplicates while preserving order
        seen = set()
        result = []
        for item in lst:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return "\n".join(result)

    scheme = {
        "title": title,
        "details": join_clean(sections["details"]),
        "benefits": join_clean(sections["benefits"]),
        "eligibility": join_clean(sections["eligibility"]),
        "exclusion": join_clean(sections["exclusion"]),
        "application_process": join_clean(sections["application_process"]),
        "documents_required": join_clean(sections["documents_required"]),
        "application_link": url,
        "state": "Maharashtra",
        "status": "Unknown",
        "gender": "All",
        "min_age": None,
        "max_age": None,
        "min_income": None,
        "max_income": None,
    }

    # If exclusion is just "NA" or empty
    if scheme["exclusion"] and scheme["exclusion"].strip().upper() in ["NA", "N/A", "NIL", "NONE"]:
        scheme["exclusion"] = None

    return scheme