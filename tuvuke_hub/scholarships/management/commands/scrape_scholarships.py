import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.text import slugify
from scholarships.models import Scholarship, Provider
from datetime import datetime, timedelta
import re
import logging

# Set up logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Scrape Kenyan education websites for new scholarship opportunities'
    
    # Predefined list of Kenyan education websites to scrape
    WEBSITES = [
        {
            'name': 'Ministry of Education Kenya',
            'url': 'https://www.education.go.ke',
            'selectors': {
                'scholarship_links': 'a[href*="scholarship"], a[href*="bursary"]',
                'title': 'h1, h2, .title',
                'description': 'p, .content, .description',
                'deadline': 'span.deadline, .date, time'
            }
        },
        {
            'name': 'Universities Kenya',
            'url': 'https://www.universitieskenyaonline.com',
            'selectors': {
                'scholarship_links': 'a[href*="scholarship"]',
                'title': 'h1, h2, .post-title',
                'description': '.post-content, .entry-content, p',
                'deadline': '.deadline, .date'
            }
        },
        {
            'name': 'Kenya Education Blog',
            'url': 'https://kenyaeducation.info',
            'selectors': {
                'scholarship_links': 'a[href*="scholarship"], a[href*="bursary"]',
                'title': 'h1, .entry-title',
                'description': '.entry-content, .post-content',
                'deadline': '.deadline, .date'
            }
        }
    ]
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Maximum number of scholarships to scrape per website (default: 10)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be scraped without saving to database'
        )
        parser.add_argument(
            '--website',
            type=str,
            help='Scrape only a specific website by name'
        )
    
    def handle(self, *args, **options):
        self.limit = options['limit']
        self.dry_run = options['dry_run']
        target_website = options.get('website')
        
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No data will be saved to database')
            )
        
        # Get or create a default scraper provider
        scraper_provider, created = Provider.objects.get_or_create(
            name='Web Scraper',
            defaults={
                'slug': 'web-scraper',
                'provider_type': 'other',
                'funding_source': 'mixed',
                'email': 'scraper@tuvuke.com',
                'phone_number': '+254700000000',
                'physical_address': 'Automated Web Scraper',
                'description': 'Automatically scraped scholarship opportunities from various Kenyan education websites',
                'is_verified': False,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created scraper provider: {scraper_provider.name}')
            )
        
        total_scraped = 0
        
        for website in self.WEBSITES:
            if target_website and website['name'].lower() != target_website.lower():
                continue
                
            try:
                self.stdout.write(f'\nScraping {website["name"]}...')
                scraped_count = self.scrape_website(website, scraper_provider)
                total_scraped += scraped_count
                self.stdout.write(
                    self.style.SUCCESS(f'Scraped {scraped_count} scholarships from {website["name"]}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error scraping {website["name"]}: {str(e)}')
                )
                logger.error(f'Error scraping {website["name"]}: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal scholarships scraped: {total_scraped}')
        )
    
    def scrape_website(self, website, provider):
        """Scrape a single website for scholarship opportunities"""
        scraped_count = 0
        
        try:
            # Set up headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Get the main page
            response = requests.get(website['url'], headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find scholarship-related links
            scholarship_links = soup.select(website['selectors']['scholarship_links'])
            
            for link in scholarship_links[:self.limit]:
                try:
                    scholarship_url = self.get_absolute_url(link.get('href'), website['url'])
                    if scholarship_url:
                        scholarship_data = self.scrape_scholarship_page(
                            scholarship_url, website, headers
                        )
                        
                        if scholarship_data and self.save_scholarship(scholarship_data, provider):
                            scraped_count += 1
                            self.stdout.write(f'  ✓ {scholarship_data["title"][:50]}...')
                        
                except Exception as e:
                    logger.error(f'Error processing link {link}: {str(e)}')
                    continue
                    
        except requests.RequestException as e:
            raise CommandError(f'Failed to fetch {website["url"]}: {str(e)}')
        
        return scraped_count
    
    def scrape_scholarship_page(self, url, website, headers):
        """Scrape individual scholarship page for details"""
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_element = soup.select_one(website['selectors']['title'])
            title = title_element.get_text(strip=True) if title_element else 'Unknown Scholarship'
            
            # Extract description
            description_elements = soup.select(website['selectors']['description'])
            description_parts = []
            for element in description_elements[:3]:  # Limit to first 3 paragraphs
                text = element.get_text(strip=True)
                if text and len(text) > 20:  # Filter out very short text
                    description_parts.append(text)
            
            description = ' '.join(description_parts) if description_parts else 'No description available'
            
            # Extract deadline (try to parse date)
            deadline = self.extract_deadline(soup, website['selectors']['deadline'])
            
            # Generate estimated amount (since we can't reliably scrape this)
            estimated_amount = self.estimate_scholarship_amount(title, description)
            
            return {
                'title': title[:300],  # Limit title length
                'description': description[:2000],  # Limit description length
                'source_url': url,
                'deadline': deadline,
                'estimated_amount': estimated_amount
            }
            
        except Exception as e:
            logger.error(f'Error scraping scholarship page {url}: {str(e)}')
            return None
    
    def extract_deadline(self, soup, deadline_selector):
        """Extract and parse deadline from page content"""
        try:
            # Look for deadline in specific elements
            deadline_elements = soup.select(deadline_selector)
            
            for element in deadline_elements:
                text = element.get_text(strip=True)
                deadline = self.parse_date_string(text)
                if deadline:
                    return deadline
            
            # Look for deadline in the entire page text
            page_text = soup.get_text()
            deadline_patterns = [
                r'deadline[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
                r'closes?[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
                r'due[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})'
            ]
            
            for pattern in deadline_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    deadline = self.parse_date_string(match.group(1))
                    if deadline:
                        return deadline
            
            # Default deadline (3 months from now)
            return timezone.now() + timedelta(days=90)
            
        except Exception as e:
            logger.error(f'Error extracting deadline: {str(e)}')
            return timezone.now() + timedelta(days=90)
    
    def parse_date_string(self, date_string):
        """Parse various date string formats"""
        date_formats = [
            '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%m-%d-%Y',
            '%Y/%m/%d', '%Y-%m-%d', '%d %B %Y', '%B %d, %Y'
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_string.strip(), fmt)
                # Convert to timezone-aware datetime
                return timezone.make_aware(
                    datetime.combine(parsed_date.date(), datetime.min.time())
                )
            except ValueError:
                continue
        
        return None
    
    def estimate_scholarship_amount(self, title, description):
        """Estimate scholarship amount based on title and description"""
        # Look for amount patterns in title and description
        text = (title + ' ' + description).lower()
        
        # Pattern for Kenyan Shillings
        amount_patterns = [
            r'ksh?\s*(\d{1,3}(?:,\d{3})*)',
            r'(\d{1,3}(?:,\d{3})*)\s*(?:kenya[n]?\s*)?shillings?',
            r'(\d{1,3}(?:,\d{3})*)\s*thousand',
            r'(\d{1,3}(?:,\d{3})*)\s*million'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = int(amount_str)
                    if 'million' in match.group(0):
                        amount *= 1000000
                    elif 'thousand' in match.group(0):
                        amount *= 1000
                    return min(amount, 10000000)  # Cap at 10M KES
                except ValueError:
                    continue
        
        # Default amounts based on keywords
        if any(word in text for word in ['university', 'undergraduate', 'degree']):
            return 200000  # 200K KES for university scholarships
        elif any(word in text for word in ['secondary', 'high school', 'form']):
            return 50000   # 50K KES for secondary school
        elif any(word in text for word in ['primary', 'elementary']):
            return 20000   # 20K KES for primary school
        else:
            return 100000  # Default 100K KES
    
    def save_scholarship(self, scholarship_data, provider):
        """Save scraped scholarship to database"""
        try:
            # Create slug from title
            slug = slugify(scholarship_data['title'])
            
            # Check if scholarship already exists
            if Scholarship.objects.filter(
                title=scholarship_data['title'],
                provider=provider
            ).exists():
                return False  # Skip if already exists
            
            if self.dry_run:
                self.stdout.write(f'  [DRY RUN] Would create: {scholarship_data["title"]}')
                return True
            
            # Create scholarship object
            scholarship = Scholarship.objects.create(
                title=scholarship_data['title'],
                slug=slug,
                provider=provider,
                scholarship_type='need',  # Default type
                description=scholarship_data['description'],
                eligibility_criteria={
                    'source': 'web_scraper',
                    'source_url': scholarship_data['source_url'],
                    'scraped_date': timezone.now().isoformat()
                },
                required_documents=[
                    'application_form',
                    'academic_transcript',
                    'national_id'
                ],
                target_education_levels=['secondary', 'undergraduate'],
                coverage_type='partial',
                amount_per_beneficiary=scholarship_data['estimated_amount'],
                total_budget=scholarship_data['estimated_amount'] * 10,  # Estimate 10 recipients
                number_of_awards=10,  # Default number
                application_start_date=timezone.now(),
                application_deadline=scholarship_data['deadline'],
                status='active',
                application_method='online',
                external_application_url=scholarship_data['source_url'],
                tags=['scraped', 'kenya', 'education'],
                meta_description=scholarship_data['description'][:160],
                source='scraper',
                source_url=scholarship_data['source_url']
            )
            
            return True
            
        except Exception as e:
            logger.error(f'Error saving scholarship {scholarship_data["title"]}: {str(e)}')
            return False
    
    def get_absolute_url(self, url, base_url):
        """Convert relative URL to absolute URL"""
        if not url:
            return None
            
        if url.startswith('http'):
            return url
        elif url.startswith('/'):
            from urllib.parse import urljoin
            return urljoin(base_url, url)
        else:
            from urllib.parse import urljoin
            return urljoin(base_url + '/', url)
