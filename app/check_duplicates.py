#!/usr/bin/env python
"""
Script to check for duplicate sensor data entries and clean them up
"""

import os
import sys
import django
from collections import defaultdict

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from dashboard.models import SensorData
from django.db.models import Count
from django.utils import timezone
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_duplicates():
    """Check for duplicate sensor data entries"""
    print("🔍 Checking for duplicate sensor data entries...")
    
    # Get all sensor data
    all_data = SensorData.objects.all().order_by('timestamp')
    total_records = all_data.count()
    
    print(f"Total records in database: {total_records}")
    
    # Check for exact duplicates (same timestamp and values)
    duplicates = defaultdict(list)
    
    for data in all_data:
        # Create a key based on timestamp and sensor values
        key = (
            data.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            data.temperature,
            data.humidity,
            data.rainfall,
            data.thunder,
            data.pest_count,
            data.battery_level,
            data.cpu_usage,
            data.status,
            data.latitude,
            data.longitude
        )
        duplicates[key].append(data.id)
    
    # Find duplicates
    duplicate_groups = {k: v for k, v in duplicates.items() if len(v) > 1}
    
    if duplicate_groups:
        print(f"\n❌ Found {len(duplicate_groups)} groups of duplicates:")
        total_duplicates = 0
        
        for key, ids in duplicate_groups.items():
            print(f"\n📅 Timestamp: {key[0]}")
            print(f"   Temperature: {key[1]}°C")
            print(f"   Humidity: {key[2]}%")
            print(f"   Duplicate IDs: {ids}")
            print(f"   Count: {len(ids)}")
            total_duplicates += len(ids) - 1  # Keep one, remove the rest
        
        print(f"\n📊 Summary:")
        print(f"   Total duplicate records to remove: {total_duplicates}")
        print(f"   Records to keep: {total_records - total_duplicates}")
        
        return duplicate_groups
    else:
        print("✅ No exact duplicates found!")
        return {}

def remove_duplicates(duplicate_groups):
    """Remove duplicate entries, keeping the first one"""
    if not duplicate_groups:
        print("No duplicates to remove.")
        return
    
    print("\n🗑️ Removing duplicate entries...")
    total_removed = 0
    
    for key, ids in duplicate_groups.items():
        # Keep the first ID, remove the rest
        ids_to_remove = ids[1:]  # Remove all except the first
        
        for data_id in ids_to_remove:
            try:
                SensorData.objects.get(id=data_id).delete()
                total_removed += 1
                print(f"   Removed duplicate ID: {data_id}")
            except SensorData.DoesNotExist:
                print(f"   Record with ID {data_id} already removed")
    
    print(f"\n✅ Successfully removed {total_removed} duplicate records!")

def add_unique_constraint():
    """Add a unique constraint to prevent future duplicates"""
    print("\n🔒 Adding unique constraint to prevent future duplicates...")
    
    # This would require a migration
    # For now, we'll implement logic in the save method
    print("   Note: Unique constraint logic will be implemented in the model")

def show_recent_data():
    """Show the most recent sensor data entries"""
    print("\n📋 Recent sensor data entries:")
    recent_data = SensorData.objects.all().order_by('-timestamp')[:10]
    
    for i, data in enumerate(recent_data, 1):
        print(f"\n{i}. ID: {data.id}")
        print(f"   Timestamp: {data.timestamp}")
        print(f"   Temperature: {data.temperature}°C")
        print(f"   Humidity: {data.humidity}%")
        print(f"   Rainfall: {data.rainfall}mm")
        print(f"   Pest Count: {data.pest_count}")
        print(f"   Status: {data.status}")

def main():
    """Main function to check and clean duplicates"""
    print("=" * 60)
    print("SENSOR DATA DUPLICATE CHECKER")
    print("=" * 60)
    
    # Check for duplicates
    duplicates = check_duplicates()
    
    if duplicates:
        response = input("\n❓ Do you want to remove these duplicates? (y/n): ").lower().strip()
        if response == 'y':
            remove_duplicates(duplicates)
            print("\n✅ Duplicate removal completed!")
        else:
            print("\n⏭️ Skipping duplicate removal.")
    
    # Show recent data
    show_recent_data()
    
    print("\n" + "=" * 60)
    print("DUPLICATE CHECK COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main() 