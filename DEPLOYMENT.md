# Deployment Guide for RecruitEase

## Prerequisites
1. A Hostinger account with:
   - PHP hosting plan
   - MySQL database
   - Python support enabled
   - SSH access (recommended)

## Deployment Steps

### 1. Database Setup
1. Create a new MySQL database in your Hostinger control panel
2. Note down the following credentials:
   - Database name
   - Username
   - Password
   - Host

### 2. Environment Variables
Create a `.env` file in your project root (don't commit this to version control):
```env
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key
MYSQL_HOST=your-mysql-host
MYSQL_USER=your-mysql-username
MYSQL_PASSWORD=your-mysql-password
MYSQL_DB=your-database-name
```

### 3. File Upload Directory
1. Create an 'uploads' directory in your hosting space
2. Create 'resumes' and 'videos' subdirectories
3. Set proper permissions:
```bash
chmod 755 uploads
chmod 755 uploads/resumes
chmod 755 uploads/videos
```

### 4. Application Files
1. Upload your application files to Hostinger via FTP or Git
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### 5. Web Server Configuration
Add this to your `.htaccess` file:
```apache
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^(.*)$ run.py [QSA,L]
```

### 6. Database Migration
Run these commands to set up your database:
```bash
flask db upgrade
```

## Important Notes

### Security
1. Always use HTTPS in production
2. Keep your `.env` file secure and never commit it
3. Use strong passwords for your database
4. Regularly update dependencies

### File Uploads
1. Maximum file size is set to 16MB
2. Supported resume formats: PDF, DOC, DOCX
3. Supported video formats: MP4, WebM, MOV

### Maintenance
1. Regularly backup your database
2. Monitor disk space usage in uploads directory
3. Check application logs for errors

## Troubleshooting

### Common Issues
1. **Database Connection Errors**
   - Verify MySQL credentials
   - Check if MySQL server is running
   - Ensure proper permissions

2. **File Upload Issues**
   - Check directory permissions
   - Verify file size limits
   - Ensure proper directory structure

3. **Application Errors**
   - Check application logs
   - Verify environment variables
   - Ensure all dependencies are installed

## Contact
For support, contact your system administrator or the development team.
