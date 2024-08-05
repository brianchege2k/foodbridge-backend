from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize the Flask application
app = Flask(__name__)

# Load configuration from config.py
app.config.from_object('config.Config')

# Initialize SQLAlchemy and Flask-Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import models (important for migrations)
from models import User, FoodRequest, Donation, Volunteer, Notification, Event, Inventory, Feedback

if __name__ == '__main__':
    # Run the application in debug mode
    app.run(debug=True)
