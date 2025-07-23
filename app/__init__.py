from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # Database configuration
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        DB_USER = os.getenv('DB_USER')
        DB_PASSWORD = os.getenv('DB_PASSWORD')
        DB_HOST = os.getenv('DB_HOST')
        DB_PORT = os.getenv('DB_PORT')
        DB_NAME = os.getenv('DB_NAME')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Email configuration (Brevo/Sendinblue)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'ropykevin@gmail.com'
    app.config['MAIL_PASSWORD'] = 'kqps pjic kalr lhrc'
    app.config['MAIL_DEFAULT_SENDER'] = 'ropykevin@gmail.com'

    db.init_app(app)
    mail.init_app(app)
    Migrate(app, db)

    # Import models
    from . import models

    # ✅ Register blueprint
    from .routes import main
    app.register_blueprint(main)
    print("Blueprint registered")
    print("Database initialized")
    print("Mail initialized")
    print("Routes registered")
    print("App initialized")

    return app
