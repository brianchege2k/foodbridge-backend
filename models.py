from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    isActive = db.Column(db.Boolean, default=True)  # Added field for activation status
    donations = db.relationship('Donation', backref='donor', lazy=True)
    feedbacks_given = db.relationship('Feedback', backref='author', lazy=True)
    volunteers = db.relationship('Volunteer', backref='participant', lazy=True)
    replies = db.relationship('Reply', backref='user_replies', lazy=True)


class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(255), nullable=True)
    payment_intent_id = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_user_donation'), nullable=False)

    def _init_(self, amount, message, payment_intent_id, user_id):
        self.amount = amount
        self.message = message
        self.payment_intent_id = payment_intent_id
        self.user_id = user_id

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # Changed from db.Date to db.String
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    picture_url = db.Column(db.String(200), nullable=True)
    completed = db.Column(db.Boolean, default=False)
    volunteers = db.relationship('Volunteer', back_populates='event')

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'date': self.date,  # No need to format date here, it's already a string
            'location': self.location,
            'description': self.description,
            'picture_url': self.picture_url,
            'completed': self.completed
        }

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='feedbacks_given')
    replies = db.relationship('Reply', back_populates='feedback')

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user = db.relationship('User', back_populates='volunteers')
    event = db.relationship('Event', back_populates='volunteers')

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    user = db.relationship('User', back_populates='replies')
    feedback = db.relationship('Feedback', back_populates='replies')
