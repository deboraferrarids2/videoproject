import jwt
import datetime
from app.models import db
from user_auth.models import User

def ensure_user_and_generate_token(secret_key, user_email="user@example.com"):
    """
    Garante que exista pelo menos um usuário no banco de dados. Se não houver, cria um.
    Em seguida, gera um token JWT para o usuário especificado.
    """
    from app import create_app
    app = create_app()
    with app.app_context():
        # Verifica se existe pelo menos um usuário
        user = User.query.first()

        if not user:
            # Se não existir usuário, cria um usuário padrão
            user = User(email=user_email, password="password123")
            db.session.add(user)
            db.session.commit()

        # Define o user_id para o token
        user_id = user.id if user.id == 1 else 2

        # Gera o token JWT
        payload = {
            "user_id": user_id,
            "sub": f"user_{user_id}",
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=365 * 100),  # 100 anos
        }
        token = jwt.encode(payload, secret_key, algorithm="HS256")
        return token
