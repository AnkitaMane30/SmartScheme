import time
from scraper.scraper_manager import scrape_source
from database.db_operations import save_scheme
from config import URLS
from utils.helpers import process_scheme


def run_pipeline(sources=None, delay=2.5):
    """
    Main scraping pipeline.
    sources: list of dicts from config (default = all URLS)
    delay: seconds to wait between requests (be polite to government sites)
    """
    sources = sources or URLS
    total = len(sources)
    success = 0
    failed = 0
    skipped = 0

    print("=" * 60)
    print(f"Starting scraping pipeline | Total URLs: {total}")
    print("=" * 60)

    for idx, source in enumerate(sources, 1):
        url = source.get("url")
        domain = source.get("domain", "unknown")
        print(f"\n[{idx}/{total}] Domain: {domain}")
        print(f"URL: {url}")

        try:
            scheme = scrape_source(source)

            if not scheme or not scheme.get("title"):
                print("→ No usable data found. Skipping.")
                failed += 1
                continue

            # Force clean + type-safe data
            scheme = process_scheme(scheme)

            # Ensure mandatory fields
            scheme.setdefault("application_link", url)
            scheme.setdefault("state", "Maharashtra")

            # Save (insert / update / skip based on content_hash)
            result = save_scheme(scheme)

            if result == "inserted":
                success += 1
                print(f"→ Inserted: {scheme.get('title')[:80]}")
            elif result == "updated":
                success += 1
                print(f"→ Updated:  {scheme.get('title')[:80]}")
            else:
                skipped += 1
                print(f"→ No change: {scheme.get('title')[:80]}")

        except Exception as e:
            failed += 1
            print(f"→ ERROR: {e}")

        # Polite delay
        time.sleep(delay)

    print("\n" + "=" * 60)
    print("Pipeline completed")
    print(f"Success : {success}")
    print(f"Skipped : {skipped}")
    print(f"Failed  : {failed}")
    print("=" * 60)