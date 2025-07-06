from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# Initialize SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'smartbiller254!')
    
    # Database Configuration - Support both DATABASE_URL and individual variables
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Use DATABASE_URL if provided (Docker setup)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Fallback to individual environment variables
        DB_USER = os.getenv('DB_USER', 'smartbiller')
        DB_PASSWORD = os.getenv('DB_PASSWORD', 'smartbiller254!')
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = os.getenv('DB_PORT', '5432')
        DB_NAME = os.getenv('DB_NAME', 'smartbiller')
        
        app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)

    # Import models after db initialization
    from . import models
    
    # Import and register routes after db initialization
    from . import routes
    routes.init_app(app)

    return app 