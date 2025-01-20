from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.use_cases import (
    handle_register,
    handle_login,
    handle_upload_video,
    handle_download_file,
    handle_list_videos
)
import logging

# Configuração do logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app_routes = Blueprint('app_routes', __name__)

@app_routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    return handle_register(data)

@app_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    return handle_login(data)

@app_routes.route('/upload-video', methods=['POST'])
@jwt_required()
def upload_video():
    user_id = get_jwt_identity()
    file = request.files.get('video')
    if not file:
        return jsonify({'message': 'No video file provided'}), 400

    return handle_upload_video(user_id, file)

@app_routes.route('/download/<path:filename>', methods=['GET'])
@jwt_required()
def download_file(filename):
    return handle_download_file(filename)

@app_routes.route('/list-videos', methods=['GET'])
@jwt_required()
def list_videos():
    user_id = get_jwt_identity()
    return handle_list_videos(user_id)