from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()  # Initialize SQLAlchemy

class User(db.Model):
    """Model for user accounts."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    username = db.Column(db.String(80), unique=True, nullable=False)  # Username
    email = db.Column(db.String(120), unique=True, nullable=False)  # User's email
    password = db.Column(db.String(255), nullable=False)  # Hashed password
    role = db.Column(db.String(20), default='user')  # User role (e.g., admin, volunteer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Creation timestamp
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Update timestamp

    donations = db.relationship('Donation', backref='user', lazy=True)  # Relationship with donations
    volunteers = db.relationship('Volunteer', backref='user', lazy=True)  # Relationship with volunteers
    notifications = db.relationship('Notification', backref='user', lazy=True)  # Relationship with notifications
    feedbacks = db.relationship('Feedback', backref='user', lazy=True)  # Relationship with feedback

class Donation(db.Model):
    """Model for donations made by users."""
    __tablename__ = 'donations'

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # User who made the donation
    amount = db.Column(db.Numeric, nullable=False)  # Donation amount
    message = db.Column(db.Text)  # Optional message
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Creation timestamp
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Update timestamp

class Volunteer(db.Model):
    """Model for volunteer registrations."""
    __tablename__ = 'volunteers'

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # User who volunteered
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)  # Event ID they volunteered for
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Creation timestamp
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Update timestamp

class Notification(db.Model):
    """Model for notifications sent to users."""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # User ID receiving the notification
    message = db.Column(db.Text, nullable=False)  # Notification message
    is_read = db.Column(db.Boolean, default=False)  # Read status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Creation timestamp
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Update timestamp

class Event(db.Model):
    """Model for events."""
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    name = db.Column(db.String(120), nullable=False)  # Event name
    description = db.Column(db.Text)  # Event description
    location = db.Column(db.String(255), nullable=False)  # Event location
    date = db.Column(db.DateTime, nullable=False)  # Event date and time
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Creation timestamp
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Update timestamp

class Inventory(db.Model):
    """Model for food inventory items."""
    __tablename__ = 'inventory'

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    name = db.Column(db.String(120), nullable=False)  # Item name
    quantity = db.Column(db.Integer, nullable=False)  # Quantity of the item
    expiry_date = db.Column(db.DateTime)  # Expiry date of the item
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Creation timestamp
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Update timestamp

class Feedback(db.Model):
    """Model for user feedback."""
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # User who submitted the feedback
    message = db.Column(db.Text, nullable=False)  # Feedback message
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Creation timestamp
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Update timestamp

class MpesaTransaction(db.Model):
    __tablename__ = 'mpesa_transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    transaction_id = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
