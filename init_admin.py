from app import app, db
from models import Admin
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        # Check if the admin already exists
        if Admin.query.filter_by(email='admin@example.com').first():
            print("Admin already exists.")
            return
        
        # Create a new admin
        hashed_password = generate_password_hash('adminpassword')
        new_admin = Admin(email='admin@example.com', password=hashed_password)
        
        # Add and commit to the database
        db.session.add(new_admin)
        db.session.commit()
        print("Admin created successfully.")

if __name__ == '__main__':
    create_admin()
