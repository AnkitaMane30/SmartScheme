import requests
from bs4 import BeautifulSoup
import re
from scraper.html_scraper import scrape_html

def scrape_water(url, base_scheme=None):
    # Use provided base scheme if available
    scheme = base_scheme or scrape_html(url)

    # Override defaults for water schemes
    scheme["category"] = "Water/Utility Scheme"
    scheme["department"] = "Water Resources Department"
    scheme["state"] = "Maharashtra"
    scheme["target_group"] = "Citizens"

    # Fallback: if details is None, grab first few <p> tags
    if not scheme["details"]:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        paras = soup.find_all("p")
        if paras:
            scheme["details"] = "\n".join([p.get_text(strip=True) for p in paras[:3]])

    return scheme
