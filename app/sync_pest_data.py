#!/usr/bin/env python
"""
Script to sync pest detection data between DetectionData and SensorData models
This fixes the issue where chart shows detection data but CSV table shows 0
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from dashboard.models import SensorData, DetectionData
from django.utils import timezone
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def sync_pest_data():
    """Sync pest detection data between DetectionData and SensorData models"""
    print("🔄 Syncing pest detection data...")
    
    # Get the latest detection data
    latest_detection = DetectionData.objects.first() # type: ignore
    
    if not latest_detection:
        print("❌ No detection data found")
        return
    
    print(f"📊 Latest detection data:")
    print(f"   Total detections: {latest_detection.total_detections}")
    print(f"   Class counts: {latest_detection.class_counts}")
    print(f"   Timestamp: {latest_detection.timestamp}")
    
    # Get the latest sensor data
    latest_sensor = SensorData.objects.first() # type: ignore
    
    if not latest_sensor:
        print("❌ No sensor data found")
        return
    
    print(f"📡 Latest sensor data:")
    print(f"   Current pest_count: {latest_sensor.pest_count}")
    print(f"   Timestamp: {latest_sensor.timestamp}")
    
    # Update the pest_count in sensor data
    old_count = latest_sensor.pest_count
    latest_sensor.pest_count = latest_detection.total_detections
    latest_sensor.save()
    
    print(f"✅ Updated pest_count from {old_count} to {latest_sensor.pest_count}")
    
    # Also update any recent sensor data records (within the last hour)
    one_hour_ago = timezone.now() - timezone.timedelta(hours=1)
    recent_sensors = SensorData.objects.filter(timestamp__gte=one_hour_ago) # type: ignore
    
    updated_count = 0
    for sensor in recent_sensors:
        if sensor.pest_count != latest_detection.total_detections:
            sensor.pest_count = latest_detection.total_detections
            sensor.save()
            updated_count += 1
    
    print(f"✅ Updated {updated_count} recent sensor records")

def show_current_data():
    """Show current data in both models"""
    print("\n📋 Current data status:")
    
    # Detection data
    detection_count = DetectionData.objects.count() # type: ignore
    latest_detection = DetectionData.objects.first() # type: ignore
    
    print(f"DetectionData records: {detection_count}")
    if latest_detection:
        print(f"  Latest: {latest_detection.total_detections} pests at {latest_detection.timestamp}")
    
    # Sensor data
    sensor_count = SensorData.objects.count() # type: ignore
    latest_sensor = SensorData.objects.first() # type: ignore
    
    print(f"SensorData records: {sensor_count}")
    if latest_sensor:
        print(f"  Latest pest_count: {latest_sensor.pest_count} at {latest_sensor.timestamp}")
    
    # Check for discrepancies
    if latest_detection and latest_sensor:
        if latest_detection.total_detections != latest_sensor.pest_count:
            print(f"⚠️  DISCREPANCY: DetectionData shows {latest_detection.total_detections} but SensorData shows {latest_sensor.pest_count}")
        else:
            print("✅ Data is synchronized")

if __name__ == "__main__":
    print("🔍 Pest Data Synchronization Tool")
    print("=" * 40)
    
    show_current_data()
    
    response = input("\nDo you want to sync the data? (y/n): ")
    if response.lower() == 'y':
        sync_pest_data()
        print("\n" + "=" * 40)
        show_current_data()
    else:
        print("Operation cancelled.") 