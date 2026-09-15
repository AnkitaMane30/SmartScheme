import re
import pandas as pd
import utils.db_connection as db

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class RecommendationEngine:

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1
        )

        self.scheme_vectors = None
        self.schemes = None

        # Load schemes from MySQL
        schemes = self.load_schemes_from_db()

        # Prepare schemes and create TF-IDF vectors
        self.prepare_schemes(schemes)

    # =========================================
    # TEXT CLEANING
    # =========================================

    def clean_text(self, value):

        if value is None:
            return ""

        value = str(value)

        if value.strip().upper() in ["\\N", "NULL", "NONE", "NAN"]:
            return ""

        value = re.sub(r"\s+", " ", value)

        return value.strip().lower()

    # =========================================
    # BUILD SCHEME TEXT
    # =========================================

    def build_scheme_text(self, scheme):

        fields = [
            scheme.get("title"),
            scheme.get("category"),
            scheme.get("eligibility"),
            scheme.get("details"),
            scheme.get("department"),
            scheme.get("target_group"),
            scheme.get("benefits")
        ]

        return " ".join(
            self.clean_text(field)
            for field in fields
        )

    # =========================================
    # PREPARE SCHEME DATA
    # =========================================

    def prepare_schemes(self, schemes):

        cleaned_schemes = []

        for scheme in schemes:

            scheme = dict(scheme)

            scheme["title"] = self.clean_text(
                scheme.get("title")
            )

            if len(scheme["title"]) < 4:
                continue

            scheme["scheme_text"] = self.build_scheme_text(
                scheme
            )

            cleaned_schemes.append(scheme)

        self.schemes = pd.DataFrame(cleaned_schemes)

        if self.schemes.empty:
            self.scheme_vectors = None
            return

        self.scheme_vectors = self.vectorizer.fit_transform(
            self.schemes["scheme_text"]
        )

    # =========================================
    # BUILD USER TEXT
    # =========================================

    def build_user_text(self, profile):

        parts = []

        # Basic info
        if profile.get("occupation"):
            parts.append(str(profile.get("occupation")))
        if profile.get("education_level"):
            parts.append(str(profile.get("education_level")))
        if profile.get("course"):
            parts.append(str(profile.get("course")))
        if profile.get("caste_category"):
            parts.append(str(profile.get("caste_category")))
        if profile.get("gender"):
            parts.append(str(profile.get("gender")))
        if profile.get("state"):
            parts.append(str(profile.get("state")))
        if profile.get("district"):
            parts.append(str(profile.get("district")))

        # Extra meaningful words based on occupation
        occupation = (profile.get("occupation") or "").lower()

        if "student" in occupation:
            parts.extend([
                "student", "education", "scholarship", "college",
                "higher education", "tuition", "hostel", "study"
            ])
        elif "farmer" in occupation:
            parts.extend([
                "farmer", "agriculture", "farming", "crop", "irrigation",
                "land", "soil", "agricultural"
            ])
        elif "homemaker" in occupation or "housewife" in occupation:
            parts.extend([
                "women", "homemaker", "self help group", "skill development",
                "women empowerment", "home based", "training"
            ])
        elif "construction" in occupation:
            parts.extend([
                "construction worker", "labour", "worker", "building", "wage"
            ])
        elif "unemployed" in occupation:
            parts.extend([
                "unemployed", "employment", "skill", "training", "job", "youth"
            ])

        # Gender specific
        if (profile.get("gender") or "").lower() == "female":
            parts.extend(["women", "female", "girl"])

        return " ".join(self.clean_text(p) for p in parts if p)
    # =========================================
    # GENERATE RECOMMENDATIONS
    # =========================================

    def recommend(self, profile, top_n=8):

        if self.schemes is None or self.schemes.empty:
            return []

        if self.scheme_vectors is None:
            return []

        user_text = self.build_user_text(profile)

        user_vector = self.vectorizer.transform(
            [user_text]
        )

        similarities = cosine_similarity(
            user_vector,
            self.scheme_vectors
        )[0]

        results = []

        for index, similarity in enumerate(similarities):

            scheme = self.schemes.iloc[index]

            results.append({
                "scheme_id": scheme.get("scheme_id"),
                "scheme_name": scheme.get("title"),
                "category": scheme.get("category"),
                "department": scheme.get("department"),
                "ml_score": round(
                    float(similarity) * 100,
                    2
                ),
                "url": scheme.get("application_link")
            })

        results.sort(
            key=lambda x: x["ml_score"],
            reverse=True
        )

        return results[:top_n]

   #==================================
   # Connect the ML engine to MySQL
   #==================================
    def load_schemes_from_db(self):

        sql = """
            SELECT
                scheme_id,
                title,
                details,
                eligibility,
                benefits,
                exclusion,
                category,
                state,
                department,
                gender,
                min_age,
                max_age,
                target_group,
                application_link
            FROM schemes
        """

        schemes = db.executeQuery(sql, ())

        return schemes