class EligibilityEngine:

    # =========================================
    # CHECK ONE CONDITION
    # =========================================
    def check_condition(self, user_value, operator, required_value):

        # We cannot verify the condition
        if user_value is None or user_value == "":
            return "UNKNOWN"

        try:
            if operator == "==":
                return (
                    "PASS"
                    if str(user_value).strip().lower()
                    == str(required_value).strip().lower()
                    else "FAIL"
                )

            if operator == "!=":
                return (
                    "PASS"
                    if str(user_value).strip().lower()
                    != str(required_value).strip().lower()
                    else "FAIL"
                )

            if operator == ">=":
                return (
                    "PASS"
                    if float(user_value) >= float(required_value)
                    else "FAIL"
                )

            if operator == "<=":
                return (
                    "PASS"
                    if float(user_value) <= float(required_value)
                    else "FAIL"
                )

            if operator == ">":
                return (
                    "PASS"
                    if float(user_value) > float(required_value)
                    else "FAIL"
                )

            if operator == "<":
                return (
                    "PASS"
                    if float(user_value) < float(required_value)
                    else "FAIL"
                )

            if operator == "BETWEEN":
                minimum = float(required_value[0])
                maximum = float(required_value[1])
                value = float(user_value)

                return (
                    "PASS"
                    if minimum <= value <= maximum
                    else "FAIL"
                )

            if operator == "IN":
                normalized_user_value = str(user_value).strip().lower()

                normalized_required_values = [
                    str(value).strip().lower()
                    for value in required_value
                ]

                return (
                    "PASS"
                    if normalized_user_value in normalized_required_values
                    else "FAIL"
                )

        except (ValueError, TypeError, IndexError):
            return "UNKNOWN"

        return "UNKNOWN"

    # =========================================
    # CHECK COMPLETE ELIGIBILITY
    # =========================================
    def check_eligibility(self, user_profile, conditions):

        failed_conditions = []
        unknown_conditions = []
        passed_conditions = []

        for condition in conditions:

            field = condition.get("field")
            operator = condition.get("operator")
            required_value = condition.get("value")

            user_value = user_profile.get(field)

            result = self.check_condition(
                user_value,
                operator,
                required_value
            )

            condition_result = {
                "field": field,
                "operator": operator,
                "required_value": required_value,
                "user_value": user_value
            }

            if result == "FAIL":
                failed_conditions.append(condition_result)

            elif result == "UNKNOWN":
                unknown_conditions.append(condition_result)

            else:
                passed_conditions.append(condition_result)

        # At least one definite failure
        if failed_conditions:
            status = "NOT_ELIGIBLE"

        # No failures, but some conditions cannot be verified
        elif unknown_conditions:
            status = "NEEDS_VERIFICATION"

        # Every condition passed
        else:
            status = "ELIGIBLE"

        return {
            "status": status,
            "passed_conditions": passed_conditions,
            "failed_conditions": failed_conditions,
            "unknown_conditions": unknown_conditions
        }

    def build_conditions_from_scheme(self, scheme):
        conditions = []

        # -------------------------
        # AGE
        # -------------------------
        if scheme.get("min_age") is not None and scheme.get("max_age") is not None:
            conditions.append({
                "field": "age",
                "operator": "BETWEEN",
                "value": [
                    scheme["min_age"],
                    scheme["max_age"]
                ]
            })

        elif scheme.get("min_age") is not None:
            conditions.append({
                "field": "age",
                "operator": ">=",
                "value": scheme["min_age"]
            })

        elif scheme.get("max_age") is not None:
            conditions.append({
                "field": "age",
                "operator": "<=",
                "value": scheme["max_age"]
            })

        # -------------------------
        # INCOME
        # -------------------------
        if scheme.get("max_income") is not None:
            conditions.append({
                "field": "annual_income",
                "operator": "<=",
                "value": scheme["max_income"]
            })

        elif scheme.get("min_income") is not None:
            conditions.append({
                "field": "annual_income",
                "operator": ">=",
                "value": scheme["min_income"]
            })

        # -------------------------
        # GENDER
        # -------------------------
        gender = scheme.get("gender")

        if gender and str(gender).strip().lower() not in [
            "all",
            "any",
            "both",
            "null"
        ]:
            conditions.append({
                "field": "gender",
                "operator": "IN",
                "value": [gender]
            })

        # -------------------------
        # STATE
        # -------------------------
        state = scheme.get("state")

        if state and str(state).strip().lower() not in [
            "all",
            "india",
            "national"
        ]:
            conditions.append({
                "field": "state",
                "operator": "IN",
                "value": [state]
            })

        return conditions

    def check_scheme_eligibility(self, profile, scheme, extracted_conditions):
            """
            Check a scheme using both:
            1. Structured database conditions
            2. Conditions extracted from eligibility text
            """

            conditions = []

            # --------------------------------
            # 1. Structured DB conditions
            # --------------------------------
            structured_conditions = self.build_conditions_from_scheme(scheme)

            conditions.extend(structured_conditions)

            # --------------------------------
            # 2. Extracted text conditions
            # --------------------------------
            conditions.extend(extracted_conditions)

            # --------------------------------
            # 3. Check all conditions
            # --------------------------------
            result = self.check_eligibility(
                profile,
                conditions
            )

            return result