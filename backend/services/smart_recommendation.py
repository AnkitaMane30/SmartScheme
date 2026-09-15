import utils.db_connection as db

from services.eligibility_engine import EligibilityEngine
from services.condition_extractor import ConditionExtractor
from services.recommendation_engine import RecommendationEngine
from services.ml_ranker import MLRanker


class SmartRecommendation:

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(self):

        self.eligibility_engine = EligibilityEngine()
        self.condition_extractor = ConditionExtractor()
        self.recommendation_engine = RecommendationEngine()

        # Load trained ML model
        try:
            self.ml_ranker = MLRanker()
            self.use_ml = True
            print("ML Ranker loaded successfully.")
        except Exception as e:
            print(f"ML Ranker not loaded: {e}")
            self.ml_ranker = None
            self.use_ml = False
    # =========================================================
    # LOAD ALL SCHEMES FROM MYSQL
    # =========================================================

    def load_schemes(self):

        sql = """
            SELECT
                scheme_id,
                title,
                details,
                eligibility,
                exclusion,
                benefits,
                category,
                state,
                department,
                gender,
                min_age,
                max_age,
                min_income,
                max_income,
                target_group,
                application_link
            FROM schemes
        """

        schemes = db.executeQuery(sql, ())

        return schemes

    # =========================================================
    # EXTRACT CONDITIONS FROM SCHEME TEXT
    # =========================================================

    def extract_conditions(self, scheme):
        """
        Extract conditions from multiple fields for better accuracy:
        title + eligibility + target_group + exclusion + category
        """
        return self.condition_extractor.extract_from_scheme(scheme)
    # =========================================================
    # CHECK ONE SCHEME
    # =========================================================

    def check_scheme(self, profile, scheme):

        extracted_conditions = self.extract_conditions(
            scheme
        )

        result = self.eligibility_engine.check_scheme_eligibility(
            profile,
            scheme,
            extracted_conditions
        )

        return result

    # =========================================================
    # CHECK ALL SCHEMES
    # =========================================================

    def filter_schemes(self, profile):

        schemes = self.load_schemes()

        eligible_schemes = []

        needs_verification = []

        not_eligible = []

        for scheme in schemes:

            result = self.check_scheme(
                profile,
                scheme
            )

            status = result["status"]

            # -------------------------------------------------
            # ELIGIBLE
            # -------------------------------------------------

            if status == "ELIGIBLE":

                eligible_schemes.append({
                    "scheme": scheme,
                    "eligibility": result
                })

            # -------------------------------------------------
            # NEEDS VERIFICATION
            # -------------------------------------------------

            elif status == "NEEDS_VERIFICATION":

                needs_verification.append({
                    "scheme": scheme,
                    "eligibility": result
                })

            # -------------------------------------------------
            # NOT ELIGIBLE
            # -------------------------------------------------

            elif status == "NOT_ELIGIBLE":

                not_eligible.append({
                    "scheme": scheme,
                    "eligibility": result
                })

        return {
            "eligible": eligible_schemes,
            "needs_verification": needs_verification,
            "not_eligible": not_eligible
        }

    # =========================================================
    # RANK ONLY ELIGIBLE SCHEMES
    # =========================================================

    def rank_eligible_schemes(self, profile, eligible_schemes, top_n=8):

        if not eligible_schemes:
            return []

        # 1. Get TF-IDF scores
        all_tfidf = self.recommendation_engine.recommend(
            profile,
            top_n=len(self.recommendation_engine.schemes)
        )
        tfidf_map = {
            item["scheme_id"]: item["ml_score"]
            for item in all_tfidf
        }

        # 2. Smart Category Boost
        occupation = (profile.get("occupation") or "").lower()
        gender = (profile.get("gender") or "").lower()

        preferred_categories = {
            "student": [
                "scholarship", "education", "education & scholarship",
                "education & learning", "social welfare"
            ],
            "farmer": [
                "agriculture", "farmer", "rural development", "irrigation"
            ],
            "construction worker": [
                "labour", "construction", "worker", "employment"
            ],
            "homemaker": [
                "women", "women & child development", "skill development"
            ],
            "unemployed": [
                "employment", "skill", "youth", "training"
            ]
        }

        user_preferred = []
        for key, cats in preferred_categories.items():
            if key in occupation:
                user_preferred = cats
                break

        if gender == "female":
            user_preferred += ["women", "women & child development", "girl child"]

        ranked = []

        for item in eligible_schemes:
            scheme = item["scheme"]
            scheme_id = scheme["scheme_id"]
            category = (scheme.get("category") or "").lower()
            title = (scheme.get("title") or "").lower()

            tfidf_score = tfidf_map.get(scheme_id, 0.0)   # 0-100

            # ML Score from Random Forest
            if self.use_ml and self.ml_ranker:
                ml_prob = self.ml_ranker.predict_score(profile, scheme, tfidf_score)
                ml_score = ml_prob * 100
            else:
                ml_score = 0

            # Category Boost
            category_boost = 0
            for pref in user_preferred:
                if pref in category or pref in title:
                    if pref in ["scholarship", "education", "education & scholarship"]:
                        category_boost = 30
                    elif pref in ["women", "women & child development", "girl child"]:
                        category_boost = 15
                    else:
                        category_boost = 12
                    break

            # ---------- Improved Final Score ----------
            # More weight to TF-IDF, less to current ML model
            final_score = (0.55 * tfidf_score) + (0.25 * ml_score) + category_boost

            ranked.append({
                "scheme_id": scheme_id,
                "scheme_name": scheme.get("title"),
                "category": scheme.get("category"),
                "department": scheme.get("department"),
                "tfidf_score": round(tfidf_score, 2),
                "ml_score": round(ml_score, 2),
                "category_boost": category_boost,
                "final_score": round(final_score, 2),
                "url": scheme.get("application_link")
            })

        ranked.sort(key=lambda x: x["final_score"], reverse=True)

        return ranked[:top_n]
    # =========================================================
    # FINAL RECOMMENDATION FUNCTION
    # =========================================================

    def recommend(
        self,
        profile,
        top_n=8
    ):

        # -----------------------------------------------------
        # STEP 1:
        # Check eligibility of every scheme
        # -----------------------------------------------------

        eligibility_results = self.filter_schemes(
            profile
        )

        # -----------------------------------------------------
        # STEP 2:
        # Get all eligible schemes
        # -----------------------------------------------------

        eligible_schemes = (
            eligibility_results["eligible"]
        )

        # -----------------------------------------------------
        # STEP 3:
        # Rank ALL eligible schemes
        # -----------------------------------------------------

        recommendations = self.rank_eligible_schemes(
            profile,
            eligible_schemes,
            top_n
        )

        # -----------------------------------------------------
        # STEP 4:
        # Return final result
        # -----------------------------------------------------

        return {

            "total_schemes": (
                len(eligibility_results["eligible"])
                +
                len(eligibility_results["needs_verification"])
                +
                len(eligibility_results["not_eligible"])
            ),

            "eligible_count": len(
                eligibility_results["eligible"]
            ),

            "needs_verification_count": len(
                eligibility_results["needs_verification"]
            ),

            "not_eligible_count": len(
                eligibility_results["not_eligible"]
            ),

            "recommendations": recommendations
        }