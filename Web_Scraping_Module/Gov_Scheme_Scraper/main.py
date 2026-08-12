from pipeline.pipeline import run_pipeline
from database.db_operations import get_all_schemes
from config import (
    WATER_URLS, BANK_URLS, SOCIAL_URLS, SPORT_URLS,
    BUSINESS_URLS, EDUCATION_URLS, AGRICULTURE_URLS, WOMEN_CHILD_URLS, HOUSING_URLS
)


def print_schemes(limit=10):
    schemes = get_all_schemes()
    print(f"\nTotal schemes in database: {len(schemes)}\n")
    print("=" * 80)

    for idx, s in enumerate(schemes[:limit], 1):
        print(f"\n[{idx}] Scheme ID: {s.get('scheme_id')}")
        print("-" * 80)
        print(f"Title               : {s.get('title')}")
        print();
        print(f"Category            : {s.get('category')}")
        print();
        print(f"Department          : {s.get('department')}")
        print();
        print(f"State               : {s.get('state')}")
        print();
        print(f"Status              : {s.get('status')}")
        print();
        print(f"Target Group        : {s.get('target_group')}")
        print();
        print(f"Gender              : {s.get('gender')}")
        print()
        print(f"Min Age             : {s.get('min_age')}")
        print(f"Max Age             : {s.get('max_age')}")
        print(f"Min Income          : {s.get('min_income')}")
        print(f"Max Income          : {s.get('max_income')}")
        print()
        print(f"Start Date          : {s.get('start_date')}")
        print(f"End Date            : {s.get('end_date')}")
        print(f"Launch Date         : {s.get('launch_date')}")
        print(f"Last Date to Apply  : {s.get('last_date_to_apply')}")
        print()
        print(f"Eligibility         :\n{s.get('eligibility')}")
        print()
        print(f"Benefits            :\n{s.get('benefits')}")
        print()
        print(f"Documents Required  :\n{s.get('documents_required')}")
        print()
        print(f"Application Process :\n{s.get('application_process')}")
        print()
        print(f"Exclusion           :\n{s.get('exclusion')}")
        print()
        print(f"Details             :\n{s.get('details')}")
        print()
        print(f"Application Link    : {s.get('application_link')}")
        print(f"Last Updated        : {s.get('last_updated')}")
        print("=" * 80)


if __name__ == "__main__":
    # -------- Choose what to run --------
    # 1. Run everything
    run_pipeline()

    # 2. Run only one domain (recommended while testing)
    #run_pipeline(WATER_URLS)          
    #run_pipeline(SOCIAL_URLS)
    #run_pipeline(EDUCATION_URLS)
    #run_pipeline(BANK_URLS)
    #run_pipeline(SPORT_URLS)
    #run_pipeline(BUSINESS_URLS)
    #run_pipeline(AGRICULTURE_URLS)
    #run_pipeline(WOMEN_CHILD_URLS)
    #run_pipeline(HOUSING_URLS)
    

    # 3. Just view current data
    #print_schemes(limit=30)
    #print_schemes()