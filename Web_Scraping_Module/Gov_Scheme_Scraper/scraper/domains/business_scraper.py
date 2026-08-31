from scraper.html_scraper import scrape_html
from scraper.dynamic_scraper import scrape_dynamic
from utils.helpers import normalize_text_field, is_noise_text
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re


def scrape_business(url: str, base_scheme: dict = None) -> dict:
    if "lidcom.in" in url:
        scheme = scrape_lidcom_properly(url)
    else:
        scheme = base_scheme
        if not scheme:
            if "standupmitra" in url:
                scheme = scrape_dynamic(url)
            else:
                scheme = scrape_html(url)

    if not scheme:
        return None

    # Domain defaults
    scheme["category"] = "Business / MSME / Entrepreneurship"
    scheme["department"] = "Industries / MSME / LIDCOM"
    scheme["state"] = "Maharashtra"
    scheme["target_group"] = "Entrepreneurs, MSMEs, Charmakar Community"

    title = (scheme.get("title") or "").lower()
    if "margin money" in title:
        scheme["category"] = "Margin Money Scheme"
    elif "subsidy" in title or "50%" in title:
        scheme["category"] = "Subsidy Scheme"
    elif "gattai" in title or "stall" in title:
        scheme["category"] = "Gattai Stall Scheme"
        scheme["target_group"] = "Roadside Cobblers / Charmakar Community"
    elif "pmegp" in title:
        scheme["category"] = "PMEGP"
        scheme["target_group"] = "Micro Enterprises / Unemployed Youth"

    # Final clean
    for field in ["details", "eligibility", "benefits", "documents_required", "application_process", "exclusion"]:
        if scheme.get(field):
            scheme[field] = normalize_text_field(scheme[field], preserve_paragraphs=True)

    return scheme


def scrape_lidcom_properly(url: str) -> dict:
    """Dedicated strong extractor for lidcom.in pages"""

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(25)
        driver.get(url)
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)

        page_source = driver.page_source
        title = None
        try:
            h1 = driver.find_element(By.TAG_NAME, "h1")
            title = h1.text.strip()
        except:
            title = driver.title.split("|")[0].strip() if driver.title else None

    except Exception as e:
        print(f"[lidcom] Error: {e}")
        return None
    finally:
        if driver:
            driver.quit()

    soup = BeautifulSoup(page_source, "html.parser")

    # Remove noise
    for sel in ["nav", "header", "footer", "script", "style", ".sidebar", ".widget"]:
        for tag in soup.select(sel):
            tag.decompose()

    sections = {
        "details": [],
        "benefits": [],
        "eligibility": [],
        "application_process": [],
        "documents_required": [],
        "exclusion": []
    }

    current = "details"

    heading_map = {
        "scheme objective": "details",
        "objective": "details",
        "benefits provided": "benefits",
        "benefits": "benefits",
        "eligibility criteria": "eligibility",
        "eligibility": "eligibility",
        "application process": "application_process",
        "how to apply": "application_process",
        "documents required": "documents_required",
        "required documents": "documents_required",
    }

    elements = soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "div", "span"])

    for el in elements:
        text = el.get_text(" ", strip=True)
        if not text or len(text) < 4:
            continue

        lower = text.lower().strip()

        # Detect heading
        matched = None
        for key, value in heading_map.items():
            if lower == key or lower.startswith(key):
                matched = value
                break

        if matched:
            current = matched
            continue

        if is_noise_text(text):
            continue
        if len(text.split()) <= 2:
            continue

        sections[current].append(text)

    def join_clean(lst):
        if not lst:
            return None
        seen = set()
        result = []
        for item in lst:
            if item not in seen and len(item) > 10:
                seen.add(item)
                result.append(item)
        return "\n".join(result) if result else None

    scheme = {
        "title": title,
        "details": join_clean(sections["details"]),
        "benefits": join_clean(sections["benefits"]),
        "eligibility": join_clean(sections["eligibility"]),
        "application_process": join_clean(sections["application_process"]),
        "documents_required": join_clean(sections["documents_required"]),
        "exclusion": join_clean(sections["exclusion"]),
        "application_link": url,
        "state": "Maharashtra",
        "status": "Unknown",
        "gender": "All",
        "min_age": None,
        "max_age": None,
    }

    return scheme