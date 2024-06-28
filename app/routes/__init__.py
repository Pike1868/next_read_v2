from flask import Flask
from .models import db, connect_db, bcrypt
from .config import Config, Testing
from .routes.users import users_bp as users
from .routes.books import books_bp as books
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os


# Loads environment variables from .env file
load_dotenv()

jwt = JWTManager()

def create_app(config_name="Config"):
    """Flask Application factory function: Creates flask app context, initializes
    extensions using the app instance, registers blueprints, and returns the app"""
    
    app = Flask(__name__)
    
    #Dynamically select the configuration class based on the ''config_name' argument
    if config_name == 'Config':
        app.config.from_object(Config)
    elif config_name == 'Testing':
        app.config.from_object(Testing)
    else:
        raise ValueError("Invalid configuration name")
    
    connect_db(app)
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    migrate = Migrate(app.db)
    
    app.register_blueprint(users)
    app.register_blueprint(books)
    
    return app