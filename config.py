import os

class Config:
    # Basic configuration settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_super_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///foodbridge.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
