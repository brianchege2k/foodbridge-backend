from flask import request, jsonify
from app import app, db
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from utils import generate_verification_code
import smtplib
from email.mime.text import MIMEText

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Check if user already exists
    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        return jsonify({"msg": "User already exists"}), 409

    # Create a new user
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

    # Check if user exists and password is correct
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Bad username or password"}), 401

    # Create JWT access token
    access_token = create_access_token(identity={'user_id': user.id, 'username': user.username, 'email': user.email, 'role': user.role})
    return jsonify(access_token=access_token), 200

@app.route('/api/donations', methods=['POST'])
@jwt_required()
def create_donation():
    data = request.get_json()
    user_id = get_jwt_identity()['user_id']
    amount = data.get('amount')

    # Create a new donation
    new_donation = Donation(user_id=user_id, amount=amount)
    db.session.add(new_donation)
    db.session.commit()

    return jsonify({"msg": "Donation made successfully"}), 201

@app.route('/api/donations', methods=['GET'])
@jwt_required()
def get_donations():
    user_id = get_jwt_identity()['user_id']
    donations = Donation.query.filter_by(user_id=user_id).all()

    # Serialize the donations
    donation_list = [{"id": d.id, "amount": d.amount, "created_at": d.created_at} for d in donations]

    return jsonify(donations=donation_list), 200

@app.route('/api/donations/summary', methods=['GET'])
def get_donation_summary():
    total_amount = db.session.query(db.func.sum(Donation.amount)).scalar()
    total_donations = Donation.query.count()

    return jsonify({"total_amount": total_amount, "total_donations": total_donations}), 200

