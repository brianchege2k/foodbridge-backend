from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from config import Config
from models import db, User, Donation, Volunteer, Notification, Event, Inventory, Feedback
from utils import generate_verification_code, send_verification_email
import bcrypt

app = Flask(__name__)  # Create Flask app
app.config.from_object(Config)  # Load configuration

db.init_app(app)  # Initialize SQLAlchemy
migrate = Migrate(app, db) 
mail = Mail(app)  # Initialize Flask-Mail
jwt = JWTManager(app)  # Initialize Flask-JWT-Extended

@app.route('/register', methods=['POST'])
def register():
    """Register a new user and send a verification email."""
    data = request.get_json()  # Get JSON data from the request
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:  # Check for missing fields
        return jsonify({'error': 'Username, email, and password are required.'}), 400

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Create a new user instance
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)  # Add the new user to the session
    db.session.commit()  # Commit the session to the database

    # Generate and send verification code
    verification_code = generate_verification_code()
    send_verification_email(email, verification_code)  # Send email

    return jsonify({'message': 'User registered successfully. Please check your email for verification.'}), 201

@app.route('/login', methods=['POST'])
def login():
    """Log in a user and return a JWT token."""
    data = request.get_json()  # Get JSON data from the request
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()  # Find user by email
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):  # Check password
        return jsonify({'error': 'Invalid email or password.'}), 401

    # Create a JWT token
    token = create_access_token(identity=user.id)  # Replace with actual user ID
    return jsonify({'token': token}), 200

@app.route('/donate', methods=['POST'])
@jwt_required()  # Protect this route
def donate():
    """Create a new donation record."""
    data = request.get_json()  # Get JSON data from the request
    user_id = get_jwt_identity()  # Get user ID from the JWT token
    amount = data.get('amount')
    message = data.get('message')

    if not amount:  # Check for missing fields
        return jsonify({'error': 'Amount is required.'}), 400

    # Create a new donation instance
    new_donation = Donation(user_id=user_id, amount=amount, message=message)
    db.session.add(new_donation)  # Add to the session
    db.session.commit()  # Commit the session

    return jsonify({'message': 'Donation recorded successfully.'}), 201

@app.route('/volunteer', methods=['POST'])
@jwt_required()  # Protect this route
def volunteer():
    """Register a user as a volunteer for an event."""
    data = request.get_json()  # Get JSON data from the request
    user_id = get_jwt_identity()  # Get user ID from the JWT token
    event_id = data.get('event_id')

    if not event_id:  # Check for missing fields
        return jsonify({'error': 'Event ID is required.'}), 400

    # Create a new volunteer instance
    new_volunteer = Volunteer(user_id=user_id, event_id=event_id)
    db.session.add(new_volunteer)  # Add to the session
    db.session.commit()  # Commit the session

    return jsonify({'message': 'Volunteer registration successful.'}), 201

@app.route('/notifications', methods=['GET'])
@jwt_required()  # Protect this route
def get_notifications():
    """Get all notifications for a user."""
    user_id = get_jwt_identity()  # Get user ID from the JWT token

    notifications = Notification.query.filter_by(user_id=user_id).all()  # Query notifications
    result = [{'id': n.id, 'message': n.message, 'is_read': n.is_read} for n in notifications]  # Prepare result

    return jsonify(result), 200  # Return notifications

@app.route('/events', methods=['POST'])
@jwt_required()  # Protect this route
def create_event():
    """Create a new event."""
    data = request.get_json()  # Get JSON data from the request
    name = data.get('name')
    description = data.get('description')
    location = data.get('location')
    date = data.get('date')

    if not name or not location or not date:  # Check for missing fields
        return jsonify({'error': 'Name, location, and date are required.'}), 400

    # Create a new event instance
    new_event = Event(name=name, description=description, location=location, date=date)
    db.session.add(new_event)  # Add to the session
    db.session.commit()  # Commit the session

    return jsonify({'message': 'Event created successfully.'}), 201

@app.route('/inventory', methods=['POST'])
@jwt_required()  # Protect this route
def add_inventory_item():
    """Add a new item to the inventory."""
    data = request.get_json()  # Get JSON data from the request
    name = data.get('name')
    quantity = data.get('quantity')
    expiry_date = data.get('expiry_date')

    if not name or not quantity:  # Check for missing fields
        return jsonify({'error': 'Name and quantity are required.'}), 400

    # Create a new inventory item
    new_item = Inventory(name=name, quantity=quantity, expiry_date=expiry_date)
    db.session.add(new_item)  # Add to the session
    db.session.commit()  # Commit the session

    return jsonify({'message': 'Inventory item added successfully.'}), 201

@app.route('/feedback', methods=['POST'])
@jwt_required()  # Protect this route
def submit_feedback():
    """Submit user feedback."""
    data = request.get_json()  # Get JSON data from the request
    user_id = get_jwt_identity()  # Get user ID from the JWT token
    message = data.get('message')

    if not message:  # Check for missing fields
        return jsonify({'error': 'Message is required.'}), 400

    # Create a new feedback instance
    new_feedback = Feedback(user_id=user_id, message=message)
    db.session.add(new_feedback)  # Add to the session
    db.session.commit()  # Commit the session

    return jsonify({'message': 'Feedback submitted successfully.'}), 201

@app.route('/notifications/<int:user_id>', methods=['PUT'])
def mark_notifications_as_read(user_id):
    """Mark all notifications for a user as read."""
    notifications = Notification.query.filter_by(user_id=user_id, is_read=False).all()  # Query unread notifications
    for notification in notifications:
        notification.is_read = True  # Mark as read

    db.session.commit()  # Commit the session

    return jsonify({'message': 'All notifications marked as read.'}), 200

if __name__ == '__main__':
    app.run(debug=True)  # Run the app
