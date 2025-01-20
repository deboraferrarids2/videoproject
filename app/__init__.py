from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import datetime

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://fiap:fiap@db:5432/videoproject'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config["JWT_SECRET_KEY"] = "your_secret_key_here"  # Chave secreta para assinar os tokens
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]  # Onde o token JWT será enviado (padrão: headers)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=1)  # Expiração do token

    # Inicializa o JWT Manager
    jwt = JWTManager(app)

    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes import app_routes
    app.register_blueprint(app_routes)
    from user_auth.routes import user_routes
    app.register_blueprint(user_routes, url_prefix='/auth')

    return app
