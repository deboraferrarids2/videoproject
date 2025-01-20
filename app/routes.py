from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.use_cases import (
    handle_upload_video,
    handle_download_file,
    handle_list_videos
)
import logging

# Configuração do logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app_routes = Blueprint('app_routes', __name__)


@app_routes.route('/upload-video', methods=['POST'])
@jwt_required()
def upload_video():
    token = request.headers.get("Authorization").replace("Bearer ", "")
    file = request.files.get("video")
    if not file:
        return jsonify({'message': 'No video file provided'}), 400

    return handle_upload_video(token, file)

@app_routes.route('/download/<path:filename>', methods=['GET'])
@jwt_required()
def download_file(filename):
    token = request.headers.get("Authorization").replace("Bearer ", "")
    return handle_download_file(token, filename)

@app_routes.route('/list-videos', methods=['GET'])
@jwt_required()
def list_videos():
    token = request.headers.get("Authorization").replace("Bearer ", "")
    return handle_list_videos(token)