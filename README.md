# Tuvuke Hub - Scholarship Management System

## Overview

Tuvuke Hub is a comprehensive scholarship management system built with Django that connects students with scholarship opportunities across Kenya. The platform enables students to discover, apply for, and track scholarship applications while providing providers with tools to manage their scholarship programs.

## 🚀 Features

### For Students
- **Personalized Dashboard**: View recommended scholarships based on profile matching
- **Smart Search & Filtering**: Find scholarships by location, education level, field of study, and more
- **Application Management**: Track application status and deadlines
- **Profile Management**: Complete academic and personal profiles for better matching
- **Real-time Notifications**: Get updates on application status changes

### For Scholarship Providers
- **Scholarship Creation**: Create and manage scholarship programs
- **Applicant Management**: Review and evaluate applications
- **Advanced Filtering**: Filter applicants by various criteria
- **Communication Tools**: Send notifications and updates to applicants

### For Administrators
- **Comprehensive Admin Panel**: Manage users, scholarships, and applications
- **Analytics Dashboard**: View system statistics and trends
- **Content Moderation**: Verify providers and monitor scholarship quality
- **Bulk Operations**: Perform administrative tasks efficiently

## 🏗️ System Architecture

### Technology Stack
- **Backend**: Django 5.2.4
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Bootstrap 5, HTMX for dynamic interactions
- **Authentication**: Custom Django authentication with role-based access
- **Static Files**: Django static files management

### Core Models

#### User Management
- **User**: Extended Django User model
- **Student**: Student profile with academic and personal information
- **Provider**: Scholarship provider organizations

#### Scholarship System
- **Scholarship**: Core scholarship information
- **Application**: Student applications to scholarships
- **County**: Kenyan county geographic data

#### Supporting Models
- **Notification**: System notifications
- **Various utility models** for metadata and tracking

## 📁 Project Structure

```
tuvuke_hub/
├── manage.py                   # Django management script
├── tuvuke_hub/                # Main project directory
│   ├── settings.py            # Project settings
│   ├── urls.py               # URL routing
│   └── wsgi.py               # WSGI configuration
├── scholarships/              # Main application
│   ├── models.py             # Database models
│   ├── views.py              # View logic
│   ├── views_htmx.py         # HTMX-specific views
│   ├── auth_views.py         # Authentication views
│   ├── admin.py              # Django admin configuration
│   ├── urls.py               # App URL patterns
│   ├── forms.py              # Django forms
│   ├── access_control.py     # Role-based access control
│   ├── backends.py           # Custom authentication backends
│   └── templates/            # HTML templates
└── templates/                # Global templates
    ├── base.html             # Base template
    ├── auth/                 # Authentication templates
    └── scholarships/         # Scholarship-specific templates
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/bajunii/TSBH.git
cd TSBH/tuvuke_hub
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
Create a `.env` file in the project root:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
TIME_ZONE=Africa/Nairobi
LANGUAGE_CODE=en-us
```

### Step 5: Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
```

### Step 6: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 7: Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to access the application.

## 🎯 How the System Works

### User Registration & Authentication

1. **Student Registration**
   - Users register with basic information (name, email, phone)
   - Complete detailed academic profile (GPA, education level, field of study)
   - System validates national ID and phone number uniqueness

2. **Provider Registration**
   - Organizations register as scholarship providers
   - Admin verification required before they can create scholarships
   - Enhanced profile with organizational details

### Scholarship Discovery & Application

1. **Search & Filtering**
   - Students browse scholarships on the homepage
   - Advanced filtering by county, education level, amount, deadline
   - Real-time search with HTMX for smooth user experience

2. **Matching Algorithm**
   - System calculates compatibility scores between students and scholarships
   - Factors include: location, education level, GPA, family income, special criteria
   - Personalized recommendations displayed on student dashboard

3. **Application Process**
   - Students click "Apply Now" on scholarship listings
   - Complete application form with personal statement, documents
   - System tracks application status and deadlines

### Application Management

1. **For Students**
   - Dashboard shows all applications with status tracking
   - Notifications for status changes and deadlines
   - Ability to update profile for better matching

2. **For Providers**
   - Review applications in provider dashboard
   - Filter and sort applicants by various criteria
   - Update application status and send notifications

3. **For Administrators**
   - Overview of all applications and scholarships
   - Moderation tools for content quality
   - Analytics and reporting features

### Key System Features

#### Role-Based Access Control
- **Students**: Access to search, apply, and track applications
- **Providers**: Create scholarships and manage applications
- **Admins**: Full system access with moderation capabilities

#### Smart Matching System
```python
# Example matching calculation
def calculate_match_score(student, scholarship):
    score = 0
    
    # Location matching (30%)
    if student.county in scholarship.target_counties:
        score += 30
    
    # Education level (25%)
    if student.education_level in scholarship.target_education_levels:
        score += 25
    
    # GPA requirements (20%)
    if student.gpa >= scholarship.minimum_gpa:
        score += 20
    
    # Additional criteria (25%)
    # Age, income, special requirements, etc.
    
    return min(score, 100)  # Cap at 100%
```

#### Real-time Features
- HTMX-powered search without page reloads
- Dynamic form validation
- Live application status updates
- Instant scholarship filtering

## 🗃️ Database Schema

### Core Relationships
- Students have many Applications
- Scholarships belong to Providers
- Applications link Students and Scholarships
- Counties are referenced by Students and Scholarships

### Key Fields

**Student Model:**
- Personal: name, email, phone, national_id, date_of_birth
- Academic: education_level, current_gpa, field_of_study
- Geographic: county, current_institution
- Financial: family_annual_income

**Scholarship Model:**
- Basic: title, description, amount_per_beneficiary
- Dates: application_start_date, application_deadline
- Eligibility: minimum_gpa, target_education_levels, target_counties
- Constraints: maximum_age, minimum_age, for_females_only, etc.

**Application Model:**
- References: student, scholarship
- Content: personal_statement, motivation_letter, career_goals
- Status: status, submission_date, evaluation_score
- Metadata: created_at, updated_at, last_modified_date

## 🔧 Configuration

### Django Settings
Key configuration areas:
- Database configuration in `DATABASES`
- Static files handling with `STATIC_URL` and `STATICFILES_DIRS`
- Authentication backends in `AUTHENTICATION_BACKENDS`
- Time zone set to 'Africa/Nairobi'

### URL Configuration
- Root URLs in `tuvuke_hub/urls.py`
- App URLs in `scholarships/urls.py`
- Namespaced URLs for organization

### Custom Features
- Custom authentication backends for role-based login
- Middleware for request processing
- Custom management commands for data operations

## 🚦 Usage Examples

### Creating a Scholarship (Provider)
1. Log in as verified provider
2. Navigate to "Create Scholarship"
3. Fill in scholarship details, eligibility criteria
4. Set application deadlines and requirements
5. Publish for student applications

### Applying for Scholarships (Student)
1. Complete student profile registration
2. Browse scholarships on homepage
3. Use filters to find relevant opportunities
4. Click "Apply Now" on desired scholarships
5. Complete application form and submit

### Managing Applications (Admin)
1. Access Django admin panel at `/admin/`
2. Monitor scholarship and application activity
3. Verify new providers and moderate content
4. Generate reports and analytics

## 🔐 Security Features

- CSRF protection on all forms
- User authentication required for sensitive operations
- Role-based access control with custom mixins
- Input validation and sanitization
- Secure password handling with Django's built-in tools

## 📊 Analytics & Reporting

The system tracks:
- User registration and activity patterns
- Scholarship application rates and success metrics
- Popular scholarship categories and criteria
- Geographic distribution of users and opportunities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with appropriate tests
4. Submit a pull request with detailed description

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For technical support or questions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation in the `docs/` directory

## Development Team 

- Haitham Omar Omar - full-stack developer(email:haithamomar520@gmail.com)
- Joseph Mwamuye - full-stack developer(email:josephmwamuye5@gmail.com)

## 🔄 Future Enhancements

- Mobile application development
- Payment gateway integration for scholarships
- Advanced analytics dashboard
- Email notification system
- Document management system
- Integration with educational institutions

---

**Tuvuke Hub** - Empowering Education Through Technology

## 🚀 Deployment Guide for Render

### Quick Deploy to Render (Recommended)

Follow these steps for a fast and clean deployment to Render:

#### Step 1: Pre-deployment Setup

1. **Ensure all files are ready:**
   ```bash
   # Navigate to project directory
   cd tuvuke_hub
   
   # Check that all deployment files exist
   ls build.sh render.yaml tuvuke_hub/settings_prod.py
   ```

2. **Make build script executable:**
   ```bash
   chmod +x build.sh
   ```

3. **Test locally (Optional but recommended):**
   ```bash
   # Install production dependencies
   pip install -r requirements.txt
   
   # Test production settings
   export DJANGO_SETTINGS_MODULE=tuvuke_hub.settings_prod
   export SECRET_KEY=test-key-for-local-testing
   export DATABASE_URL=sqlite:///db.sqlite3
   export DEBUG=False
   
   python manage.py check --deploy
   ```

#### Step 2: Deploy to Render

##### Option A: Using render.yaml (Automated - Fastest)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Deploy to Render: Add production configuration"
   git push origin main
   ```

2. **Deploy on Render:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Select the `render.yaml` file
   - Click "Apply"

##### Option B: Manual Setup (More Control)

1. **Create PostgreSQL Database:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "PostgreSQL"
   - Settings:
     - **Name**: `tuvuke-hub-db`
     - **Database**: `tuvuke_hub`
     - **User**: `admin`
     - **Plan**: Free (or paid for production)
   - Click "Create Database"
   - **Copy the External Database URL**

2. **Create Web Service:**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Settings:
     - **Name**: `tuvuke-hub`
     - **Environment**: `Python 3`
     - **Build Command**: `chmod +x build.sh && ./build.sh`
     - **Start Command**: `gunicorn tuvuke_hub.wsgi:application`
     - **Plan**: Free (or paid for production)

3. **Environment Variables:**
   ```env
   DJANGO_SETTINGS_MODULE=tuvuke_hub.settings_prod
   SECRET_KEY=[Generate a strong secret key]
   DATABASE_URL=[Paste the PostgreSQL URL from step 1]
   DEBUG=False
   ALLOWED_HOSTS=your-app-name.onrender.com,.onrender.com
   PYTHON_VERSION=3.11
   ```

#### Step 3: Post-Deployment Configuration

1. **Create Superuser:**
   - Go to your web service dashboard
   - Click "Shell" tab
   - Run:
     ```bash
     python manage.py createsuperuser
     ```

2. **Load Initial Data (if needed):**
   ```bash
   # Load counties data
   python manage.py loaddata counties.json
   
   # Load sample scholarships (if you have fixtures)
   python manage.py loaddata sample_scholarships.json
   ```

3. **Test the Deployment:**
   - Visit your app: `https://your-app-name.onrender.com`
   - Test key features:
     - Homepage loads
     - User registration works
     - Admin panel accessible: `/admin/`
     - Health check: `/health/`

### Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_SETTINGS_MODULE` | Django settings module | `tuvuke_hub.settings_prod` |
| `SECRET_KEY` | Django secret key | `your-secret-key-here` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `DEBUG` | Debug mode (always False in production) | `False` |
| `ALLOWED_HOSTS` | Allowed hostnames | `your-app.onrender.com,.onrender.com` |
| `EMAIL_HOST_USER` | Email service username (optional) | `your-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Email service password (optional) | `your-app-password` |

### Troubleshooting Common Issues

#### Build Failures
- **Python version issues**: Ensure `PYTHON_VERSION=3.11` is set
- **Dependency conflicts**: Check `requirements.txt` for version conflicts
- **Permission denied**: Ensure `build.sh` is executable with `chmod +x build.sh`

#### Database Issues
- **Connection refused**: Verify `DATABASE_URL` is correctly set
- **Migration errors**: Check that migrations are up to date locally first
- **Permission denied**: Ensure database user has proper permissions

#### Static Files Not Loading
- **WhiteNoise not working**: Verify it's in `MIDDLEWARE` in settings
- **Missing collectstatic**: Ensure `build.sh` runs `collectstatic`
- **Wrong static URL**: Check `STATIC_URL` and `STATIC_ROOT` settings

#### SSL/HTTPS Issues
- **Mixed content**: Ensure all resources use HTTPS in production
- **Redirect loops**: Check `SECURE_SSL_REDIRECT` setting
- **Certificate issues**: Render handles SSL automatically

### Performance Optimization

1. **Database Optimization:**
   - Use connection pooling with `conn_max_age=600`
   - Add database indexes for frequently queried fields
   - Use `select_related()` and `prefetch_related()` for complex queries

2. **Static Files:**
   - Enable compression with WhiteNoise
   - Use CDN for media files in production
   - Optimize images and CSS/JS files

3. **Caching:**
   - Enable database caching for session storage
   - Cache expensive database queries
   - Use Redis for advanced caching (paid plans)

### Monitoring and Maintenance

1. **Health Monitoring:**
   - Health check endpoint: `/health/`
   - Monitor application logs in Render dashboard
   - Set up alerting for downtime

2. **Database Maintenance:**
   - Regular backups (automatic on paid plans)
   - Monitor database size and performance
   - Clean up old sessions and logs periodically

3. **Updates and Deployments:**
   - Use Git branches for feature development
   - Test changes locally before deployment
   - Use Render's preview deployments for testing

### Cost Optimization

1. **Free Tier Limitations:**
   - Services sleep after 15 minutes of inactivity
   - 750 hours per month limit
   - Limited bandwidth and storage

2. **Upgrade Considerations:**
   - **Starter ($7/month)**: No sleeping, more bandwidth
   - **Standard ($25/month)**: Better performance, more resources
   - **Pro ($85/month)**: High availability, advanced features

### Security Best Practices

1. **Environment Variables:**
   - Never commit secrets to Git
   - Use strong, unique secret keys
   - Rotate credentials regularly

2. **Django Security:**
   - Keep Django and dependencies updated
   - Use HTTPS everywhere (`SECURE_SSL_REDIRECT=True`)
   - Enable security headers

3. **Database Security:**
   - Use strong database passwords
   - Limit database access to your application
   - Regular security updates

### Deployment Checklist

- [ ] `build.sh` is executable
- [ ] `requirements.txt` includes all production dependencies
- [ ] `settings_prod.py` is configured correctly
- [ ] Environment variables are set in Render
- [ ] Database is created and connected
- [ ] Static files are configured with WhiteNoise
- [ ] Health check endpoint is working
- [ ] Superuser account is created
- [ ] SSL/HTTPS is working
- [ ] All key features are tested

### Expected Deployment Time

- **Preparation**: 15-20 minutes
- **Render Setup**: 10-15 minutes
- **Build and Deploy**: 5-10 minutes
- **Testing and Configuration**: 10-15 minutes

**Total**: ~40-60 minutes for complete deployment

Your Tuvuke Hub will be live at: `https://your-app-name.onrender.com`

---
