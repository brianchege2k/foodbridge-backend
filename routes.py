from flask import Blueprint, request, jsonify
from app import db
from models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    
    if not username or not email or not password or not role:
        return jsonify({'msg': 'Missing fields'}), 400

    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        return jsonify({'msg': 'User already exists'}), 409

    hashed_password = generate_password_hash(password)
    user = User(username=username, email=email, password=hashed_password, role=role)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'msg': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):  
        access_token = create_access_token(identity={'username': user.username, 'role': user.role})
        return jsonify(access_token=access_token), 200
    return jsonify({'msg': 'Invalid credentials'}), 401

@auth_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()
    if user:
        user_data = {
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'created_at': user.created_at,
            'updated_at': user.updated_at
        }
        return jsonify(user_data), 200
    return jsonify({'msg': 'User not found'}), 404
