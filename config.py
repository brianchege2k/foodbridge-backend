import os

class Config:
    # Base configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_super_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///foodbridge.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/your_database'

class DevelopmentConfig(Config):
    # Development-specific configuration
    DEBUG = True

# Default configuration
app_config = {
    'development': DevelopmentConfig,
}
