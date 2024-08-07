import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///foodbridge.db'  # SQLite database URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable track modifications
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mysecret')  # Secret key for JWT
