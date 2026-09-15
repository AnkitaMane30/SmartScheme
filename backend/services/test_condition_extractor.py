from services.condition_extractor import ConditionExtractor


extractor = ConditionExtractor()

text = """
The applicant should be a woman between age 21 to 65
years of age and should have an annual family income
not exceeding Rs. 2 lakh.
"""

age_conditions = extractor.extract_age(text)
income_conditions = extractor.extract_income(text)
gender_conditions = extractor.extract_gender(text)

print("Extracted conditions:")

for condition in age_conditions:
    print(condition)

for condition in income_conditions:
    print(condition)

for condition in gender_conditions:
    print(condition)