"""
Improved Training Data Generator (Smarter Labels)
"""

import os
import sys
import random
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils.db_connection as db
from services.eligibility_engine import EligibilityEngine
from services.condition_extractor import ConditionExtractor
from services.recommendation_engine import RecommendationEngine

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "training_data.csv")
random.seed(42)


def generate_synthetic_users(n_users=100):
    ages = [18, 19, 20, 21, 22, 23, 25, 28, 30, 35, 40, 45, 50, 55, 60]
    genders = ["Male", "Female"]
    states = ["Maharashtra"]
    districts = ["Kolhapur", "Pune", "Mumbai", "Nagpur", "Nashik", "Aurangabad", "Satara"]
    castes = ["General", "SC", "ST", "OBC", "VJNT", "SBC"]
    occupations = ["Student", "Farmer", "Construction Worker", "Unemployed", "Homemaker", "Self Employed"]
    incomes = [50000, 100000, 150000, 200000, 250000, 300000, 400000, 500000, 800000]
    education_levels = ["10th", "12th", "Diploma", "B.Tech", "B.A", "B.Com", "M.Tech", "MBA", None]
    disability_options = [True, False]
    bpl_options = [True, False]
    land_owner_options = [True, False]
    marital_status_options = ["Single", "Married", "Widow", "Unmarried"]

    users = []
    for i in range(n_users):
        occupation = random.choice(occupations)
        user = {
            "user_id": i + 1,
            "age": random.choice(ages),
            "gender": random.choice(genders),
            "state": random.choice(states),
            "district": random.choice(districts),
            "caste_category": random.choice(castes),
            "occupation": occupation,
            "annual_income": random.choice(incomes),
            "disability_status": random.choice(disability_options),
            "is_bpl": random.choice(bpl_options),
            "land_owner": random.choice(land_owner_options) if occupation == "Farmer" else False,
            "marital_status": random.choice(marital_status_options),
            "education_level": random.choice(education_levels) if occupation == "Student" else None,
            "course": "B.Tech" if occupation == "Student" and random.random() > 0.4 else None,
            "rural_urban": random.choice(["Rural", "Urban"]),
        }
        users.append(user)
    return users


def get_category_match_score(user, scheme):
    """
    Returns a score (0 to 1) based on how well scheme category matches user.
    """
    occupation = (user.get("occupation") or "").lower()
    gender = (user.get("gender") or "").lower()
    category = (scheme.get("category") or "").lower()
    title = (scheme.get("title") or "").lower()

    score = 0.0

    # Student
    if "student" in occupation:
        if any(x in category or x in title for x in ["scholarship", "education"]):
            score += 0.7
        if "sports" in category and "scholarship" in category:
            score += 0.15   # sports scholarship is partially ok
        if any(x in category for x in ["women & child", "anganwadi", "shelter", "rape", "victim"]):
            score -= 0.4

    # Farmer
    if "farmer" in occupation:
        if any(x in category or x in title for x in ["agriculture", "farmer", "rural", "irrigation", "crop"]):
            score += 0.7

    # Construction Worker
    if "construction" in occupation:
        if any(x in category or x in title for x in ["labour", "worker", "construction", "employment"]):
            score += 0.6

    # Homemaker / Female
    if "homemaker" in occupation or gender == "female":
        if any(x in category for x in ["women", "women & child"]):
            score += 0.4

    # Penalize completely unrelated
    if "student" in occupation and "sports infrastructure" in category:
        score -= 0.5

    return max(0.0, min(1.0, score))


def load_schemes():
    sql = """
        SELECT scheme_id, title, details, eligibility, exclusion, benefits,
               category, state, department, gender, min_age, max_age,
               min_income, max_income, target_group, application_link
        FROM schemes
    """
    return db.executeQuery(sql, ())


def main():
    print("=" * 60)
    print("GENERATING IMPROVED TRAINING DATA")
    print("=" * 60)

    schemes = load_schemes()
    print(f"Loaded {len(schemes)} schemes")

    users = generate_synthetic_users(n_users=100)
    print(f"Generated {len(users)} synthetic users")

    eligibility_engine = EligibilityEngine()
    condition_extractor = ConditionExtractor()
    recommendation_engine = RecommendationEngine()

    rows = []
    total = len(users) * len(schemes)
    print(f"Total combinations: {total}")
    print("Processing...\n")

    processed = 0

    for user in users:
        all_recs = recommendation_engine.recommend(user, top_n=len(schemes))
        tfidf_map = {r["scheme_id"]: r["ml_score"] for r in all_recs}

        for scheme in schemes:
            processed += 1
            if processed % 800 == 0:
                print(f"  Processed {processed}/{total}...")

            extracted = condition_extractor.extract_from_scheme(scheme)
            result = eligibility_engine.check_scheme_eligibility(user, scheme, extracted)

            is_eligible = 1 if result["status"] == "ELIGIBLE" else 0
            category_score = get_category_match_score(user, scheme)
            tfidf_score = tfidf_map.get(scheme["scheme_id"], 0.0)

            # ---------- Smarter Label Logic ----------
            # Base on eligibility + category match
            if is_eligible == 1 and category_score >= 0.4:
                label = 1
            elif is_eligible == 1 and category_score >= 0.15 and tfidf_score > 2:
                label = 1
            elif is_eligible == 0:
                label = 0
            else:
                # Borderline cases - mostly negative to reduce noise
                label = 1 if (category_score > 0.5 and random.random() > 0.6) else 0

            row = {
                "user_age": user["age"],
                "user_gender": user["gender"],
                "user_caste": user["caste_category"],
                "user_occupation": user["occupation"],
                "user_income": user["annual_income"],
                "user_disability": int(user["disability_status"]),
                "user_is_bpl": int(user["is_bpl"]),
                "user_land_owner": int(user["land_owner"]),
                "user_marital_status": user["marital_status"],
                "user_state": user["state"],
                "user_education": user.get("education_level") or "None",

                "scheme_id": scheme["scheme_id"],
                "scheme_min_age": scheme.get("min_age") if scheme.get("min_age") is not None else -1,
                "scheme_max_age": scheme.get("max_age") if scheme.get("max_age") is not None else 999,
                "scheme_max_income": scheme.get("max_income") if scheme.get("max_income") is not None else 99999999,
                "scheme_gender": scheme.get("gender") or "All",
                "scheme_category": scheme.get("category") or "Unknown",
                "scheme_state": scheme.get("state") or "All",

                "tfidf_score": tfidf_score,
                "category_match": round(category_score, 3),
                "relevant": label
            }
            rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_FILE, index=False)

    print("\n" + "=" * 60)
    print("IMPROVED TRAINING DATA GENERATED")
    print("=" * 60)
    print(f"Total rows     : {len(df)}")
    print(f"Positive (1)   : {df['relevant'].sum()}")
    print(f"Negative (0)   : {len(df) - df['relevant'].sum()}")
    print(f"Saved to       : {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()