from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.cli import register_commands
from app.exceptions.handler import register_error_handlers
from app.extension import db, limiter, ma, migrate
from config.cors import CORS_CONFIG
from config.database import DatabaseConfig
from config.jwt import JWTConfig
from config.logging import setup_logging

app = Flask(__name__)

# ///// implement log ///////////////
setup_logging(app)
register_commands(app)

# ///// implement cors /////////////////
CORS(app, **CORS_CONFIG)

# ///// setup database and jwt ///////////////////
app.config.from_object(DatabaseConfig)
app.config.from_object(JWTConfig)

# /////// Initialize extensions ////////////
db.init_app(app)
migrate.init_app(app, db)
limiter.init_app(app)
ma.init_app(app)

# JWT
jwt = JWTManager(app)

# ///////////////// implement web /////////
import route.api as routes


@app.route("/")
def initialRoute():
    return "<h1 style='text-align: center; margin-top:250px; font-size: 60px;'>Hello World</p>"


# /////// implement models ////////////////
from app.models import *

# register all Blueprint Route
for bp_name in getattr(routes, "__all__", []):
    bp = getattr(routes, bp_name)
    app.register_blueprint(bp)

# //////// register error handler /////////
register_error_handlers(app)

# //////// run application ////////////////
if __name__ == "__main__":
    app.run(debug=True)
