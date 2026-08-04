from flask import Flask
from flask_cors import CORS
from utils.utils import enableJWT
from routes.users import usersRouter
from routes.schemes import schemesRouter

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "mysecretkey"

CORS(app, supports_credentials=True)

enableJWT(app)

app.register_blueprint(usersRouter)
app.register_blueprint(schemesRouter)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)