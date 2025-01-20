import os
import logging
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from user_auth.models import User
from app.models import db

logger = logging.getLogger(__name__)

SECRET_KEY = 'your_secret_key_here'
UPLOAD_FOLDER = '/tmp/uploads'
PROCESSED_FOLDER = '/tmp/processed'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def handle_register(data):
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return {'message': 'Email and password are required.'}, 400

    if User.query.filter_by(email=email).first():
        return {'message': 'User already exists.'}, 409

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    token = jwt.encode(
        {
            'sub': str(new_user.id),
            'user_id': new_user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        },
        SECRET_KEY,
        algorithm='HS256'
    )

    return {'message': 'User registered successfully.', 'token': token}, 201

def handle_login(data):
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return {'message': 'Email and password are required.'}, 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return {'message': 'Invalid credentials.'}, 401

    token = jwt.encode(
        {
            'sub': str(user.id),
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        },
        SECRET_KEY,
        algorithm='HS256'
    )

    return {'message': 'Login successful.', 'token': token}, 200

