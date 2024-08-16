from app import app, db
from models import Event
from datetime import datetime

# Create a Flask application context
with app.app_context():
    # Convert the date strings to datetime.date objects
    event1 = Event(
        name='Charity Run',
        description='5K run for charity.',
        location='Central Park',
        date=datetime.strptime('2024-09-01', '%Y-%m-%d').date()
    )
    event2 = Event(
        name='Food Drive',
        description='Collecting non-perishable food items.',
        location='Community Center',
        date=datetime.strptime('2024-09-15', '%Y-%m-%d').date()
    )

    # Add them to the session
    db.session.add(event1)
    db.session.add(event2)

    # Commit the session to save the events in the database
    db.session.commit()

    print("Seed data has been added successfully.")