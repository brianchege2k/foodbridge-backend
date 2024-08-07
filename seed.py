# to seed my database with the initial data
from app import db
from models import User, Donation, Volunteer, Notification, Event, Inventory, Feedback

def seed_db():
    """Seed the database with initial data."""
    # Add your seed data here
    user = User(username='admin', email='admin@example.com', password='admin')  # Password hashing should be implemented here
    db.session.add(user)
    db.session.commit()
    print('Database seeded!')

if __name__ == '__main__':
    db.create_all()  # Create all tables
    seed_db()  # Seed the database
