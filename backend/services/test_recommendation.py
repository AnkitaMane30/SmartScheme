from services.recommendation_engine import RecommendationEngine


engine = RecommendationEngine()

print("Total schemes:", len(engine.schemes))
print("Prepared schemes:", len(engine.schemes))
print("TF-IDF matrix shape:", engine.scheme_vectors.shape)


# Test user profile
user_profile = {
    "age": 22,
    "gender": "Female",
    "state": "Maharashtra",
    "district": "Kolhapur",
    "annual_income": 200000,
    "caste_category": "General",
    "occupation": "Student",
    "education_level": "B.Tech",
    "disability_status": False,
    "is_bpl": False,
    "rural_urban": "Urban",
    "marital_status": "Single"
}


# Get recommendations
recommendations = engine.recommend(user_profile)


print("\nRecommendations:")
print("Total recommendations:", len(recommendations))

for recommendation in recommendations[:5]:
    print(recommendation)