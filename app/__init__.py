from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import datetime

db = SQLAlchemy()
migrate = Migrate()

from flask_jwt_extended import JWTManager

jwt = JWTManager()  # Instância global do JWTManager

def create_app(config_class=None):
    app = Flask(__name__)

    if config_class:
        app.config.from_object(config_class)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://fiap:fiap@db:5432/videoproject'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configurações para JWT
    app.config["JWT_SECRET_KEY"] = "your_secret_key_here"
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=1)

    # Inicializa JWTManager
    jwt.init_app(app)
    print("JWTManager initialized successfully.")

    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes import app_routes
    app.register_blueprint(app_routes)
    from user_auth.routes import user_routes
    app.register_blueprint(user_routes, url_prefix='/auth')

    return app
