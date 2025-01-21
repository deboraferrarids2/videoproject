from unittest.mock import patch
import pytest
from app import create_app, db

@pytest.fixture
def app():
    test_app = create_app(config_class="app.tests.test_config.TestConfig")

    with test_app.app_context():
        db.create_all()
        print("Current Config:", test_app.config)  # Depuração
        assert test_app.config["TESTING"] is True  # Verifica se a configuração de teste está ativa
        assert test_app.config["JWT_SECRET_KEY"] == "your_secret_key_here"  # Confirma configuração do JWT
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    # Retorna um cliente de teste para interagir com o app
    return app.test_client()

def test_app_initialization(client):
    """Teste para garantir que o app inicializa corretamente."""
    response = client.get("/")
    assert response.status_code in [200, 404]  # Depende se você configurou uma rota para "/"

def test_jwt_manager_initialization(app):
    """Teste para garantir que o JWTManager foi inicializado."""
    assert "flask-jwt-extended" in app.extensions, "JWTManager não está inicializado no app."


def test_auth_endpoint(client):
    """Teste básico para o endpoint de autenticação."""
    response = client.post("/auth/login", json={"email": "test@example.com", "password": "password"})
    assert response.status_code == 200 or response.status_code == 401  # Ajuste conforme sua lógica

def test_register_user(client):
    """Teste para o endpoint de registro de usuário."""
    response = client.post("/auth/register", json={
        "email": "new_user@example.com",
        "password": "newpassword123"
    })
    assert response.status_code == 201 
    
def test_login_user(client):
    """Teste para o endpoint de login."""
    # Primeiro, registre um usuário
    client.post("/auth/register", json={
        "email": "test_user@example.com",
        "password": "testpassword"
    })

    # Em seguida, faça login
    response = client.post("/auth/login", json={
        "email": "test_user@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "token" in data

from unittest.mock import patch
import pytest
from app import create_app, db

@pytest.fixture
def app():
    # Configura o app para usar a configuração de testes
    test_app = create_app(config_class="app.tests.test_config.TestConfig")

    with test_app.app_context():
        db.create_all()  # Cria as tabelas no banco de dados em memória
        yield test_app
        db.session.remove()
        db.drop_all()  # Limpa o banco de dados após os testes

@pytest.fixture
def client(app):
    # Retorna um cliente de teste para interagir com o app
    return app.test_client()


@patch("app.use_cases.process_video", return_value="/tmp/processed/test_video.zip")
def test_upload_video_authenticated(mock_process_video, client):
    """Teste para upload de vídeo com usuário autenticado."""
    # Registra e faz login para obter um token
    response = client.post("/auth/register", json={
        "email": "video_user@example.com",
        "password": "videopassword"
    })
    assert response.status_code == 201, f"Unexpected status code: {response.status_code}"

    login_response = client.post("/auth/login", json={
        "email": "video_user@example.com",
        "password": "videopassword"
    })
    assert login_response.status_code == 200, f"Login failed with status code: {login_response.status_code}"

    token = login_response.get_json()["token"]
    assert token, "Token was not returned"

    # Upload de vídeo com token
    headers = {"Authorization": f"Bearer {token}"}
    with open("app/tests/assets/test_video.mp4", "rb") as video_file:
        response = client.post("/upload-video", headers=headers, data={
            "video": video_file
        })
    
    assert response.status_code == 200


@patch("app.use_cases.process_video", side_effect=Exception("FFmpeg error"))
def test_upload_video_processing_error(mock_process_video, client):
    """Teste para falha no processamento de vídeo."""
    # Registra e faz login para obter um token
    response = client.post("/auth/register", json={
        "email": "video_user@example.com",
        "password": "videopassword"
    })
    assert response.status_code == 201

    login_response = client.post("/auth/login", json={
        "email": "video_user@example.com",
        "password": "videopassword"
    })
    token = login_response.get_json()["token"]

    headers = {"Authorization": f"Bearer {token}"}
    with open("app/tests/assets/test_video.mp4", "rb") as video_file:
        response = client.post("/upload-video", headers=headers, data={
            "video": video_file
        })
    
    assert response.status_code != 200


def test_upload_video_unauthenticated(client):
    """Teste para upload de vídeo sem autenticação."""
    with open("app/tests/assets/test_video.mp4", "rb") as video_file:
        response = client.post("/upload-video", data={"video": video_file})
    assert response.status_code == 401  # Não autenticado

def test_list_videos(client):
    """Teste para listar vídeos de um usuário autenticado."""
    # Registra e faz login para obter um token
    client.post("/auth/register", json={
        "email": "list_user@example.com",
        "password": "listpassword"
    })
    login_response = client.post("/auth/login", json={
        "email": "list_user@example.com",
        "password": "listpassword"
    })
    token = login_response.get_json()["token"]

    # Lista os vídeos
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/list-videos", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "videos" in data
    assert isinstance(data["videos"], list)

def test_invalid_video_upload(client):
    """Teste para upload de um arquivo inválido (não é vídeo)."""
    # Registra e faz login para obter um token
    client.post("/auth/register", json={
        "email": "invalid_video_user@example.com",
        "password": "invalidpassword"
    })
    login_response = client.post("/auth/login", json={
        "email": "invalid_video_user@example.com",
        "password": "invalidpassword"
    })
    token = login_response.get_json()["token"]

    # Upload de arquivo inválido
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/upload-video", headers=headers, data={
        "video": (b"Not a video content", "test.txt")
    })
    assert response.status_code != 200  # Erro esperado para arquivo inválido

