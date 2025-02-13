from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')
    
    # Configure upload directories
    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    resumes_dir = os.path.join(uploads_dir, 'resumes')
    videos_dir = os.path.join(uploads_dir, 'videos')
    
    # Create directories if they don't exist
    os.makedirs(resumes_dir, exist_ok=True)
    os.makedirs(videos_dir, exist_ok=True)
    
    # Load configuration
    app.config.from_object(Config)
    
    CORS(app)
    db.init_app(app)
    
    # Add route to serve uploaded files
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        directory = os.path.dirname(filename)
        file_name = os.path.basename(filename)
        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], directory), file_name)
    
    with app.app_context():
        # Import routes and models
        from app.routes import main
        from app.admin import admin
        
        # Register blueprints
        app.register_blueprint(main)
        app.register_blueprint(admin)
        
        # Drop all tables and create new ones
        db.drop_all()
        db.create_all()
        
    return app
