from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token
import os
from passlib.hash import sha256_crypt

crypto = sha256_crypt

JWT_SECRET = os.getenv("MY_JWT_SECRET")


def enableJWT(app):
    app.config["JWT_SECRET_KEY"] = JWT_SECRET
    jwt = JWTManager(app)

    
    @app.before_request
    def allow_options_requests():
        if request.method == "OPTIONS":
            return '', 200

# ---------------- RESPONSE ----------------
def createResult(error=None, data=None):
    if error:
        return jsonify(status="error", error=error)
    return jsonify(status="success", data=data)