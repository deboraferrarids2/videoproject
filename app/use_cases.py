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

    try:
        # Call the Celery task instead of the direct function
        task = process_video.delay(filename, video_path, PROCESSED_FOLDER)
        return {'message': 'Video processing started.', 'task_id': task.id}, 202
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
        videos = ProcessedVideo.query.filter_by(user_id=user_id).all()
        response = [
            {
                'video_name': video.original_video_name,
                'processed_file_url': video.zip_file_url
            }
            for video in videos
        ]
        return {'videos': response}, 200
    except Exception as e:
        logger.error(f"Error listing videos: {e}")
        return {'message': f'Error listing videos: {str(e)}'}, 500

# def process_video(filename, video_path, output_folder):
#     os.makedirs(output_folder, exist_ok=True)

#     try:
#         probe = ffmpeg.probe(video_path)
#         duration = float(probe['format']['duration'])
#         interval = 20

#         screenshots = []
#         for time in range(0, int(duration), interval):
#             output_path = os.path.join(output_folder, f"frame_at_{time}s.jpg")
#             try:
#                 (
#                     ffmpeg
#                     .input(video_path, ss=time)
#                     .output(output_path, vframes=1, format='image2', vcodec='mjpeg')
#                     .run(capture_stdout=True, capture_stderr=True)
#                 )
#                 screenshots.append(output_path)
#             except subprocess.CalledProcessError as e:
#                 stderr_output = e.stderr.decode() if hasattr(e, 'stderr') else 'No stderr available'
#                 logger.error(f"Error extracting frame at {time}s: {stderr_output}")
#                 raise RuntimeError(f"FFmpeg failed: {stderr_output}")

#         base_name = os.path.splitext(filename)[0]
#         zip_filename = f"{base_name}.zip"
#         zip_path = os.path.join(output_folder, zip_filename)

#         with ZipFile(zip_path, 'w') as zipf:
#             for screenshot in screenshots:
#                 zipf.write(screenshot, os.path.basename(screenshot))

#         return zip_path

#     except Exception as e:
#         logger.error(f"Error processing video: {e}")
#         raise
