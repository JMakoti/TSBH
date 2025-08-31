# Django Data Migration Documentation
# County Population Migration

## Overview
This document describes the data migration created to populate the County model with all 47 official counties of Kenya.

## Migration Details

**File**: `scholarships/migrations/0002_auto_20250831_1238.py`

**Purpose**: Populate the County model with comprehensive data for all 47 Kenyan counties

## Data Included

The migration includes the following data for each county:
- **Name**: Official county name (stored as choice value)
- **Code**: Official county code (3-digit format)
- **Capital City**: County headquarters/capital
- **Population**: Current estimated population (2019 Census data)
- **Area**: County area in square kilometers

## Counties Populated

The migration creates records for all 47 counties:

1. **Mombasa** (001) - Mombasa - Pop: 1,208,333 - Area: 229.7 km²
2. **Kwale** (002) - Kwale - Pop: 866,820 - Area: 8,270.3 km²
3. **Kilifi** (003) - Kilifi - Pop: 1,453,787 - Area: 12,245.9 km²
4. **Tana River** (004) - Hola - Pop: 315,943 - Area: 38,437.0 km²
5. **Lamu** (005) - Lamu - Pop: 143,920 - Area: 6,167.2 km²
...and 42 more counties

## Migration Features

### Forward Migration (`populate_counties`)
- Creates County objects using `get_or_create()` to avoid duplicates
- Includes comprehensive data for each county
- Provides console output showing created counties
- Uses the apps registry to get the model (migration best practice)

### Reverse Migration (`reverse_populate_counties`)
- Deletes all County objects
- Allows for clean rollback if needed
- Ensures migration reversibility

## Usage

### Apply Migration
```bash
python manage.py migrate
```

### Rollback Migration
```bash
python manage.py migrate scholarships 0001
```

### Check Migration Status
```bash
python manage.py showmigrations scholarships
```

## Data Sources

The county data is based on:
- **Official County Codes**: Kenya National Bureau of Statistics
- **Population Data**: Kenya Population and Housing Census 2019
- **Geographic Data**: Kenya National Bureau of Statistics
- **Administrative Data**: Commission on Revenue Allocation

## Technical Implementation

### Migration Structure
```python
def populate_counties(apps, schema_editor):
    County = apps.get_model('scholarships', 'County')
    # Data population logic
    
def reverse_populate_counties(apps, schema_editor):
    County = apps.get_model('scholarships', 'County')
    County.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [("scholarships", "0001_initial")]
    operations = [
        migrations.RunPython(
            populate_counties,
            reverse_populate_counties,
            hints={'model_name': 'county'}
        ),
    ]
```

### Key Benefits
1. **Atomic Operation**: All counties created in a single transaction
2. **Idempotent**: Safe to run multiple times
3. **Reversible**: Can be rolled back cleanly
4. **Comprehensive**: Includes all official county data
5. **Validated**: Uses Django model validation

## Verification

After running the migration, verify the data:

```python
# Check total count
from scholarships.models import County
print(f"Total counties: {County.objects.count()}")

# Check specific counties
nairobi = County.objects.get(name='nairobi')
print(f"Nairobi: {nairobi.capital_city}, Pop: {nairobi.population}")

# List all counties
for county in County.objects.all().order_by('code'):
    print(f"{county.code} - {county.get_name_display()}")
```

## Integration Points

This county data serves as the foundation for:
- **Student Profiles**: County of residence
- **Provider Locations**: Organization locations
- **Scholarship Targeting**: Geographic targeting of scholarships
- **Reporting**: Geographic analysis and reporting
- **Filtering**: County-based search and filtering

## Maintenance

### Updating County Data
If county data needs updates:
1. Create a new migration file
2. Update specific fields as needed
3. Maintain data consistency

### Adding New Fields
For new county fields:
1. Add model field migration first
2. Create data migration to populate new fields
3. Ensure backward compatibility

This data migration provides a solid foundation for geographic organization and targeting within the scholarship management system.
