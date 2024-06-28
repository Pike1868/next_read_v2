import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('SECRET_KEY')
    UPLOAD_FOLDER = 'app/static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

class Testing(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URI')
