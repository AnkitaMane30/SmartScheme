"""
ML Ranker - Uses the trained Random Forest model
to score eligible schemes.
"""

import os
import joblib
import pandas as pd
import numpy as np


class MLRanker:

    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_dir, "ml", "models", "recommendation_model.pkl")
        encoders_path = os.path.join(base_dir, "ml", "models", "label_encoders.pkl")

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at {model_path}. Please train the model first."
            )

        self.model = joblib.load(model_path)
        self.encoders = joblib.load(encoders_path)

        self.categorical_cols = [
            "user_gender",
            "user_caste",
            "user_occupation",
            "user_marital_status",
            "user_state",
            "user_education",
            "scheme_gender",
            "scheme_category",
            "scheme_state",
        ]

        self.numerical_cols = [
            "user_age",
            "user_income",
            "user_disability",
            "user_is_bpl",
            "user_land_owner",
            "scheme_min_age",
            "scheme_max_age",
            "scheme_max_income",
            "tfidf_score",
        ]

    def _safe_encode(self, col_name, value):
        """Encode a categorical value. Unknown values get -1."""
        value = str(value) if value is not None else "Unknown"
        le = self.encoders.get(col_name)

        if le is None:
            return 0

        if value in le.classes_:
            return le.transform([value])[0]
        else:
            # Unseen category during training
            return 0

    def predict_score(self, user_profile, scheme, tfidf_score):
        """
        Returns probability that this scheme is relevant for the user.
        Score is between 0 and 1.
        """

        # Prepare features in the same order as training
        features = {
            "user_age": user_profile.get("age") or 0,
            "user_income": user_profile.get("annual_income") or 0,
            "user_disability": int(user_profile.get("disability_status") or 0),
            "user_is_bpl": int(user_profile.get("is_bpl") or 0),
            "user_land_owner": int(user_profile.get("land_owner") or 0),
            "scheme_min_age": scheme.get("min_age") if scheme.get("min_age") is not None else -1,
            "scheme_max_age": scheme.get("max_age") if scheme.get("max_age") is not None else 999,
            "scheme_max_income": scheme.get("max_income") if scheme.get("max_income") is not None else 99999999,
            "tfidf_score": tfidf_score or 0.0,

            # Categorical (will be encoded)
            "user_gender": user_profile.get("gender") or "Unknown",
            "user_caste": user_profile.get("caste_category") or "Unknown",
            "user_occupation": user_profile.get("occupation") or "Unknown",
            "user_marital_status": user_profile.get("marital_status") or "Unknown",
            "user_state": user_profile.get("state") or "Unknown",
            "user_education": user_profile.get("education_level") or "None",
            "scheme_gender": scheme.get("gender") or "All",
            "scheme_category": scheme.get("category") or "Unknown",
            "scheme_state": scheme.get("state") or "All",
        }

        # Encode categorical columns
        for col in self.categorical_cols:
            features[col] = self._safe_encode(col, features[col])

        # Create DataFrame with correct column order
        feature_order = self.numerical_cols + self.categorical_cols
        X = pd.DataFrame([[features[col] for col in feature_order]], columns=feature_order)

        # Predict probability of class 1 (relevant)
        proba = self.model.predict_proba(X)[0][1]

        return round(float(proba), 4)