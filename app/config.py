import os

class Config:
    # Configurações básicas
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key_here')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data.db')
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET', 'video-processor')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ['true', '1']

    # Configurações para JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_secret_key_here')  # Chave secreta para JWT
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # Tempo de expiração do token (em segundos)
    JWT_TOKEN_LOCATION = ["headers"]  # Define onde o token JWT será enviado (padrão: cabeçalhos)

    # Configurações para senha criptografada
    BCRYPT_LOG_ROUNDS = int(os.getenv('BCRYPT_LOG_ROUNDS', 12))  # Custo para gerar os hashes da senha

