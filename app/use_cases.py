import os
import ffmpeg
from zipfile import ZipFile
import logging
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import jsonify, send_file
import uuid
import subprocess
from app.models import db, ProcessedVideo
from app.utils import upload_to_s3
from user_auth.use_cases import validate_user_token
from app.tasks import process_video
from sqlalchemy import desc

logger = logging.getLogger(__name__)

SECRET_KEY = 'your_secret_key_here'
UPLOAD_FOLDER = '/tmp/uploads'
PROCESSED_FOLDER = '/tmp/processed'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def handle_upload_video(token, file):
    try:
        # Valida o token e obtém o user_id
        user_id = validate_user_token(token)
    except ValueError as e:
        return {"message": str(e)}, 401

    filename = secure_filename(file.filename)
    video_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename}")
    file.save(video_path)

    # Criação inicial do registro ProcessedVideo
    new_video = ProcessedVideo(
        user_id=user_id,
        original_video_name=filename,
        task_id=None,  # Será preenchido após a criação da task
        status="PENDING",
        zip_file_url=None
    )
    db.session.add(new_video)
    db.session.commit()

    try:
        # Chamar a task do Celery
        task = process_video.delay(user_id, filename, video_path, PROCESSED_FOLDER)

        # Atualizar o task_id no registro ProcessedVideo
        new_video.task_id = task.id
        db.session.commit()

        return {
            'message': 'Video processing started.',
            'task_id': task.id,
            'processed_video_id': new_video.id
        }, 202
    except Exception as e:
        logger.error(f"Error queuing video processing: {e}")
        return {'message': f'Error queuing video processing: {str(e)}'}, 500


def handle_download_file(token, filename):
    try:
        # Valida o token e obtém o user_id
        validate_user_token(token)
    except ValueError as e:
        return {"message": str(e)}, 401
        
    try:
        file_path = os.path.join(PROCESSED_FOLDER, filename)
        return send_file(file_path, as_attachment=True)
    except FileNotFoundError:
        return {'message': 'File not found.'}, 404
    
def handle_list_videos(token):
    try:
        # Valida o token e obtém o user_id
        user_id = validate_user_token(token)
    except ValueError as e:
        return {"message": str(e)}, 401
    try:
        videos = ProcessedVideo.query.filter_by(user_id=user_id).order_by(desc(ProcessedVideo.created_at)).all()
        response = [
            {
                'video_id': video.id,
                'video_name': video.original_video_name,
                'processed_file_url': video.zip_file_url,
                'task_id': video.task_id,
                "status": video.status
            }
            for video in videos
        ]
        return {'videos': response}, 200
    except Exception as e:
        logger.error(f"Error listing videos: {e}")
        return {'message': f'Error listing videos: {str(e)}'}, 500

def handle_get_video(token, pk):
    try:
        # Valida o token e obtém o user_id
        user_id = validate_user_token(token)
    except ValueError as e:
        return {"message": str(e)}, 401
    try:
        video = ProcessedVideo.query.filter_by(user_id=user_id, id=pk).first()
        response ={
                'video_id': video.id,
                'video_name': video.original_video_name,
                'processed_file_url': video.zip_file_url,
                'task_id': video.task_id,
                "status": video.status
        }
        return {'videos': response}, 200
    except Exception as e:
        logger.error(f"Error listing videos: {e}")
        return {'message': f'Error listing videos: {str(e)}'}, 500