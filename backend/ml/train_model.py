"""
Train Random Forest recommendation model.

Features used:
- User features (age, gender, caste, occupation, income, etc.)
- Scheme features (min_age, max_age, max_income, gender, category)
- TF-IDF similarity score

Label: relevant (1 = eligible, 0 = not eligible)  [weak supervision]
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "training_data.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "recommendation_model.pkl")
ENCODERS_PATH = os.path.join(MODEL_DIR, "label_encoders.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():
    if not os.path.exists(DATA_FILE):
        print(f"ERROR: {DATA_FILE} not found.")
        print("Please run generate_training_data.py first.")
        sys.exit(1)

    df = pd.read_csv(DATA_FILE)
    print(f"Loaded training data: {len(df)} rows")
    print(f"Positive samples: {df['relevant'].sum()}")
    print(f"Negative samples: {len(df) - df['relevant'].sum()}")
    return df


# ============================================================
# PREPROCESS
# ============================================================

CATEGORICAL_COLS = [
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

NUMERICAL_COLS = [
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


def preprocess(df):
    """
    Encode categorical columns and prepare X, y.
    """
    df = df.copy()
    encoders = {}

    for col in CATEGORICAL_COLS:
        le = LabelEncoder()
        df[col] = df[col].astype(str).fillna("Unknown")
        df[col] = le.fit_transform(df[col])
        encoders[col] = le

    feature_cols = NUMERICAL_COLS + CATEGORICAL_COLS

    X = df[feature_cols]
    y = df["relevant"]

    return X, y, encoders, feature_cols


# ============================================================
# TRAIN
# ============================================================

def train():
    print("=" * 60)
    print("TRAINING RANDOM FOREST MODEL")
    print("=" * 60)

    df = load_data()
    X, y, encoders, feature_cols = preprocess(df)

    # Train / Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    print(f"\nTrain size: {len(X_train)}")
    print(f"Test size : {len(X_test)}")

    # Random Forest
    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    print("\nTraining model...")
    model.fit(X_train, y_train)

    # ---------------- Evaluation ----------------
    y_pred = model.predict(X_test)

    print("\n" + "=" * 60)
    print("MODEL PERFORMANCE")
    print("=" * 60)
    print(f"Accuracy : {accuracy_score(y_test, y_pred):.4f}")
    print(f"Precision: {precision_score(y_test, y_pred):.4f}")
    print(f"Recall   : {recall_score(y_test, y_pred):.4f}")
    print(f"F1 Score : {f1_score(y_test, y_pred):.4f}")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Not Relevant", "Relevant"]))

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Feature Importance
    print("\nTop Feature Importances:")
    importances = pd.Series(model.feature_importances_, index=feature_cols)
    print(importances.sort_values(ascending=False).head(10))

    # ---------------- Save ----------------
    joblib.dump(model, MODEL_PATH)
    joblib.dump(encoders, ENCODERS_PATH)

    print("\n" + "=" * 60)
    print("MODEL SAVED SUCCESSFULLY")
    print("=" * 60)
    print(f"Model    → {MODEL_PATH}")
    print(f"Encoders → {ENCODERS_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    train()