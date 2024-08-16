from flask import Flask, request, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import os
from dotenv import load_dotenv
from models import db, User, Donation,Admin,Event,Feedback

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, methods=["GET", "POST", "PUT", "DELETE"], headers=["Content-Type", "Authorization"])
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

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

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Invalid credentials"}), 401

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
        # Fetch statistics
        total_users = User.query.count()
        total_donations = db.session.query(db.func.sum(Donation.amount)).scalar() or 0
        active_campaigns = Event.query.count()

        # Fetch recent feedback
        recent_feedback = Feedback.query.order_by(Feedback.id.desc()).limit(5).all()
        feedback_list = [feedback.feedback_text for feedback in recent_feedback]

        data = {
            'stats': {
                'users': total_users,
                'donations': total_donations,
                'campaigns': active_campaigns,
            },
            'feedback': feedback_list
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
                
            } for user in users
        ]

        return jsonify(users_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404
        
        db.session.delete(user)
        db.session.commit()

        return jsonify({"msg": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/campaigns', methods=['GET'])
@jwt_required()
def get_campaigns():
    try:
        campaigns = Event.query.all()
        campaigns_list = [
            {
                'id': campaign.id,
                'name': campaign.name,
                'date': campaign.date.strftime('%Y-%m-%d %H:%M:%S'),
                'location': campaign.location,
                'description': campaign.description
            }
            for campaign in campaigns
        ]
        return jsonify(campaigns_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/api/admin/campaigns/<int:campaign_id>', methods=['PUT','GET'])
@jwt_required()
def update_campaign(campaign_id):
    try:
        data = request.json
        campaign = Event.query.get_or_404(campaign_id)

        # Update fields if provided in the request
        campaign.name = data.get('name', campaign.name)
        campaign.date = data.get('date', campaign.date)
        campaign.location = data.get('location', campaign.location)
        campaign.description = data.get('description', campaign.description)

        db.session.commit()

        return jsonify({"message": "Campaign updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/api/admin/campaigns/<int:campaign_id>', methods=['DELETE'])
@jwt_required()
def delete_campaign(campaign_id):
    try:
        campaign = Event.query.get_or_404(campaign_id)
        db.session.delete(campaign)
        db.session.commit()

        return jsonify({"message": "Campaign deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    try:
        user = User.query.filter_by(email=data['email']).first()  # Fetch user based on email
        if not user:
            return jsonify({'message': 'User not found'}), 404

        feedback = Feedback(user_id=user.id, feedback_text=data['message'])
        db.session.add(feedback)
        db.session.commit()

        return jsonify({'message': 'Feedback submitted successfully'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@app.route('/api/donate', methods=['POST'])
@jwt_required()
def donate():
    data = request.get_json()
    user_id = get_jwt_identity()['id']
    amount = data.get('amount')
    message = data.get('message', '')

    if not amount:
        return jsonify({"msg": "Amount is required"}), 400

    try:
        donation = Donation(user_id=user_id, amount=amount, message=message)
        db.session.add(donation)
        db.session.commit()

        return jsonify({"msg": "Donation successful"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/campaigns', methods=['POST'])
@jwt_required()
def add_campaign():
    data = request.get_json()
    try:
        new_campaign = Event(
            name=data.get('name'),
            date=data.get('date'),
            location=data.get('location'),
            description=data.get('description')
        )
        db.session.add(new_campaign)
        db.session.commit()

        return jsonify({"message": "Campaign added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
