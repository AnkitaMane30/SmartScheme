from scraper.domains.bank_scraper import scrape_bank
from scraper.domains.social_scraper import scrape_social
from scraper.domains.sports_scraper import scrape_sport
from scraper.domains.business_scraper import scrape_business
from scraper.domains.agriculter_scraper import scrape_agriculture
from scraper.domains.education_scraper import scrape_education
from scraper.html_scraper import scrape_html
from scraper.dynamic_scraper import scrape_dynamic
from scraper.pdf_scraper import scrape_pdf
from scraper.domains.water_scraper import scrape_water
from scraper.domains.women_child_scraper import scrape_women_child
from scraper.domains.housing_scraper import scrape_housing


def scrape_source(source):
    url = source["url"]
    type_ = source["type"]
    domain = source.get("domain")  # NEW field

    
    if type_ == "dynamic":
        scheme = scrape_dynamic(url)
    elif type_ == "pdf":
        scheme = scrape_pdf(url)
    else:
        scheme = scrape_html(url)

    # Then apply domain-specific overrides if available, passing base scheme
    if domain == "water":
        scheme = scrape_water(url, base_scheme=scheme)
    elif domain == "bank":
        scheme = scrape_bank(url, base_scheme=scheme)
    elif domain == "social":
        scheme = scrape_social(url, base_scheme=scheme)
    elif domain == "sport":
        scheme = scrape_sport(url, base_scheme=scheme)
    elif domain == "business":
        scheme = scrape_business(url, base_scheme=scheme)
    elif domain == "agriculture":
        scheme = scrape_agriculture(url, base_scheme=scheme)
    elif domain == "education":
        scheme = scrape_education(url, base_scheme=scheme)
    elif domain == "women_child":
        scheme = scrape_women_child(url, base_scheme=scheme)
    elif domain == "housing":
        scheme = scrape_housing(url, base_scheme=scheme)

    return scheme
