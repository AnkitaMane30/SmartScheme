from scraper.scraper_manager import scrape_source
from database.db_operations import save_scheme
from config import URLS
import time

def run_pipeline(sources=None):
    sources = sources or URLS
    print("Starting scraping pipeline...\n")

    for source in sources:
        try:
            print("Processing:", source["url"])

            # Step 1: Scrape
            scheme = scrape_source(source)

            if not scheme:
                print("No data found\n")
                continue

            # Step 2: Fill missing fields (important)
            scheme.setdefault("eligibility", None)
            scheme.setdefault("benefits", None)
            scheme.setdefault("details", None)
            scheme.setdefault("application_link", source["url"])

            # Step 3: Save (Insert / Update / Skip)
            save_scheme(scheme)

            print("Done\n")

            # Step 4: Delay (avoid blocking)
            time.sleep(2)

        except Exception as e:
            print("Error:", e, "\n")

    print("Pipeline completed.")