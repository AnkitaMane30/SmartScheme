import re


class ConditionExtractor:

    # =========================================================
    # AGE
    # =========================================================

    def extract_age(self, text):

        if not text:
            return []

        text = text.lower()
        conditions = []

        # age 18 to 50 / age between 18 and 50 / aged 18-50
        patterns = [
            r"(?:age|aged)[^\d]{0,30}(\d{1,3})\s*(?:to|-|and)\s*(\d{1,3})",
            r"(?:between)[^\d]{0,10}(\d{1,3})\s*(?:and|to|-)\s*(\d{1,3})"
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            for minimum, maximum in matches:
                conditions.append({
                    "field": "age",
                    "operator": "BETWEEN",
                    "value": [int(minimum), int(maximum)]
                })

        # age above 18 / minimum age 18
        minimum_patterns = [
            r"(?:age|aged)[^\d]{0,20}(\d{1,3})\s*(?:years?)?\s*(?:and)?\s*(?:above|over|or above)",
            r"(?:minimum age)[^\d]{0,10}(\d{1,3})",
            r"(?:age of)\s*(\d{1,3})\s*(?:years?)?\s*(?:and above|or above|and older)"
        ]

        for pattern in minimum_patterns:
            matches = re.findall(pattern, text)
            for minimum in matches:
                conditions.append({
                    "field": "age",
                    "operator": ">=",
                    "value": int(minimum)
                })

        # age below 65 / maximum age 65
        maximum_patterns = [
            r"(?:age|aged)[^\d]{0,20}(\d{1,3})\s*(?:years?)?\s*(?:and)?\s*(?:below|under|or below)",
            r"(?:maximum age)[^\d]{0,10}(\d{1,3})",
            r"(?:upto|up to)\s*(\d{1,3})\s*(?:years?)?"
        ]

        for pattern in maximum_patterns:
            matches = re.findall(pattern, text)
            for maximum in matches:
                conditions.append({
                    "field": "age",
                    "operator": "<=",
                    "value": int(maximum)
                })

        return conditions

    # =========================================================
    # INCOME
    # =========================================================

    def extract_income(self, text):

        if not text:
            return []

        text = text.lower()
        conditions = []

        def convert_amount(amount, unit):
            amount = float(amount)
            if unit in ["lakh", "lakhs"]:
                amount *= 100000
            elif unit in ["thousand", "thousands"]:
                amount *= 1000
            elif unit in ["crore", "crores"]:
                amount *= 10000000
            return int(amount)

        # Income <= value
        pattern = (
            r"(?:income|annual family income|family income|annual income)"
            r"[^₹\d]{0,50}"
            r"(?:rs\.?|₹)?\s*"
            r"(\d+(?:\.\d+)?)\s*"
            r"(lakh|lakhs|crore|crores|thousand|thousands|k)?"
        )

        matches = re.findall(pattern, text)

        for amount, unit in matches:
            value = convert_amount(amount, unit)
            conditions.append({
                "field": "annual_income",
                "operator": "<=",
                "value": value
            })

        return conditions

    # =========================================================
    # GENDER
    # =========================================================

    def extract_gender(self, text):

        if not text:
            return []

        text = text.lower()
        conditions = []

        female_patterns = [
            r"\bwoman\b", r"\bwomen\b", r"\bfemale\b",
            r"\bgirl\b", r"\bgirls\b", r"\bgirl child\b",
            r"\bwidow\b", r"\bwidows\b"
        ]

        male_patterns = [
            r"\bman\b", r"\bmen\b", r"\bmale\b",
            r"\bboy\b", r"\bboys\b"
        ]

        female_found = any(re.search(p, text) for p in female_patterns)
        male_found = any(re.search(p, text) for p in male_patterns)

        # Only create gender condition if only one gender is clearly targeted
        if female_found and not male_found:
            conditions.append({
                "field": "gender",
                "operator": "IN",
                "value": ["female"]
            })
        elif male_found and not female_found:
            conditions.append({
                "field": "gender",
                "operator": "IN",
                "value": ["male"]
            })

        return conditions

    # =========================================================
    # CASTE / CATEGORY  (STRICT)
    # =========================================================

    def extract_caste(self, text):

        if not text:
            return []

        text = text.lower()
        conditions = []

        # More complete and stricter mapping
        caste_mapping = {
            # SC
            "scheduled caste": "SC",
            "scheduled castes": "SC",
            "sc / neo-buddhist": "SC",
            "sc/neo-buddhist": "SC",
            "sc/neo buddhist": "SC",
            "neo-buddhist": "SC",
            "neo buddhist": "SC",
            "sc students": "SC",
            "sc student": "SC",
            "sc category": "SC",
            "sc/st": "SC",

            # ST
            "scheduled tribe": "ST",
            "scheduled tribes": "ST",
            "st students": "ST",
            "st student": "ST",
            "st category": "ST",

            # VJNT
            "vimukta jatis": "VJNT",
            "vimukta jati": "VJNT",
            "nomadic tribes": "VJNT",
            "nomadic tribe": "VJNT",
            "vjnt": "VJNT",
            "vj / nt": "VJNT",
            "v.j.nt": "VJNT",
            "vjnt students": "VJNT",

            # SBC
            "sbc": "SBC",
            "special backward class": "SBC",
            "special backward classes": "SBC",

            # OBC
            "other backward class": "OBC",
            "other backward classes": "OBC",
            "obc": "OBC",
            "obc students": "OBC",

            # Backward Class
            "backward class": "OBC",
            "backward classes": "OBC",
            "backward class students": "OBC",
        }

        found_categories = []

        for keyword, category in caste_mapping.items():
            if keyword in text:
                if category not in found_categories:
                    found_categories.append(category)

        # Special handling for "SC/ST"
        if "sc/st" in text or "sc / st" in text:
            if "SC" not in found_categories:
                found_categories.append("SC")
            if "ST" not in found_categories:
                found_categories.append("ST")

        if found_categories:
            conditions.append({
                "field": "caste_category",
                "operator": "IN",
                "value": found_categories
            })

        return conditions

    # =========================================================
    # OCCUPATION
    # =========================================================

    def extract_occupation(self, text):

        if not text:
            return []

        text = text.lower()
        conditions = []

        occupation_mapping = {
            "farmer": "farmer",
            "farmers": "farmer",
            "agricultural labourer": "agricultural labourer",
            "agricultural laborer": "agricultural labourer",
            "agricultural labourers": "agricultural labourer",
            "construction worker": "construction worker",
            "construction workers": "construction worker",
            "registered construction worker": "construction worker",
            "registered construction workers": "construction worker",
            "landless labourer": "landless labourer",
            "landless laborer": "landless labourer",
            "landless labourers": "landless labourer",
            "student": "student",
            "students": "student",
            "unemployed": "unemployed",
            "unemployed youth": "unemployed",
            "homemaker": "homemaker",
            "housewife": "homemaker",
            "self employed": "self employed",
            "self-employed": "self employed",
        }

        found_occupations = []

        for keyword, occupation in occupation_mapping.items():
            if keyword in text:
                if occupation not in found_occupations:
                    found_occupations.append(occupation)

        if found_occupations:
            conditions.append({
                "field": "occupation",
                "operator": "IN",
                "value": found_occupations
            })

        return conditions

    # =========================================================
    # LAND OWNERSHIP (NEW)
    # =========================================================

    def extract_land_ownership(self, text):

        if not text:
            return []

        text = text.lower()

        land_owner_keywords = [
            "land owner", "landowner", "land holding", "landholding",
            "owns land", "own land", "agricultural land",
            "farmer who owns", "land owning"
        ]

        landless_keywords = [
            "landless", "land less", "without land", "no land"
        ]

        if any(k in text for k in landless_keywords):
            return [{
                "field": "land_owner",
                "operator": "==",
                "value": False
            }]

        if any(k in text for k in land_owner_keywords):
            return [{
                "field": "land_owner",
                "operator": "==",
                "value": True
            }]

        return []

    # =========================================================
    # MARITAL STATUS (NEW)
    # =========================================================

    def extract_marital_status(self, text):

        if not text:
            return []

        text = text.lower()
        conditions = []

        if any(k in text for k in ["widow", "widows", "widowed"]):
            conditions.append({
                "field": "marital_status",
                "operator": "IN",
                "value": ["widow", "widowed"]
            })

        if any(k in text for k in ["unmarried", "single woman", "single women"]):
            conditions.append({
                "field": "marital_status",
                "operator": "IN",
                "value": ["single", "unmarried"]
            })

        if "married" in text and "unmarried" not in text and "widow" not in text:
            if "married women" in text or "married woman" in text:
                conditions.append({
                    "field": "marital_status",
                    "operator": "IN",
                    "value": ["married"]
                })

        return conditions

    # =========================================================
    # DISABILITY
    # =========================================================

    def extract_disability(self, text):

        if not text:
            return []

        text = text.lower()

        disability_keywords = [
            "person with disability", "persons with disabilities",
            "persons with disability", "disabled person", "disabled persons",
            "disability", "divyang", "divyangjan", "pwd", "differently abled"
        ]

        if any(keyword in text for keyword in disability_keywords):
            return [{
                "field": "disability_status",
                "operator": "==",
                "value": True
            }]

        return []

    # =========================================================
    # BPL
    # =========================================================

    def extract_bpl(self, text):

        if not text:
            return []

        text = text.lower()

        bpl_keywords = [
            "below poverty line", "bpl", "bpl family",
            "bpl families", "bpl card", "yellow ration card"
        ]

        if any(keyword in text for keyword in bpl_keywords):
            return [{
                "field": "is_bpl",
                "operator": "==",
                "value": True
            }]

        return []

    # =========================================================
    # EXTRACT ALL CONDITIONS
    # =========================================================

    def extract_all(self, text):
        if not text:
            return []

        conditions = []

        conditions.extend(self.extract_age(text))
        conditions.extend(self.extract_income(text))
        conditions.extend(self.extract_gender(text))
        conditions.extend(self.extract_caste(text))
        conditions.extend(self.extract_occupation(text))
        conditions.extend(self.extract_land_ownership(text))
        conditions.extend(self.extract_marital_status(text))
        conditions.extend(self.extract_disability(text))
        conditions.extend(self.extract_bpl(text))

        return conditions

    # =========================================================
    # EXTRACT FROM FULL SCHEME (BEST METHOD)
    # =========================================================

    def extract_from_scheme(self, scheme):
        """
        Extract from title + eligibility + target_group + exclusion + category
        """
        parts = [
            scheme.get("title") or "",
            scheme.get("eligibility") or "",
            scheme.get("target_group") or "",
            scheme.get("exclusion") or "",
            scheme.get("category") or "",
        ]

        combined_text = " ".join(str(p) for p in parts if p)
        return self.extract_all(combined_text)