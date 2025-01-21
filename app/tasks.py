# tasks.py
import os
import ffmpeg
from zipfile import ZipFile
from app.celery_utils import make_celery

celery_app = make_celery()

@celery_app.task
def process_video(filename, video_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    try:
        probe = ffmpeg.probe(video_path)
        duration = float(probe['format']['duration'])
        interval = 20

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
            except Exception as e:
                raise RuntimeError(f"Error extracting frame at {time}s: {str(e)}")

        base_name = os.path.splitext(filename)[0]
        zip_filename = f"{base_name}.zip"
        zip_path = os.path.join(output_folder, zip_filename)

        with ZipFile(zip_path, 'w') as zipf:
            for screenshot in screenshots:
                zipf.write(screenshot, os.path.basename(screenshot))

        return zip_path

    except Exception as e:
        raise RuntimeError(f"Error processing video: {str(e)}")
