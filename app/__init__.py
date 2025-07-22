import os
from flask import Flask
from flask_login import LoginManager
from config import config


def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Debug: Print loaded config values
    if app.debug:
        print("---- PaperHub Config ----")
        print(f"SECRET_KEY: {app.config['SECRET_KEY']}")
        print(f"DATABASE_URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"UPLOAD_FOLDER: {app.config['UPLOAD_FOLDER']}")
        print(f"MAX_CONTENT_LENGTH: {app.config['MAX_CONTENT_LENGTH']}")
        print(f"ALLOWED_EXTENSIONS: {app.config['ALLOWED_EXTENSIONS']}")
        print(f"SESSION_LIFETIME_DAYS: {app.config['PERMANENT_SESSION_LIFETIME']}")
        print(f"OPENROUTER_API_KEY: {app.config['OPENROUTER_API_KEY']}")
        print("------------------------")
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    from app.models import db
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.main import main_bp
    app.register_blueprint(main_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app 