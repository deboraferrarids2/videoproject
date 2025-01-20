import boto3
from botocore.exceptions import NoCredentialsError

S3_BUCKET = 'your-s3-bucket-name'

def upload_to_s3(file_path, s3_key):
    """
    Faz upload de um arquivo para o S3.
    """
    s3 = boto3.client('s3')

    try:
        s3.upload_file(file_path, S3_BUCKET, s3_key)
        s3_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{s3_key}"
        return s3_url
    except FileNotFoundError:
        raise Exception("File not found.")
    except NoCredentialsError:
        raise Exception("Credentials not available.")
