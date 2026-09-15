from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from utils.utils import crypto, createResult
import utils.db_connection as db


usersRouter = Blueprint(
    "users",
    __name__,
    url_prefix="/users"
)


# ============================================================
# BOOLEAN HELPER
# ============================================================

def to_bool(value):
    """
    Converts frontend Yes/No or 0/1 values
    into Python Boolean values.

    Yes  -> True
    No   -> False
    1    -> True
    0    -> False
    True -> True
    False -> False
    """

    if value is True or value == 1 or value == "1":
        return True

    if value is False or value == 0 or value == "0":
        return False

    if isinstance(value, str):
        value = value.strip().lower()

        if value in ["yes", "true"]:
            return True

        if value in ["no", "false"]:
            return False

    return None


# ============================================================
# BOOLEAN RESPONSE HELPER
# ============================================================

def convert_boolean_fields(user):
    """
    Converts MySQL 0/1 values into Python True/False
    before sending them to React/recommendation system.
    """

    boolean_fields = [
        "disability_status",
        "is_bpl",
        "loan_required",
        "house_ownership",
        "current_scholarship",
        "land_owner",
        "irrigation_available",
        "agricultural_loan",
        "business_registered",
        "business_financial_need",
        "home_based_business",
        "business_interest",
        "profile_completed"
    ]

    for field in boolean_fields:
        if field in user and user[field] is not None:
            user[field] = bool(user[field])

    return user


# ============================================================
# REGISTER
# ============================================================

@usersRouter.route("/register", methods=["POST"])
def register():

    try:

        data = request.get_json()

        if not data:
            return createResult("Registration data required")

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not name or not email or not password:
            return createResult(
                "Name, email and password are required"
            )

        hashed_password = crypto.hash(password)

        sql = """
            INSERT INTO users(
                name,
                email,
                password
            )
            VALUES(%s, %s, %s)
        """

        db.executeQuery(
            sql,
            (
                name,
                email,
                hashed_password
            )
        )

        return createResult(
            None,
            "User registered successfully"
        )

    except Exception as e:

        print("REGISTER ERROR:", e)

        return createResult(
            "Failed to register user"
        )


# ============================================================
# LOGIN
# ============================================================

@usersRouter.route("/login", methods=["POST"])
def login():

    try:

        data = request.get_json()

        if not data:
            return createResult(
                "Email and password required"
            )

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return createResult(
                "Email and password required"
            )

        sql = """
            SELECT
                email,
                password
            FROM users
            WHERE email=%s
        """

        result = db.executeQuery(
            sql,
            (email,)
        )

        if not result:
            return createResult(
                "Invalid email or password"
            )

        user = result[0]

        if not crypto.verify(
            password,
            user["password"]
        ):
            return createResult(
                "Invalid email or password"
            )

        token = create_access_token(
            identity=user["email"]
        )

        return createResult(
            None,
            {
                "email": user["email"],
                "token": token
            }
        )

    except Exception as e:

        print("LOGIN ERROR:", e)

        return createResult(
            "Login failed"
        )


# ============================================================
# PROFILE
# ============================================================

@usersRouter.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():

    try:

        email = get_jwt_identity()

        sql = """
            SELECT
                name,
                email,
                age,
                gender,
                state,
                occupation
            FROM users
            WHERE email=%s
        """

        result = db.executeQuery(
            sql,
            (email,)
        )

        if not result:
            return createResult(
                "User not found"
            )

        return createResult(
            None,
            result[0]
        )

    except Exception as e:

        print("PROFILE ERROR:", e)

        return createResult(
            "Failed to fetch profile"
        )


# ============================================================
# USER INFO
# ============================================================

@usersRouter.route("/user-info", methods=["GET"])
@jwt_required()
def get_user_info():

    try:

        email = get_jwt_identity()

        sql = """
            SELECT

                name,
                email,

                age,
                gender,
                state,
                district,
                marital_status,
                disability_status,
                annual_income,
                is_bpl,
                rural_urban,
                caste_category,
                loan_required,
                house_ownership,
                occupation,

                education_level,
                course,
                year_of_study,
                institution_type,
                current_scholarship,

                land_owner,
                land_holding,
                farming_type,
                irrigation_available,
                agricultural_loan,

                business_type,
                business_registered,
                business_age,
                business_turnover,
                business_financial_need,

                skills,
                home_based_business,
                business_interest,

                profile_completed

            FROM users
            WHERE email=%s
        """

        result = db.executeQuery(
            sql,
            (email,)
        )

        if not result:
            return createResult(
                "User not found"
            )

        user = result[0]

        # Convert DB 0/1 → Python True/False
        user = convert_boolean_fields(user)

        return createResult(
            None,
            user
        )

    except Exception as e:

        print("USER INFO ERROR:", e)

        return createResult(
            "Failed to fetch user information"
        )


# ============================================================
# UPDATE USER INFO
# ============================================================

@usersRouter.route("/update-user-info", methods=["POST"])
@jwt_required()
def update_user_info():

    try:

        data = request.get_json()

        if not data:
            return createResult(
                "No data provided"
            )

        email = get_jwt_identity()

        # ====================================================
        # COMMON FIELDS
        # ====================================================

        age = data.get("age")
        gender = data.get("gender")
        state = data.get("state")
        district = data.get("district")
        marital_status = data.get("marital_status")

        disability_status = to_bool(
            data.get("disability_status")
        )

        annual_income = data.get("annual_income")

        is_bpl = to_bool(
            data.get("is_bpl")
        )

        rural_urban = data.get("rural_urban")
        caste_category = data.get("caste_category")

        loan_required = to_bool(
            data.get("loan_required")
        )

        house_ownership = to_bool(
            data.get("house_ownership")
        )

        occupation = data.get("occupation")

        # ====================================================
        # COMMON VALIDATION
        # ====================================================

        common_fields = {
            "age": age,
            "gender": gender,
            "state": state,
            "district": district,
            "marital_status": marital_status,
            "disability_status": disability_status,
            "annual_income": annual_income,
            "is_bpl": is_bpl,
            "rural_urban": rural_urban,
            "caste_category": caste_category,
            "loan_required": loan_required,
            "house_ownership": house_ownership,
            "occupation": occupation
        }

        for field, value in common_fields.items():

            if value is None or value == "":
                return createResult(
                    f"{field} is required"
                )

        # ====================================================
        # INITIALIZE OPTIONAL FIELDS
        # ====================================================

        education_level = None
        course = None
        year_of_study = None
        institution_type = None
        current_scholarship = None

        land_owner = None
        land_holding = None
        farming_type = None
        irrigation_available = None
        agricultural_loan = None

        business_type = None
        business_registered = None
        business_age = None
        business_turnover = None
        business_financial_need = None

        skills = None
        home_based_business = None
        business_interest = None

        # ====================================================
        # STUDENT
        # ====================================================

        if occupation == "Student":

            education_level = data.get("education_level")
            course = data.get("course")
            year_of_study = data.get("year_of_study")
            institution_type = data.get("institution_type")

            current_scholarship = to_bool(
                data.get("current_scholarship")
            )

            fields = {
                "education_level": education_level,
                "course": course,
                "year_of_study": year_of_study,
                "institution_type": institution_type,
                "current_scholarship": current_scholarship
            }

            for field, value in fields.items():

                if value is None or value == "":
                    return createResult(
                        f"{field} is required"
                    )

        # ====================================================
        # FARMER
        # ====================================================

        elif occupation == "Farmer":

            land_owner = to_bool(
                data.get("land_owner")
            )

            land_holding = data.get("land_holding")
            farming_type = data.get("farming_type")

            irrigation_available = to_bool(
                data.get("irrigation_available")
            )

            agricultural_loan = to_bool(
                data.get("agricultural_loan")
            )

            fields = {
                "land_owner": land_owner,
                "land_holding": land_holding,
                "farming_type": farming_type,
                "irrigation_available": irrigation_available,
                "agricultural_loan": agricultural_loan
            }

            for field, value in fields.items():

                if value is None or value == "":
                    return createResult(
                        f"{field} is required"
                    )

        # ====================================================
        # BUSINESS
        # ====================================================

        elif occupation == "Business Owner / Self-employed":

            business_type = data.get("business_type")

            business_registered = to_bool(
                data.get("business_registered")
            )

            business_age = data.get("business_age")
            business_turnover = data.get("business_turnover")

            business_financial_need = to_bool(
                data.get("business_financial_need")
            )

            fields = {
                "business_type": business_type,
                "business_registered": business_registered,
                "business_age": business_age,
                "business_turnover": business_turnover,
                "business_financial_need": business_financial_need
            }

            for field, value in fields.items():

                if value is None or value == "":
                    return createResult(
                        f"{field} is required"
                    )

        # ====================================================
        # HOMEMAKER
        # ====================================================

        elif occupation == "Homemaker":

            education_level = data.get(
                "education_level"
            )

            skills = data.get(
                "skills"
            )

            home_based_business = to_bool(
                data.get("home_based_business")
            )

            business_interest = to_bool(
                data.get("business_interest")
            )

            fields = {
                "education_level": education_level,
                "skills": skills,
                "home_based_business": home_based_business,
                "business_interest": business_interest
            }

            for field, value in fields.items():

                if value is None or value == "":
                    return createResult(
                        f"{field} is required"
                    )

        elif occupation == "Other":

            pass

        else:

            return createResult(
                "Invalid occupation"
            )

        # ====================================================
        # UPDATE DATABASE
        # ====================================================

        sql = """
            UPDATE users
            SET

                age=%s,
                gender=%s,
                state=%s,
                district=%s,
                marital_status=%s,
                disability_status=%s,
                annual_income=%s,
                is_bpl=%s,
                rural_urban=%s,
                caste_category=%s,
                loan_required=%s,
                house_ownership=%s,
                occupation=%s,

                education_level=%s,
                course=%s,
                year_of_study=%s,
                institution_type=%s,
                current_scholarship=%s,

                land_owner=%s,
                land_holding=%s,
                farming_type=%s,
                irrigation_available=%s,
                agricultural_loan=%s,

                business_type=%s,
                business_registered=%s,
                business_age=%s,
                business_turnover=%s,
                business_financial_need=%s,

                skills=%s,
                home_based_business=%s,
                business_interest=%s

            WHERE email=%s
        """

        params = (
            age,
            gender,
            state,
            district,
            marital_status,
            disability_status,
            annual_income,
            is_bpl,
            rural_urban,
            caste_category,
            loan_required,
            house_ownership,
            occupation,

            education_level,
            course,
            year_of_study,
            institution_type,
            current_scholarship,

            land_owner,
            land_holding,
            farming_type,
            irrigation_available,
            agricultural_loan,

            business_type,
            business_registered,
            business_age,
            business_turnover,
            business_financial_need,

            skills,
            home_based_business,
            business_interest,

            email
        )

        db.executeQuery(
            sql,
            params
        )

        return createResult(
            None,
            "User information updated successfully"
        )

    except Exception as e:

        print("UPDATE USER INFO ERROR:", e)

        return createResult(
            "Failed to update user information"
        )


# ============================================================
# COMPLETE PROFILE
# ============================================================

@usersRouter.route("/complete-profile", methods=["POST"])
@jwt_required()
def complete_profile():

    try:

        email = get_jwt_identity()

        # ====================================================
        # CHECK USER
        # ====================================================

        check_sql = """
            SELECT profile_completed
            FROM users
            WHERE email=%s
        """

        existing_user = db.executeQuery(
            check_sql,
            (email,)
        )

        if not existing_user:
            return createResult(
                "User not found"
            )

        if existing_user[0]["profile_completed"]:
            return createResult(
                "Profile already completed. Please use Update Profile."
            )

        # ====================================================
        # GET DATA
        # ====================================================

        data = request.get_json()

        if not data:
            return createResult(
                "Questionnaire data required"
            )

        print("COMPLETE PROFILE DATA:")
        print(data)

        # ====================================================
        # COMMON FIELDS
        # ====================================================

        age = data.get("age")
        gender = data.get("gender")
        state = data.get("state")
        district = data.get("district")
        marital_status = data.get("marital_status")

        disability_status = to_bool(
            data.get("disability_status")
        )

        annual_income = data.get("annual_income")

        is_bpl = to_bool(
            data.get("is_bpl")
        )

        rural_urban = data.get("rural_urban")
        caste_category = data.get("caste_category")

        loan_required = to_bool(
            data.get("loan_required")
        )

        house_ownership = to_bool(
            data.get("house_ownership")
        )

        occupation = data.get("occupation")

        # ====================================================
        # COMMON VALIDATION
        # ====================================================

        common_fields = {
            "age": age,
            "gender": gender,
            "state": state,
            "district": district,
            "marital_status": marital_status,
            "disability_status": disability_status,
            "annual_income": annual_income,
            "is_bpl": is_bpl,
            "rural_urban": rural_urban,
            "caste_category": caste_category,
            "loan_required": loan_required,
            "house_ownership": house_ownership,
            "occupation": occupation
        }

        for field, value in common_fields.items():

            if value is None or value == "":
                return createResult(
                    f"{field} is required"
                )

        # ====================================================
        # INITIALIZE OPTIONAL FIELDS
        # ====================================================

        education_level = None
        course = None
        year_of_study = None
        institution_type = None
        current_scholarship = None

        land_owner = None
        land_holding = None
        farming_type = None
        irrigation_available = None
        agricultural_loan = None

        business_type = None
        business_registered = None
        business_age = None
        business_turnover = None
        business_financial_need = None

        skills = None
        home_based_business = None
        business_interest = None

        # ====================================================
        # STUDENT
        # ====================================================

        if occupation == "Student":

            education_level = data.get(
                "education_level"
            )

            course = data.get(
                "course"
            )

            year_of_study = data.get(
                "year_of_study"
            )

            institution_type = data.get(
                "institution_type"
            )

            current_scholarship = to_bool(
                data.get("current_scholarship")
            )

            fields = {
                "education_level": education_level,
                "course": course,
                "year_of_study": year_of_study,
                "institution_type": institution_type,
                "current_scholarship": current_scholarship
            }

            for field, value in fields.items():

                if value is None or value == "":
                    return createResult(
                        f"{field} is required"
                    )

        # ====================================================
        # FARMER
        # ====================================================

        elif occupation == "Farmer":

            land_owner = to_bool(
                data.get("land_owner")
            )

            land_holding = data.get(
                "land_holding"
            )

            farming_type = data.get(
                "farming_type"
            )

            irrigation_available = to_bool(
                data.get("irrigation_available")
            )

            agricultural_loan = to_bool(
                data.get("agricultural_loan")
            )

            fields = {
                "land_owner": land_owner,
                "land_holding": land_holding,
                "farming_type": farming_type,
                "irrigation_available": irrigation_available,
                "agricultural_loan": agricultural_loan
            }

            for field, value in fields.items():

                if value is None or value == "":
                    return createResult(
                        f"{field} is required"
                    )

        # ====================================================
        # BUSINESS
        # ====================================================

        elif occupation == "Business Owner / Self-employed":

            business_type = data.get(
                "business_type"
            )

            business_registered = to_bool(
                data.get("business_registered")
            )

            business_age = data.get(
                "business_age"
            )

            business_turnover = data.get(
                "business_turnover"
            )

            business_financial_need = to_bool(
                data.get("business_financial_need")
            )

            fields = {
                "business_type": business_type,
                "business_registered": business_registered,
                "business_age": business_age,
                "business_turnover": business_turnover,
                "business_financial_need": business_financial_need
            }

            for field, value in fields.items():

                if value is None or value == "":
                    return createResult(
                        f"{field} is required"
                    )

        # ====================================================
        # HOMEMAKER
        # ====================================================

        elif occupation == "Homemaker":

            education_level = data.get(
                "education_level"
            )

            skills = data.get(
                "skills"
            )

            home_based_business = to_bool(
                data.get("home_based_business")
            )

            business_interest = to_bool(
                data.get("business_interest")
            )

            fields = {
                "education_level": education_level,
                "skills": skills,
                "home_based_business": home_based_business,
                "business_interest": business_interest
            }

            for field, value in fields.items():

                if value is None or value == "":
                    return createResult(
                        f"{field} is required"
                    )

        elif occupation == "Other":

            pass

        else:

            return createResult(
                "Invalid occupation"
            )

        # ====================================================
        # DATABASE UPDATE
        # ====================================================

        sql = """
            UPDATE users
            SET

                age=%s,
                gender=%s,
                state=%s,
                district=%s,
                marital_status=%s,
                disability_status=%s,
                annual_income=%s,
                is_bpl=%s,
                rural_urban=%s,
                caste_category=%s,
                loan_required=%s,
                house_ownership=%s,
                occupation=%s,

                education_level=%s,
                course=%s,
                year_of_study=%s,
                institution_type=%s,
                current_scholarship=%s,

                land_owner=%s,
                land_holding=%s,
                farming_type=%s,
                irrigation_available=%s,
                agricultural_loan=%s,

                business_type=%s,
                business_registered=%s,
                business_age=%s,
                business_turnover=%s,
                business_financial_need=%s,

                skills=%s,
                home_based_business=%s,
                business_interest=%s,

                profile_completed=TRUE

            WHERE email=%s
        """

        params = (

            age,
            gender,
            state,
            district,
            marital_status,
            disability_status,
            annual_income,
            is_bpl,
            rural_urban,
            caste_category,
            loan_required,
            house_ownership,
            occupation,

            education_level,
            course,
            year_of_study,
            institution_type,
            current_scholarship,

            land_owner,
            land_holding,
            farming_type,
            irrigation_available,
            agricultural_loan,

            business_type,
            business_registered,
            business_age,
            business_turnover,
            business_financial_need,

            skills,
            home_based_business,
            business_interest,

            email
        )

        db.executeQuery(
            sql,
            params
        )

        print("PROFILE COMPLETED SUCCESSFULLY")

        return createResult(
            None,
            "Profile completed successfully"
        )

    except Exception as e:

        print("COMPLETE PROFILE ERROR:", e)

        return createResult(
            "Failed to save questionnaire"
        )


# ============================================================
# PROFILE STATUS
# ============================================================

@usersRouter.route("/profile-status", methods=["GET"])
@jwt_required()
def profile_status():

    try:

        email = get_jwt_identity()

        sql = """
            SELECT profile_completed
            FROM users
            WHERE email=%s
        """

        result = db.executeQuery(
            sql,
            (email,)
        )

        if not result:
            return createResult(
                "User not found"
            )

        return createResult(
            None,
            {
                "profile_completed":
                    bool(result[0]["profile_completed"])
            }
        )

    except Exception as e:

        print("PROFILE STATUS ERROR:", e)

        return createResult(
            "Failed to check profile status"
        )


# ============================================================
# SMART RECOMMENDATIONS
# ============================================================

@usersRouter.route("/recommendations", methods=["GET"])
@jwt_required()
def get_recommendations():

    try:
        email = get_jwt_identity()

        # 1. Load full user profile from DB
        sql = """
            SELECT
                age, gender, state, district, marital_status,
                disability_status, annual_income, is_bpl,
                rural_urban, caste_category, occupation,
                education_level, course, land_owner, land_holding,
                home_based_business, business_interest, skills,
                profile_completed
            FROM users
            WHERE email = %s
        """
        result = db.executeQuery(sql, (email,))

        if not result:
            return createResult("User not found")

        user = result[0]
        user = convert_boolean_fields(user)

        if not user.get("profile_completed"):
            return createResult(
                "Please complete your profile first to get recommendations"
            )

        # 2. Build profile for SmartRecommendation
        profile = {
            "age": user.get("age"),
            "gender": user.get("gender"),
            "state": user.get("state") or "Maharashtra",
            "district": user.get("district"),
            "annual_income": float(user.get("annual_income") or 0),
            "caste_category": user.get("caste_category") or "General",
            "occupation": user.get("occupation"),
            "education_level": user.get("education_level"),
            "course": user.get("course"),
            "disability_status": bool(user.get("disability_status")),
            "is_bpl": bool(user.get("is_bpl")),
            "land_owner": bool(user.get("land_owner")),
            "land_holding": float(user.get("land_holding") or 0),
            "marital_status": user.get("marital_status"),
            "home_based_business": bool(user.get("home_based_business")),
            "business_interest": bool(user.get("business_interest")),
            "skills": user.get("skills"),
        }

        # 3. Call Smart Recommendation Engine
        from services.smart_recommendation import SmartRecommendation
        engine = SmartRecommendation()
        recommendation_result = engine.recommend(profile, top_n=10)

        # 4. Return response
        return createResult(None, {
            "total_schemes": recommendation_result.get("total_schemes"),
            "eligible_count": recommendation_result.get("eligible_count"),
            "needs_verification_count": recommendation_result.get("needs_verification_count"),
            "not_eligible_count": recommendation_result.get("not_eligible_count"),
            "recommendations": recommendation_result.get("recommendations", [])
        })

    except Exception as e:
        print("RECOMMENDATIONS ERROR:", e)
        import traceback
        traceback.print_exc()
        return createResult(f"Failed to generate recommendations: {str(e)}")






    