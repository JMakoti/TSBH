# Django Admin Customizations for Tuvuke Hub

This document outlines the custom Django admin implementations created for the Tuvuke Hub scholarship management system.

## 1. Custom ScholarshipAdmin Class

### Overview
The `ScholarshipAdmin` class has been customized to display specific fields in the list view and provide filtering and search capabilities.

### Features
- **List Display**: Shows `title`, `provider`, `deadline`, `is_verified`, and `is_active` columns
- **Filters**: Added filters for `is_verified` and `county` (via target_counties)
- **Search**: Search functionality for the `title` field
- **Custom Methods**:
  - `deadline()`: Formats the application deadline as 'YYYY-MM-DD HH:MM'
  - `is_verified()`: Shows verification status based on the provider's verification status

### File Location
`scholarships/admin.py` - `ScholarshipAdmin` class

## 2. Provider Admin Action

### Overview
Added a custom Django admin action for the Provider model to bulk verify providers.

### Features
- **Action Name**: "Mark selected providers as verified"
- **Functionality**: Sets `is_verified=True` and `verification_date=now()` for selected providers
- **User Feedback**: Displays success message with count of updated providers
- **Efficiency**: Only updates providers that aren't already verified

### Usage
1. Go to Provider admin page
2. Select providers using checkboxes
3. Choose "Mark selected providers as verified" from the Actions dropdown
4. Click "Go"

### File Location
`scholarships/admin.py` - `ProviderAdmin.mark_as_verified()` method

## 3. Web Scraping Management Command

### Overview
A Django management command that scrapes Kenyan education websites for scholarship opportunities using BeautifulSoup.

### Features
- **Command**: `python manage.py scrape_scholarships`
- **Predefined Websites**: Ministry of Education Kenya, Universities Kenya, Kenya Education Blog
- **Auto-creates**: Scholarships with `is_verified=False` and `source='scraper'`
- **Smart Parsing**: Extracts titles, descriptions, deadlines, and estimates amounts
- **Duplicate Prevention**: Checks for existing scholarships before creating new ones

### Command Options
```bash
# Basic usage
python manage.py scrape_scholarships

# Limit results per website
python manage.py scrape_scholarships --limit 5

# Dry run (preview without saving)
python manage.py scrape_scholarships --dry-run

# Scrape specific website
python manage.py scrape_scholarships --website "Ministry of Education Kenya"
```

### Features Detail
- **Provider Creation**: Auto-creates a "Web Scraper" provider if it doesn't exist
- **URL Handling**: Converts relative URLs to absolute URLs
- **Date Parsing**: Intelligent deadline extraction and parsing
- **Amount Estimation**: Estimates scholarship amounts based on content analysis
- **Error Handling**: Continues scraping even if individual pages fail
- **Logging**: Comprehensive logging of scraping activities

### File Location
`scholarships/management/commands/scrape_scholarships.py`

### Dependencies
- `beautifulsoup4>=4.12.2`
- `requests>=2.31.0`
- `lxml>=4.9.3`

## 4. Custom Admin Dashboard with Analytics

### Overview
Extended the Django admin dashboard to display comprehensive analytics about the scholarship system.

### Features

#### Analytics Displayed
- **Core Metrics**:
  - Total Students
  - Available Scholarships
  - Total Applications
  - Scholarship Providers
  - Total Disbursed Amount
  - Counties Represented

#### Application Statistics
- Submitted Applications
- Approved Applications
- Under Review Applications
- Success Rate (approval percentage)

#### Scholarship Statistics
- Active Scholarships
- Verified Providers
- Total Scholarship Value
- Average Award Amount

#### Student Demographics
- Verified Students
- Female Students (with percentage)
- Students with Disabilities
- Orphaned Students

#### Recent Activity (Last 30 Days)
- New Students
- New Applications
- New Scholarships
- Total Disbursements

### Technical Implementation

#### Custom Admin Site
Created a custom admin site class (`TuvukeAdminSite`) that:
- Extends Django's default `AdminSite`
- Overrides the `index()` method to inject analytics data
- Calculates real-time statistics using Django ORM aggregations

#### Template Override
- **File**: `templates/admin/index.html`
- **Extends**: Default Django admin index template
- **Features**:
  - Responsive grid layout
  - Color-coded statistics cards
  - Hover effects and animations
  - Real-time data display

#### URL Configuration
Added a separate admin interface accessible at `/tuvuke-admin/` while keeping the default Django admin at `/admin/`.

### File Locations
- **Admin Site**: `scholarships/admin.py` - `TuvukeAdminSite` class
- **Template**: `templates/admin/index.html`
- **URLs**: `tuvuke_hub/urls.py`

### Styling
- Custom CSS with Bootstrap-inspired design
- Color-coded cards for different metric types
- Responsive design for mobile compatibility
- Professional dashboard appearance

## 5. New Model Fields

### Overview
Added source tracking fields to the Scholarship model to track where scholarship records originate.

### New Fields
- **`source`**: CharField with choices (manual, scraper, import, api)
- **`source_url`**: URLField for original source URL (optional)

### Migration
- **File**: `scholarships/migrations/0003_add_source_fields.py`
- **Purpose**: Adds the new fields to existing Scholarship model

## Installation and Setup

### 1. Install Dependencies
```bash
pip install beautifulsoup4 requests lxml
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Access Custom Admin
- **Default Admin**: `http://your-site.com/admin/`
- **Analytics Dashboard**: `http://your-site.com/tuvuke-admin/`

### 4. Test Web Scraping
```bash
# Dry run first
python manage.py scrape_scholarships --dry-run --limit 2

# Actual scraping
python manage.py scrape_scholarships --limit 5
```

## Security Considerations

### Web Scraping
- Implements proper User-Agent headers
- Includes timeout handling
- Respects website structure
- Error handling prevents crashes

### Admin Interface
- Maintains Django's built-in admin security
- No additional authentication bypass
- Proper permission checking

## Performance Considerations

### Analytics Dashboard
- Uses efficient Django ORM aggregations
- Calculates statistics on-demand
- Minimal database queries
- Can be extended with caching if needed

### Web Scraping
- Configurable limits per website
- Timeout handling prevents hanging
- Continues on individual page failures
- Duplicate prevention reduces unnecessary database writes

## Future Enhancements

### Possible Improvements
1. **Caching**: Add Redis/Memcached for analytics data
2. **Scheduled Scraping**: Use Celery for automated periodic scraping
3. **More Websites**: Add more Kenyan education websites to scraping list
4. **Advanced Filtering**: More sophisticated content filtering in scraper
5. **Email Notifications**: Alert admins when new scholarships are scraped
6. **Data Validation**: Enhanced validation for scraped scholarship data

## Troubleshooting

### Common Issues

1. **Scraping Failures**
   - Check internet connection
   - Verify website URLs are accessible
   - Check for website structure changes

2. **Template Not Loading**
   - Ensure templates directory is in TEMPLATES setting
   - Check template file paths

3. **Analytics Not Displaying**
   - Verify custom admin site is properly configured
   - Check URL configuration
   - Ensure analytics template is accessible

### Support
For issues or questions, refer to the Django documentation or project maintainers.
