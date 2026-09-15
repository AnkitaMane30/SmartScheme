from services.eligibility_engine import EligibilityEngine
import utils.db_connection as db


engine = EligibilityEngine()


# =========================================
# USER PROFILE
# =========================================

user_profile = {
    "age": 22,
    "gender": "Female",
    "state": "Maharashtra",
    "annual_income": 200000,
    "caste_category": "General"
}


# =========================================
# GET SCHEMES FROM MYSQL
# =========================================

sql = """
    SELECT
        scheme_id,
        title,
        category,
        state,
        gender,
        min_age,
        max_age,
        min_income,
        max_income
    FROM schemes
"""

schemes = db.executeQuery(sql, ())

print("Total schemes:", len(schemes))


# =========================================
# CHECK EVERY SCHEME
# =========================================

for scheme in schemes:

    conditions = engine.build_conditions_from_scheme(scheme)

    result = engine.check_eligibility(
        user_profile,
        conditions
    )

    print("\n--------------------------------")
    print("Scheme ID:", scheme["scheme_id"])
    print("Scheme:", scheme["title"])
    print("Conditions:", conditions)
    print("Status:", result["status"])