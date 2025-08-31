# Django Environment Configuration Guide

## Overview
This Django project is configured to use environment variables for sensitive data using the `django-environ` package.

## Setup Instructions

### 1. Install Required Packages
```bash
cd tuvuke_hub
python -m pip install -r requirements.txt
```

### 2. Environment Configuration
1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

2. Edit the `.env` file with your actual values:
   ```
   SECRET_KEY=your-actual-secret-key-here
   DEBUG=True
   DATABASE_URL=mysql://username:password@localhost:3306/tuvuke_hub_db
   ```

### 3. MySQL Database Setup
1. Install MySQL Server if not already installed
2. Create a database for the project:
   ```sql
   CREATE DATABASE tuvuke_hub_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'tuvuke_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON tuvuke_hub_db.* TO 'tuvuke_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. Update your `.env` file with the database credentials:
   ```
   DATABASE_URL=mysql://tuvuke_user:your_password@localhost:3306/tuvuke_hub_db
   ```

### 4. Generate a Secure Secret Key
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

## Environment Variables Reference

### Required Variables
- `SECRET_KEY`: Django secret key for cryptographic signing
- `DEBUG`: Boolean flag for debug mode (True/False)
- `DATABASE_URL`: Database connection string

### Optional Variables
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `TIME_ZONE`: Time zone setting (default: UTC)
- `LANGUAGE_CODE`: Language code (default: en-us)
- `EMAIL_HOST`: SMTP server host
- `EMAIL_PORT`: SMTP server port
- `EMAIL_HOST_USER`: Email username
- `EMAIL_HOST_PASSWORD`: Email password
- `AFRICASTALKING_USERNAME`: AfricasTalking username
- `AFRICASTALKING_API_KEY`: AfricasTalking API key

## Security Notes

1. **Never commit `.env` files** - They contain sensitive information
2. **Use different secret keys** for development and production
3. **Set DEBUG=False** in production
4. **Configure ALLOWED_HOSTS** properly for production
5. **Use strong database passwords**

## Production Deployment

For production, ensure you:
1. Set `DEBUG=False`
2. Configure proper `ALLOWED_HOSTS`
3. Use environment variables or a secure secret management system
4. Enable SSL/HTTPS
5. Use a production-grade database
6. Configure proper logging

## Troubleshooting

### Common Issues
1. **Import Error for mysqlclient**: Install MySQL development headers
   - Windows: Install MySQL Connector/C++
   - Ubuntu: `sudo apt-get install python3-dev default-libmysqlclient-dev build-essential`
   - macOS: `brew install mysql-client`

2. **Database Connection Error**: Verify MySQL service is running and credentials are correct

3. **Environment Variables Not Loading**: Ensure `.env` file is in the project root directory

## File Structure
```
tuvuke_hub/
├── .env                    # Environment variables (not in git)
├── .env.example           # Environment template
├── .gitignore            # Git ignore file
├── requirements.txt      # Python dependencies
├── manage.py            # Django management script
├── scholarships/        # Scholarships app
└── tuvuke_hub/         # Project settings
    └── settings.py     # Django settings with environment config
```
