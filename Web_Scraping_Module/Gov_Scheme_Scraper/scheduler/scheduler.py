import schedule
import time
from datetime import datetime
from pipeline.pipeline import run_pipeline


def job():
    """Wrapper so that errors do not stop the scheduler"""
    print("\n" + "=" * 60)
    print(f"Scheduled scraping started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    try:
        run_pipeline()
        print(f"Scheduled scraping completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"Error during scheduled scraping: {e}")


def start_scheduler():
    print("Scheduler started...")
    print("Press Ctrl+C to stop.\n")

    # ---------- Choose one of the following ----------

    # 1. For testing (runs every 2 minutes)
    # schedule.every(2).minutes.do(job)

    # 2. Recommended for production (runs once every day at 2:00 AM)
    schedule.every().day.at("02:00").do(job)

    # 3. Optional: also run once immediately when scheduler starts
    # job()

    while True:
        schedule.run_pending()
        time.sleep(30)