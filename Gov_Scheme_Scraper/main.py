# for testing db connection
# from database.db_connection import get_connection

# try:
#     conn = get_connection()
#     print("Database connected successfully!")
#     conn.close()
# except Exception as e:
#     print("Error:", e)


## for testing the insertion in the database
# from database.db_operations import save_scheme

# sample_scheme = {
#     "title": Test Scheme",
#     "details": "Sample details",
#     "eligibility": "Anyone",
#     "benefits": "Money",
#     "exclusion": "None",
#     "documents_required": "ID",
#     "application_process": "Online",
#     "category": "General",
#     "state": "India",
#     "department": "Gov Dept",
#     "status": "Active",
#     "start_date": "2025-01-01",
#     "end_date": "2026-01-01",
#     "launch_date": None,
#     "min_income": 0,
#     "max_income": 100000,
#     "gender": "All",
#     "min_age": 18,
#     "max_age": 60,
#     "target_group": "Citizens",
#     "last_date_to_apply": "2025-12-31",
#     "application_link": "http://example.com/scheme1"
# }

# save_scheme(sample_scheme)"

# from scheduler.scheduler import start_scheduler

# if __name__ == "__main__":
#     start_scheduler()


from pipeline.pipeline import run_pipeline
from database.db_operations import get_all_schemes
from config import AGRICULTURE_URLS, BUSINESS_URLS, EDUCATION_URLS, WOMEN_CHILD_URLS

def print_schemes():
    schemes = get_all_schemes()
    print(f"\n{'='*50}")
    print(f"Total schemes in database: {len(schemes)}")
    print(f"{'='*50}\n")

    for idx, s in enumerate(schemes, 1):
        print(f"[Scheme #{idx}]")
        print("----------------------------")
       
        for key, value in s.items():
           
            if isinstance(value, str) and len(value) > 200:
                value = value[:200] + "..."
            print(f"{key}: {value}")
        print("----------------------------\n")

if __name__ == "__main__":
    print_schemes()

  

