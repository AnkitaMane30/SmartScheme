import schedule
import time
from pipeline.pipeline import run_pipeline

def start_scheduler():
    print("Scheduler started...")

    # Run every day
    #schedule.every().day.at("02:00").do(run_pipeline)

    # OR (for testing: run every 1 minute)
    schedule.every(1).minutes.do(run_pipeline)

    while True:
        schedule.run_pending()
        time.sleep(60)