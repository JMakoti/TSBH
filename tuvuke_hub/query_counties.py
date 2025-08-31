#!/usr/bin/env python
"""
County Data Query Examples
Demonstrates how to work with the populated County data
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tuvuke_hub.settings')
django.setup()

from scholarships.models import County


def display_all_counties():
    """Display all counties with their details"""
    print("=" * 80)
    print("ALL KENYAN COUNTIES")
    print("=" * 80)
    print(f"{'Code':<6} {'County Name':<20} {'Capital':<15} {'Population':<12} {'Area (km²)':<10}")
    print("-" * 80)
    
    counties = County.objects.all().order_by('code')
    for county in counties:
        print(f"{county.code:<6} {county.get_name_display():<20} {county.capital_city:<15} "
              f"{county.population:,} {county.area_sq_km:,.1f}")
    
    print("-" * 80)
    print(f"Total Counties: {counties.count()}")


def display_largest_counties():
    """Display counties by population"""
    print("\n" + "=" * 60)
    print("TOP 10 COUNTIES BY POPULATION")
    print("=" * 60)
    
    counties = County.objects.all().order_by('-population')[:10]
    for i, county in enumerate(counties, 1):
        print(f"{i:2d}. {county.get_name_display():<15} - {county.population:,} people")


def display_largest_by_area():
    """Display counties by area"""
    print("\n" + "=" * 60)
    print("TOP 10 COUNTIES BY AREA")
    print("=" * 60)
    
    counties = County.objects.all().order_by('-area_sq_km')[:10]
    for i, county in enumerate(counties, 1):
        print(f"{i:2d}. {county.get_name_display():<15} - {county.area_sq_km:,.1f} km²")


def search_counties(query):
    """Search counties by name or capital"""
    print(f"\n" + "=" * 60)
    print(f"SEARCH RESULTS FOR: '{query}'")
    print("=" * 60)
    
    from django.db.models import Q
    
    counties = County.objects.filter(
        Q(name__icontains=query) | 
        Q(capital_city__icontains=query)
    )
    
    if counties.exists():
        for county in counties:
            print(f"- {county.get_name_display()} (Capital: {county.capital_city})")
            print(f"  Code: {county.code}, Population: {county.population:,}, "
                  f"Area: {county.area_sq_km:,.1f} km²")
    else:
        print("No counties found matching your search.")


def display_statistics():
    """Display county statistics"""
    print("\n" + "=" * 60)
    print("COUNTY STATISTICS")
    print("=" * 60)
    
    from django.db.models import Sum, Avg, Max, Min
    
    stats = County.objects.aggregate(
        total_population=Sum('population'),
        avg_population=Avg('population'),
        max_population=Max('population'),
        min_population=Min('population'),
        total_area=Sum('area_sq_km'),
        avg_area=Avg('area_sq_km'),
        max_area=Max('area_sq_km'),
        min_area=Min('area_sq_km')
    )
    
    print(f"Total Population: {stats['total_population']:,}")
    print(f"Average Population: {stats['avg_population']:,.0f}")
    print(f"Largest County (Population): {stats['max_population']:,}")
    print(f"Smallest County (Population): {stats['min_population']:,}")
    print()
    print(f"Total Area: {stats['total_area']:,.1f} km²")
    print(f"Average Area: {stats['avg_area']:,.1f} km²")
    print(f"Largest County (Area): {stats['max_area']:,.1f} km²")
    print(f"Smallest County (Area): {stats['min_area']:,.1f} km²")


def main():
    """Main function to run all examples"""
    try:
        # Check if counties exist
        county_count = County.objects.count()
        if county_count == 0:
            print("No counties found in database!")
            print("Please run: python manage.py migrate")
            return
        
        # Display all counties
        display_all_counties()
        
        # Display largest counties by population
        display_largest_counties()
        
        # Display largest counties by area
        display_largest_by_area()
        
        # Display statistics
        display_statistics()
        
        # Example search
        search_counties("nai")
        
        print("\n" + "=" * 60)
        print("EXAMPLE USAGE IN DJANGO VIEWS/MODELS")
        print("=" * 60)
        print("""
# Get all counties for a dropdown
counties = County.objects.all().order_by('name')

# Get a specific county
nairobi = County.objects.get(name='nairobi')

# Filter students by county
from scholarships.models import Student
nairobi_students = Student.objects.filter(county__name='nairobi')

# Get counties in a specific region (example)
coastal_counties = County.objects.filter(
    name__in=['mombasa', 'kwale', 'kilifi', 'tana_river', 'lamu', 'taita_taveta']
)

# Count scholarships targeting specific counties
from scholarships.models import Scholarship
targeted_scholarships = Scholarship.objects.filter(
    target_counties__name='nairobi'
).count()
        """)
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have run 'python manage.py migrate' first")


if __name__ == "__main__":
    main()
