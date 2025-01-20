from flask import Blueprint, request, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, db, ProcessedVideo
from app.use_cases import process_video
from app.utils import upload_to_s3
import jwt
import datetime
import logging
import os
import uuid

# Configuração do logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app_routes = Blueprint('app_routes', __name__)

SECRET_KEY = 'your_secret_key_here'
UPLOAD_FOLDER = '/tmp/uploads'
PROCESSED_FOLDER = '/tmp/processed'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app_routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    logger.debug(f"Received registration request with data: {data}")

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        logger.warning("Email or password not provided.")
        return jsonify({'message': 'Email and password are required.'}), 400

    if User.query.filter_by(email=email).first():
        logger.warning("User already exists.")
        return jsonify({'message': 'User already exists.'}), 409

    # Gera o hash da senha usando werkzeug
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
    logger.debug(f"Generated password hash: {hashed_password}")

    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    logger.debug(f"New user created with ID: {new_user.id}")

    # Gera o token JWT
    token = jwt.encode(
            {
                'sub': str(new_user.id),  # Adiciona o campo 'sub' com o identificador do usuário
                'user_id': new_user.id,  # Mantém o 'user_id' caso esteja sendo usado em outro lugar
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            },
            SECRET_KEY,
            algorithm='HS256'
        )
    logger.debug(f"Generated token for new user: {token}")

    return jsonify({'message': 'User registered successfully.', 'token': token}), 201

@app_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    logger.debug(f"Received login request with data: {data}")

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        logger.warning("Email or password not provided.")
        return jsonify({'message': 'Email and password are required.'}), 400

    user = User.query.filter_by(email=email).first()
    logger.debug(f"User found in database: {user}")

    if not user:
        logger.warning("User not found in the database.")
        return jsonify({'message': 'Invalid credentials.'}), 401

    logger.debug(f"Stored password hash (from database): {user.password}")

    try:
        if not check_password_hash(user.password, password):
            logger.warning("Password does not match.")
            return jsonify({'message': 'Invalid credentials.'}), 401
    except Exception as e:
        logger.error(f"Error during password validation: {e}")
        return jsonify({'message': 'An error occurred while validating the password.'}), 500

    # Gera o token JWT
    try:
        token = jwt.encode(
            {
                'sub': str(user.id),  # Adiciona o campo 'sub' com o identificador do usuário
                'user_id': user.id,  # Mantém o 'user_id' caso esteja sendo usado em outro lugar
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            },
            SECRET_KEY,
            algorithm='HS256'
        )

        logger.debug(f"Generated token: {token}")
    except Exception as e:
        logger.error(f"Error generating JWT: {e}")
        return jsonify({'message': 'An error occurred while generating the token.'}), 500

    logger.info("Login successful.")
    return jsonify({'message': 'Login successful.', 'token': token}), 200

@app_routes.route('/upload-video', methods=['POST'])
@jwt_required()
def upload_video():
    user_id = get_jwt_identity()
    logger.debug(f"User ID from JWT: {user_id}")

    file = request.files.get('video')
    if not file:
        logger.warning("No video file provided.")
        return jsonify({'message': 'No video file provided'}), 400

    # Salvar o vídeo no servidor temporariamente
    filename = secure_filename(file.filename)
    video_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename}")
    file.save(video_path)
    logger.debug(f"Video saved at: {video_path}")

    # Processar o vídeo
    try:
        zip_path = process_video(filename, video_path, PROCESSED_FOLDER)
        logger.debug(f"Video processed. ZIP path: {zip_path}")
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        return jsonify({'message': f'Error processing video: {str(e)}'}), 500

    # Salvar informações no banco de dados
    zip_filename = os.path.basename(zip_path)
    download_url = f"http://{request.host}/download/{zip_filename}"
    try:
        new_video = ProcessedVideo(
            user_id=user_id,
            original_video_name=os.path.basename(video_path),
            zip_file_url=download_url
        )
        db.session.add(new_video)
        db.session.commit()
        logger.debug(f"Video metadata saved in database: {new_video}")
    except Exception as e:
        logger.error(f"Error saving video metadata: {e}")
        return jsonify({'message': 'Error saving video metadata'}), 500

    return jsonify({
        'message': 'Video processed successfully.',
        'download_url': download_url
    }), 200


@app_routes.route('/download/<path:filename>', methods=['GET'])
@jwt_required()
def download_file(filename):
    directory = PROCESSED_FOLDER
    try:
        return send_file(
            os.path.join(directory, filename),
            as_attachment=True
        )
    except FileNotFoundError:
        logger.warning(f"File not found: {filename}")
        return jsonify({'message': 'File not found.'}), 404


@app_routes.route('/list-videos', methods=['GET'])
@jwt_required()
def list_videos():
    user_id = get_jwt_identity()
    try:
        videos = ProcessedVideo.query.filter_by(user_id=user_id).all()
        response = [
            {
                'video_name': video.original_video_name,
                'processed_file_url': video.zip_file_url
            }
            for video in videos
        ]
        return jsonify({'videos': response}), 200
    except Exception as e:
        logger.error(f"Error listing videos: {e}")
        return jsonify({'message': f'Error listing videos: {str(e)}'}), 500
