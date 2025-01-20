from app import db
import datetime

class ProcessedVideo(db.Model):
    __tablename__ = 'processed_videos'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), nullable=False)  # Alterado para string simples
    original_video_name = db.Column(db.String(255), nullable=False)
    zip_file_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
