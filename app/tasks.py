import os
import ffmpeg
from zipfile import ZipFile
from app.celery_utils import make_celery
import logging
from app import db, create_app  # Importa a função para criar o app
from app.models import ProcessedVideo
import sys

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery_app = make_celery()

@celery_app.task(bind=True)
def process_video(self, user_id, filename, video_path, output_folder):
    """
    Task para processar um vídeo, extrair frames e gerar um arquivo ZIP.
    """
    logger.info(f"Starting video processing task for: {filename}")
    logger.info(f"Video path: {video_path}")
    logger.info(f"Output folder: {output_folder}")

    # Criação do app para usar o contexto
    app = create_app()
    task_status = "FAILED"  # Status padrão em caso de erro

    try:
        # Garantir que o diretório de saída existe
        os.makedirs(output_folder, exist_ok=True)
        logger.info(f"Output directory verified: {output_folder}")

        # Nome e caminho para o arquivo ZIP
        base_name = os.path.splitext(filename)[0]
        zip_filename = f"{base_name}.zip"
        zip_path = os.path.join(output_folder, zip_filename)

        # Extração de frames e criação do ZIP
        screenshots = []
        interval = 20

        # Probing o vídeo
        probe = ffmpeg.probe(video_path)
        duration = float(probe['format']['duration'])
        logger.info(f"Video duration: {duration} seconds")

        for time in range(0, int(duration), interval):
            frame_name = f"{video_path}_frame_at_{time}s.jpg"
            output_path = os.path.join(output_folder, frame_name)
            logger.info(f"Creating frame at {output_path}")
            try:
                (
                    ffmpeg
                    .input(video_path, ss=time)
                    .output(output_path, vframes=1, format='image2', vcodec='mjpeg')
                    .run(capture_stdout=True, capture_stderr=True)
                )
                screenshots.append(output_path)
            except ffmpeg.Error as e:
                stderr_output = e.stderr.decode() if hasattr(e, 'stderr') else 'No stderr available'
                logger.error(f"Error extracting frame at {time}s: {stderr_output}")
                raise RuntimeError(f"FFmpeg failed: {stderr_output}")

        # Criar o ZIP
        with ZipFile(zip_path, 'w') as zipf:
            for screenshot in screenshots:
                logger.info(f"Adding {screenshot} to ZIP")
                zipf.write(screenshot, os.path.basename(screenshot))

        logger.info(f"ZIP file created successfully at {zip_path}")
        
        # Criar a URL de download
        zip_filename = os.path.basename(zip_path)
        download_url = f"http://localhost:8000/download/{zip_filename}"
        logger.info(f"Download URL generated: {download_url}")

        # Atualizar o banco de dados dentro do contexto da aplicação
        with app.app_context():
            processed_video = ProcessedVideo.query.filter_by(task_id=self.request.id).first()
            if processed_video:
                processed_video.status = 'COMPLETED'
                processed_video.zip_file_url = download_url  # Caminho do arquivo ZIP gerado
                db.session.commit()
                task_status = processed_video.status  # Atualiza o status para retorno
                logger.info("ProcessedVideo updated in the database")
            else:
                logger.error("ProcessedVideo record not found")

    except Exception as e:
        logger.error(f"Error processing video: {e}")
        with app.app_context():
            processed_video = ProcessedVideo.query.filter_by(task_id=self.request.id).first()
            if processed_video:
                processed_video.status = 'FAILED'
                db.session.commit()
                task_status = processed_video.status

    return {"status": task_status}

