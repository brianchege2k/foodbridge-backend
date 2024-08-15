# insert_dummy_data.py

from app import app, db
from models import Event
from datetime import datetime
from sqlalchemy.sql import text

def insert_dummy_data():
    with app.app_context():
        # Clear existing data
        db.session.execute(text('DELETE FROM event;'))
        db.session.commit()

        # Create dummy events
        events = [
            Event(
                name="Community Food Drive",
                date=datetime(2024, 9, 15, 10, 0, 0),
                location="City Hall",
                description="A community food drive to support local families in need."
            ),
            Event(
                name="Charity Gala",
                date=datetime(2024, 10, 22, 19, 0, 0),
                location="Grand Ballroom, Hotel Lux",
                description="An elegant gala to raise funds for charity."
            ),
            Event(
                name="Health and Wellness Fair",
                date=datetime(2024, 11, 5, 9, 0, 0),
                location="Community Center",
                description="A fair promoting health and wellness with various activities and stalls."
            ),
            Event(
                name="Holiday Toy Drive",
                date=datetime(2024, 12, 10, 14, 0, 0),
                location="Main Street Park",
                description="A toy drive to collect gifts for children during the holiday season."
            )
        ]

        # Add dummy data to the database
        db.session.add_all(events)
        db.session.commit()
        print("Dummy data inserted successfully!")

if __name__ == '__main__':
    insert_dummy_data()
