from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_cors import CORS

# Initialize Flask app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # Update with your actual database URI
app.config['JWT_SECRET_KEY'] = '1a477dd69ce234ca8cfb0186ff2c86dc6ef195047bf0fd8ed9b86b27b5120bfc'  # Optional: Update with your actual JWT secret key

# Initialize CORS and database
CORS(app)
db = SQLAlchemy(app)

# Define the Admin model
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password, password)

# Create the database tables if they don't exist
with app.app_context():
    db.create_all()

def add_admin(email, password):
    """Add an admin user to the database."""
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_admin = Admin(email=email, password=hashed_password)
    
    try:
        with app.app_context():
            # Check if the admin already exists
            existing_admin = Admin.query.filter_by(email=email).first()
            if existing_admin:
                print(f"Admin with email {email} already exists.")
                return

            db.session.add(new_admin)
            db.session.commit()
            print(f"Admin with email {email} added successfully.")
    except Exception as e:
        with app.app_context():
            db.session.rollback()
        print(f"Error adding admin: {e}")

if __name__ == '__main__':
    # Example usage:
    # Replace these values with the actual email and password you want to use
    email = 'admin3@gmail.com'
    password = 'admin3password'

    add_admin(email, password)
