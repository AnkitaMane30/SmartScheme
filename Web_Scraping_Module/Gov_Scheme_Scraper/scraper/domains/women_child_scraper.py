from scraper.html_scraper import scrape_html
from scraper.dynamic_scraper import scrape_dynamic
from utils.helpers import normalize_text_field, is_noise_text
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import re


def scrape_women_child(url: str, base_scheme: dict = None) -> dict:
    if "csr.wcdcommpune.com" in url:
        scheme = scrape_wcd_properly(url)
    elif "myscheme.gov.in" in url:
        scheme = scrape_dynamic(url)
        scheme = clean_myscheme_women(scheme)
    else:
        scheme = base_scheme or scrape_html(url)

    if not scheme:
        return None

    # ---------- Domain defaults ----------
    scheme["category"] = "Women & Child Development"
    scheme["department"] = "Women and Child Development Department"
    scheme["state"] = "Maharashtra"
    scheme["target_group"] = "Women, Adolescent Girls, Children"
    scheme["min_age"] = None
    scheme["max_age"] = None

    title = (scheme.get("title") or "").lower()

    if any(x in title for x in ["adolescent", "sag", "sabla"]):
        scheme["target_group"] = "Adolescent Girls (14-18 years)"
    elif any(x in title for x in ["creche", "palna", "nursery"]):
        scheme["target_group"] = "Children of Working Mothers"
    elif any(x in title for x in ["one stop", "shakti sadan", "manodhairya", "shelter"]):
        scheme["target_group"] = "Women in Distress / Victims of Violence"
    elif any(x in title for x in ["poshan", "nutrition", "ahar"]):
        scheme["target_group"] = "Women and Children (Nutrition)"
    elif any(x in title for x in ["beti bachao", "kanya", "bhagyashree"]):
        scheme["target_group"] = "Girl Child"
    elif "working women" in title or "hostel" in title:
        scheme["target_group"] = "Working Women"
    elif "anganwadi" in title:
        scheme["target_group"] = "Children, Adolescent Girls and Women (Anganwadi)"
    elif "probation" in title or "offender" in title:
        scheme["target_group"] = "Offenders under Probation"

    # Final clean
    for field in ["details", "eligibility", "benefits", "documents_required", "application_process", "exclusion"]:
        if scheme.get(field):
            scheme[field] = normalize_text_field(scheme[field], preserve_paragraphs=True)

    return scheme


def scrape_wcd_properly(url: str) -> dict:
    """Dedicated strong extractor for csr.wcdcommpune.com"""

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
        title = driver.title.split("|")[0].strip() if driver.title else None
    except Exception as e:
        print(f"[wcd] Error: {e}")
        return None
    finally:
        if driver:
            driver.quit()

    soup = BeautifulSoup(page_source, "html.parser")

    # Remove noise elements
    for sel in ["nav", "header", "footer", "script", "style", ".modal", ".popup", "#accessibility"]:
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
        "beneficiaries": "eligibility",
        "short description": "details",
        "key points": "benefits",
        "scheme details": "details",
        "details": "details",
        "introduction": "details",
        "objective": "details",
        "criteria / procedure to apply": "application_process",
        "criteria": "eligibility",
        "procedure to apply": "application_process",
        "information / criteria / procedure to apply": "application_process",
        "conditions for": "eligibility",
        "regulations for": "eligibility",
        "facilities provided": "benefits",
    }

    elements = soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "div"])

    for el in elements:
        text = el.get_text(" ", strip=True)
        if not text or len(text) < 8:
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

        # Strong noise filter
        if is_noise_text(text):
            continue
        if any(x in lower for x in [
            "your browser does not support",
            "exiting our website",
            "you are about to proceed",
            "click yes to proceed",
            "schemes home",
            "women child",
            ".pdf",
            "back to top",
            "loading..."
        ]):
            continue
        if len(text.split()) <= 3:
            continue

        sections[current].append(text)

    def join_and_dedupe(lst):
        if not lst:
            return None

        # Remove near-duplicates
        cleaned = []
        seen = set()
        for item in lst:
            normalized = re.sub(r"\s+", " ", item.lower()).strip()
            if len(normalized) < 25:
                continue

            is_dup = False
            for existing in seen:
                if normalized in existing or existing in normalized:
                    is_dup = True
                    break
                w1 = set(normalized.split())
                w2 = set(existing.split())
                if len(w1) > 8 and len(w2) > 8:
                    if len(w1 & w2) / max(len(w1), len(w2)) > 0.7:
                        is_dup = True
                        break

            if not is_dup:
                seen.add(normalized)
                cleaned.append(item)

        return "\n".join(cleaned) if cleaned else None

    return {
        "title": title,
        "details": join_and_dedupe(sections["details"]),
        "benefits": join_and_dedupe(sections["benefits"]),
        "eligibility": join_and_dedupe(sections["eligibility"]),
        "application_process": join_and_dedupe(sections["application_process"]),
        "documents_required": join_and_dedupe(sections["documents_required"]),
        "exclusion": join_and_dedupe(sections["exclusion"]),
        "application_link": url,
        "state": "Maharashtra",
        "status": "Unknown",
        "gender": "All",
    }


def clean_myscheme_women(scheme: dict) -> dict:
    if not scheme:
        return scheme

    def cut_faq(text):
        if not text:
            return text
        parts = re.split(
            r"frequently asked questions|what is the|who is eligible|how can i apply|was this helpful",
            text,
            flags=re.IGNORECASE
        )
        return parts[0].strip() if parts else text

    for field in ["details", "eligibility", "benefits", "documents_required", "application_process", "exclusion"]:
        scheme[field] = cut_faq(scheme.get(field) or "")

    NOISE = [
        r"you're being redirected.*?(ok|cancel)",
        r"your mobile number will be shared.*?(ok|cancel)",
        r"something went wrong.*?ok",
        r"you have already submitted.*?ok",
        r"you need to sign in.*?sign in",
        r"it seems you have already initiated.*?",
        r"was this helpful\??",
        r"news and updates",
        r"no new news and updates available",
        r"check eligibility",
        r"sign in",
        r"cancel",
        r"apply now",
    ]

    for field in ["details", "eligibility", "benefits", "documents_required", "application_process", "exclusion"]:
        text = scheme.get(field) or ""
        for pat in NOISE:
            text = re.sub(pat, " ", text, flags=re.IGNORECASE | re.DOTALL)
        scheme[field] = normalize_text_field(text, preserve_paragraphs=True) if text.strip() else None

    return scheme