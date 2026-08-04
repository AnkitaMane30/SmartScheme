from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
import mysql.connector

from utils.utils import crypto, createResult
import utils.db_connection as db

usersRouter = Blueprint("users", __name__, url_prefix="/users")


# ================= REGISTER =================
@usersRouter.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return createResult("All fields required")

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all([name, email, password]):
        return createResult("Name, Email and Password required")

    hashed_password = crypto.hash(password)

    sql = """
        INSERT INTO users(name, email, password)
        VALUES(%s, %s, %s)
    """

    try:
        db.executeQuery(sql, (name, email, hashed_password))
        return createResult(None, "User registered successfully")

    except mysql.connector.IntegrityError:
        return createResult("Email already exists")


# ================= LOGIN =================
@usersRouter.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return createResult("Email and Password required")

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return createResult("Email and Password required")

    sql = """
        SELECT email, password
        FROM users
        WHERE email=%s
    """

    result = db.executeQuery(sql, (email,))

    if not result:
        return createResult("Invalid email or password")

    user = result[0]

    if not crypto.verify(password, user["password"]):
        return createResult("Invalid email or password")

    token = create_access_token(identity=user["email"])

    return createResult(None, {
        "email": user["email"],
        "token": token
    })


# ================= PROFILE =================
@usersRouter.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():

    email = get_jwt_identity()

    sql = """
        SELECT
            name,
            email
        FROM users
        WHERE email=%s
    """

    result = db.executeQuery(sql, (email,))

    if not result:
        return createResult("User not found")

    return createResult(None, result[0])