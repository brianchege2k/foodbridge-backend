from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Donation
from . import db

auth_bp = Blueprint('auth', __name__)
donation_bp = Blueprint('donation', __name__)

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        return jsonify({"msg": "User already exists"}), 409

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully"}), 201

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity={'user_id': user.id})
    return jsonify(access_token=access_token), 200

@donation_bp.route('/api/donations', methods=['POST'])
@jwt_required()
def create_donation():
    data = request.get_json()
    user_id = get_jwt_identity()['user_id']
    amount = data.get('amount')

    new_donation = Donation(user_id=user_id, amount=amount)
    db.session.add(new_donation)
    db.session.commit()

    return jsonify({"msg": "Donation made successfully"}), 201

@donation_bp.route('/api/donations', methods=['GET'])
@jwt_required()
def get_donations():
    user_id = get_jwt_identity()['user_id']
    donations = Donation.query.filter_by(user_id=user_id).all()
    donation_list = [{"id": d.id, "amount": d.amount} for d in donations]
    return jsonify(donations=donation_list), 200
