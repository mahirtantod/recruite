import os
from datetime import timedelta

class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///recruitment.db')
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
         # Add SSL mode and other connection parameters
        if '?' in SQLALCHEMY_DATABASE_URI:
            SQLALCHEMY_DATABASE_URI += "&sslmode=require&connect_timeout=30"
        else:
            SQLALCHEMY_DATABASE_URI += "?sslmode=require&connect_timeout=30"
    
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Enable connection health checks
        'pool_recycle': 300,    # Recycle connections every 5 minutes
        'pool_timeout': 30,     # Connection timeout of 30 seconds
        'pool_size': 10,        # Maximum pool size
        'max_overflow': 5       # Maximum number of connections that can be created beyond pool_size
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    IS_PRODUCTION = os.environ.get('RENDER', False)
    if IS_PRODUCTION:
        UPLOAD_FOLDER = '/tmp/uploads'  # Use /tmp directory in production
    else:
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Session
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    def __init__(self):
        # Create upload directories
        os.makedirs(os.path.join(self.UPLOAD_FOLDER, 'resumes'), exist_ok=True)
        os.makedirs(os.path.join(self.UPLOAD_FOLDER, 'videos'), exist_ok=True)

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

# Choose configuration based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
