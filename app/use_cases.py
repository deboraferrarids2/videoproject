import os
import ffmpeg
from zipfile import ZipFile
import logging
import subprocess

logger = logging.getLogger(__name__)


def process_video(filename, video_path, output_folder):
    """
    Processa um vídeo e gera screenshots em intervalos regulares.
    Cria um arquivo ZIP com os screenshots gerados.
    """
    os.makedirs(output_folder, exist_ok=True)

    try:
        # Analisar o vídeo para obter informações
        probe = ffmpeg.probe(video_path)
        duration = float(probe['format']['duration'])
        interval = 20  # Intervalo em segundos

        screenshots = []
        for time in range(0, int(duration), interval):
            output_path = os.path.join(output_folder, f"frame_at_{time}s.jpg")
            try:
                (
                    ffmpeg
                    .input(video_path, ss=time)
                    .output(output_path, vframes=1, format='image2', vcodec='mjpeg')
                    .run(capture_stdout=True, capture_stderr=True)
                )
                screenshots.append(output_path)
                logger.debug(f"Screenshot saved: {output_path}")
            except subprocess.CalledProcessError as e:
                stderr_output = e.stderr.decode()
                logger.error(f"Error extracting frame at {time}s: {stderr_output}")
                raise RuntimeError(f"FFmpeg failed: {stderr_output}")

        # Modificar o nome do arquivo ZIP para usar a extensão .zip
        base_name = os.path.splitext(filename)[0]
        zip_filename = f"{base_name}.zip"
        zip_path = os.path.join(output_folder, zip_filename)

        # Criar o arquivo ZIP com os screenshots
        with ZipFile(zip_path, 'w') as zipf:
            for screenshot in screenshots:
                zipf.write(screenshot, os.path.basename(screenshot))
        logger.debug(f"ZIP file created at: {zip_path}")

        return zip_path

    except Exception as e:
        logger.error(f"Error processing video: {e}")
        raise
