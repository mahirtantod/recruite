from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import os
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Add route to serve uploaded files
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        directory = os.path.dirname(filename)
        file_name = os.path.basename(filename)
        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], directory), file_name)
    
    with app.app_context():
        # Import models first
        from app.models import Job, Candidate
        
        # Import and register blueprints
        from app.routes import main
        from app.admin import admin
        app.register_blueprint(main)
        app.register_blueprint(admin)
        
        try:
            # Create tables only if they don't exist
            db.create_all()
        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}")
            
        # Ensure upload directories exist
        try:
            upload_folder = app.config['UPLOAD_FOLDER']
            os.makedirs(os.path.join(upload_folder, 'resumes'), exist_ok=True)
            os.makedirs(os.path.join(upload_folder, 'videos'), exist_ok=True)
        except Exception as e:
            app.logger.error(f"Error creating upload directories: {str(e)}")
    
    return app
