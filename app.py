from flask import Flask, request, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import os
from dotenv import load_dotenv
from datetime import datetime
import stripe


# Import your models here
from models import db, User, Donation, Admin, Event, Feedback, Member ,Reply

load_dotenv()

app = Flask(__name__)
CORS(
    app,
    resources={r"/api/*": {"origins": "http://localhost:3000"}}, 
    methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
    headers=["Content-Type", "Authorization"],
    supports_credentials=True
)



app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///app.db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')

db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)
jwt = JWTManager(app)


@app.route('/')
def index():
    return "Welcome to the FoodBridge API!"

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({"msg": "Missing fields"}), 400

        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            return jsonify({"msg": "User already exists"}), 409

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"msg": "User registered successfully"}), 201

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"msg": "Internal Server Error"}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Retrieve the user by email
    user = User.query.filter_by(email=email).first()

    # Check if the user exists and the password is correct
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Invalid credentials"}), 401

    # Check if the user account is active
    if not user.isActive:
        return jsonify({"msg": "Account is deactivated"}), 403

    # Generate access token
    access_token = create_access_token(identity={'id': user.id, 'email': user.email})
    return jsonify({"msg": "Login successful", "access_token": access_token}), 200

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Authenticate the admin
    admin = Admin.query.filter_by(email=email).first()

    if not admin or not admin.check_password(password):
        return jsonify({"msg": "Invalid credentials"}), 401

    access_token = create_access_token(identity={'email': admin.email})
    return jsonify({"access_token": access_token}), 200

@app.route('/api/admin/stats', methods=['GET'])
@jwt_required()
def get_admin_stats():
    try:
        total_users = User.query.count()
        total_donations = db.session.query(db.func.sum(Donation.amount)).scalar() or 0
        active_campaigns = Event.query.count()
        total_members = Member.query.count()  # Add this line to count the members

        data = {
            'stats': {
                'users': total_users,
                'donations': total_donations,
                'campaigns': active_campaigns,
                'members': total_members,  # Include the members count
            }
        }

        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    try:
        # Fetch all users
        users = User.query.all()
        users_list = [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'isActive': user.isActive  # Include activation status
            } for user in users
        ]

        return jsonify(users_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/admin/users/<int:user_id>/status', methods=['PUT'])
@jwt_required()
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.isActive = data.get('isActive')
    db.session.commit()
    return jsonify({'message': 'User status updated successfully'})    

@app.route('/api/admin/events', methods=['GET'])
@jwt_required()
def get_events():
    try:
        events = Event.query.all()
        return jsonify([event.serialize() for event in events]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/events/incomplete', methods=['GET'])
def get_incomplete_events():
    events = Event.query.filter_by(completed=False).all()
    return jsonify([event.serialize() for event in events])   

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    try:
        # Fetch user based on email
        user = User.query.filter_by(email=data.get('email')).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Create feedback
        feedback = Feedback(user_id=user.id, message=data.get('message'))
        db.session.add(feedback)
        db.session.commit()

        return jsonify({'message': 'Feedback submitted successfully'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/admin/events', methods=['POST'])
@jwt_required()
def add_event():
    data = request.get_json()
    try:
        # Convert date string to datetime object
        event_date = datetime.strptime(data.get('date'), '%Y-%m-%d')

        # Convert the datetime object back to a string for storage
        event_date_str = event_date.strftime('%Y-%m-%d')

        new_event = Event(
            name=data.get('name'),
            date=event_date_str,  # Store the date as a string
            location=data.get('location'),
            description=data.get('description'),
            picture_url=data.get('pictureUrl')  # Ensure this key matches the request body
        )
        db.session.add(new_event)
        db.session.commit()

        return jsonify({"message": "Event added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/events/<int:id>/complete', methods=['PATCH'])
@jwt_required()
def complete_event(id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Authorization token missing"}), 401

    event = Event.query.get(id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    try:
        # Set completed to True
        event.completed = True
        db.session.commit()
        return jsonify(event.serialize()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# Endpoint to add a new member
@app.route('/api/admin/members', methods=['POST'])
@jwt_required()
def add_member():
    data = request.get_json()
    print(data)  # Log the received data to verify it's correct
    
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if 'name' not in data or 'position' not in data:
        return jsonify({"error": "Missing required fields: 'name' and 'position' are required."}), 400

    try:
        new_member = Member(
            name=data.get('name'),
            position=data.get('position'),
            image_url=data.get('image_url')  # Ensure this field matches the frontend key
        )
        db.session.add(new_member)
        db.session.commit()

        return jsonify({"message": "Member added successfully", "member": {
            'id': new_member.id,
            'name': new_member.name,
            'position': new_member.position,
            'image_url': new_member.image_url
        }}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Endpoint to fetch all members
@app.route('/api/members', methods=['GET'])
def get_members():
    try:
        members = Member.query.all()
        members_list = [
            {
                'id': member.id,
                'name': member.name,
                'position': member.position,
                'image_url': member.image_url
            } for member in members
        ]
        return jsonify(members_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to delete a member
@app.route('/api/admin/members/<int:member_id>', methods=['DELETE'])
@jwt_required()
def delete_member(member_id):
    try:
        member = Member.query.get_or_404(member_id)
        db.session.delete(member)
        db.session.commit()

        return jsonify({"message": "Member deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/api/admin/feedback', methods=['GET'])
@jwt_required()
def get_feedback():
    try:
        feedback_records = Feedback.query.all()
        feedback_list = []

        for feedback in feedback_records:
            user = User.query.get(feedback.user_id)  # Get the user associated with the feedback
            if user:
                feedback_list.append({
                    'id': feedback.id,                # Include the feedback id
                    'userId': user.id,
                    'username': user.username,
                    'email': user.email,
                    'message': feedback.message       # Ensure attribute name is correct
                })
            else:
                feedback_list.append({
                    'id': feedback.id,                # Include the feedback id
                    'userId': feedback.user_id,
                    'username': 'Unknown',            # Default value if user not found
                    'email': 'Unknown',
                    'message': feedback.message
                })

        return jsonify({'feedback': feedback_list}), 200
    except Exception as e:
        print(f"Error: {str(e)}")  # Print the error for debugging
        return jsonify({"error": str(e)}), 500


@app.route('/api/admin/feedback/reply', methods=['POST'])
@jwt_required()
def post_reply():
    try:
        data = request.get_json()
        user_id = data.get('userId')
        user_email = data.get('userEmail')
        feedback_id = data.get('feedbackId')
        reply_message = data.get('reply')

        if not user_id or not user_email or not feedback_id or not reply_message:
            return jsonify({"error": "Missing required fields"}), 400

        new_reply = Reply(
            user_id=user_id,
            feedback_id=feedback_id,
            message=reply_message
        )
        db.session.add(new_reply)
        db.session.commit()

        return jsonify({'reply': {'userId': user_id, 'feedbackId': feedback_id, 'message': reply_message}}), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/create-payment-intent', methods=['POST'])
def create_payment_intent():
    data = request.json
    amount = data['amount']

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount) * 100,  # amount in cents
            currency='usd'
        )
        return jsonify(clientSecret=intent['client_secret'])
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/api/save-donation', methods=['POST'])
def save_donation():
    data = request.json

    # Validate required fields
    if 'amount' not in data or not isinstance(data['amount'], (int, float)):
        return jsonify({"error": "Invalid amount. It should be a number."}), 422

    if 'paymentIntentId' not in data or not isinstance(data['paymentIntentId'], str):
        return jsonify({"error": "Invalid payment intent ID. It should be a string."}), 422

    if 'email' not in data or not isinstance(data['email'], str):
        return jsonify({"error": "Invalid email. It should be a string."}), 422

    # Extract email and find the user
    email = data['email']
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "User with the provided email not found."}), 404

    # Assuming message is optional
    amount = int(float(data['amount']))  # Convert the amount to an integer (cents)
    message = data.get('message', '')
    payment_intent_id = data['paymentIntentId']
    user_id = user.id

    # Save the donation to the database
    donation = Donation(amount=amount, message=message, payment_intent_id=payment_intent_id, user_id=user_id)
    db.session.add(donation)
    db.session.commit()

    return jsonify({"msg": "Donation saved successfully."}), 200

@app.route('/api/check-email', methods=['POST'])
def check_email():
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if user:
        return jsonify({"exists": True}), 200
    else:
        return jsonify({"exists": False}), 200      