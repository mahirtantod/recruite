from app import create_app
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app()

if __name__ == '__main__':
    # Create upload directories
    upload_folder = app.config['UPLOAD_FOLDER']
    try:
        os.makedirs(os.path.join(upload_folder, 'resumes'), exist_ok=True)
        os.makedirs(os.path.join(upload_folder, 'videos'), exist_ok=True)
        logger.info(f"Created upload directories in {upload_folder}")
    except Exception as e:
        logger.error(f"Error creating upload directories: {str(e)}")

    # Run the application
    app.run(debug=True)
