from services.smart_recommendation import SmartRecommendation


# =========================================================
# CREATE ENGINE
# =========================================================

engine = SmartRecommendation()


# =========================================================
# TEST USER PROFILE
# =========================================================

user_profile = {
    "age": 34,
    "gender": "Female",
    "state": "Maharashtra",
    "district": "Mumbai",
    "annual_income": 180000,
    "caste_category": "General",
    "occupation": "Homemaker",
    "education_level": "12th",
    "disability_status": False,
    "is_bpl": False,
    "land_owner": False,
    "marital_status": "Married",
    "home_based_business": True
}


# =========================================================
# GENERATE RECOMMENDATIONS
# =========================================================

result = engine.recommend(
    user_profile,
    top_n=8
)


# =========================================================
# PRINT SUMMARY
# =========================================================

print("\n========================================")
print("SMARTSCHEME RECOMMENDATION RESULT")
print("========================================")

print(
    "Total schemes:",
    result["total_schemes"]
)

print(
    "Eligible schemes:",
    result["eligible_count"]
)

print(
    "Needs verification:",
    result["needs_verification_count"]
)

print(
    "Not eligible:",
    result["not_eligible_count"]
)


# =========================================================
# PRINT RECOMMENDATIONS
# =========================================================

print("\n========================================")
print("TOP RECOMMENDATIONS")
print("========================================")


recommendations = result["recommendations"]


if not recommendations:

    print("No recommendations found.")

else:

    for index, recommendation in enumerate(recommendations, start=1):

        print(f"\n{index}. {recommendation['scheme_name']}")
        print("   Scheme ID   :", recommendation["scheme_id"])
        print("   Category    :", recommendation["category"])
        print("   Department  :", recommendation["department"])
        print("   TF-IDF Score   :", recommendation.get("tfidf_score"))
        print("   ML Score       :", recommendation.get("ml_score"))
        print("   Category Boost :", recommendation.get("category_boost"))
        print("   Final Score    :", recommendation.get("final_score"))
        print("   URL         :", recommendation["url"])