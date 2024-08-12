import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///app.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwtsecretkey')

    # Mpesa API credentials 
    MPESA_CONSUMER_KEY = 'your_mpesa_consumer_key'
    MPESA_CONSUMER_SECRET = 'your_mpesa_consumer_secret'
    MPESA_SHORTCODE = 'your_mpesa_shortcode'
    MPESA_PASSKEY = 'your_mpesa_passkey'
    MPESA_ENV = 'sandbox'  # or 'production'
    MPESA_BASE_URL = 'https://sandbox.safaricom.co.ke' if MPESA_ENV == 'sandbox' else 'https://api.safaricom.co.ke'

