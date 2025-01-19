import logging
from flask import Flask
from .models import db, connect_db, bcrypt
from .config import Config, Testing
from .routes.users import users_bp as users
from .routes.books import books_bp as books
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import os

# Load environment variables from .env file
load_dotenv()

jwt = JWTManager()

# Global logging setup
logging.basicConfig(
    level=logging.DEBUG,  # Use DEBUG for development, change to INFO for production
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),  # Logs to console
        logging.FileHandler("app.log"),  # Saves logs to a file
    ],
)
logger = logging.getLogger(__name__)  # Creates a logger for this module

def create_app(config_name="Config"):
    """Flask Application factory function: Creates flask app context, initializes
    extensions using the app instance, registers blueprints, and returns the app"""
    
    logger.info("Initializing Flask app...")  # Example log message
    
    app = Flask(__name__)
    
    # Sets the configuration class based on the 'config_name' argument
    if config_name == 'Config':
        app.config.from_object(Config)
        logger.debug("Loaded Config class.")
    elif config_name == 'Testing':
        app.config.from_object(Testing)
        logger.debug("Loaded Testing class.")
    else:
        logger.error(f"Invalid configuration name: {config_name}")
        raise ValueError("Invalid configuration name")
    
    # Initialize Sentry inside the app context
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN", ""),
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        _experiments={
            "continuous_profiling_auto_start": True,
        },
    )
    logger.info("Sentry initialized.")

    connect_db(app)
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate = Migrate(app, db)
    CORS(app)
    logger.info("Extensions initialized.")

    # Register blueprints with URL prefixes
    app.register_blueprint(users, url_prefix='/api/users')
    app.register_blueprint(books, url_prefix='/api/books')
    logger.debug("Blueprints registered.")

    # Simple route for index page
    @app.route("/")
    def index():
        logger.info("Index route accessed.")
        return "NextRead-v2 backend running...."

    logger.info("Flask app creation complete.")
    return app
