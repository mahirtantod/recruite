# Recruitment Portal with Interactive Chatbot

A Flask-based recruitment portal with an interactive chatbot for job applications.

## Features

- Interactive chatbot for job applications
- Admin dashboard for job management
- Candidate tracking system
- File upload support for resumes and videos
- Real-time job status updates

## Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python run.py
   ```

## Deployment to Render

1. Create a new account on [Render](https://render.com)
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Fill in the following details:
   - Name: recruitment-portal
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn -c gunicorn.conf.py run:app`
5. Add the following environment variables:
   - `SECRET_KEY`: Your secret key
   - `DATABASE_URL`: Your database URL (Render will provide this)
   - `UPLOAD_FOLDER`: Path for uploads

## Environment Variables

- `SECRET_KEY`: Flask secret key
- `DATABASE_URL`: Database connection URL
- `UPLOAD_FOLDER`: Path for file uploads

## Database Migrations

```bash
flask db init
flask db migrate
flask db upgrade
```
