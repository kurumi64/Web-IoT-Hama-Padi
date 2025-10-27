#!/usr/bin/env python
"""
Test script to verify the pest data synchronization fix
"""

import os
import sys
import django
import json
import time

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from dashboard.models import SensorData, DetectionData
from dashboard.mqtt_client import MQTTClient
from django.utils import timezone

def test_sync_fix():
    """Test that detection data properly updates sensor data pest_count"""
    print("🧪 Testing pest data synchronization fix...")
    
    # Get current data
    latest_sensor = SensorData.objects.first()
    latest_detection = DetectionData.objects.first()
    
    print(f"📊 Before test:")
    print(f"   SensorData pest_count: {latest_sensor.pest_count if latest_sensor else 'No data'}")
    print(f"   DetectionData total_detections: {latest_detection.total_detections if latest_detection else 'No data'}")
    
    # Create test detection data
    test_detection_data = {
        "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "detection",
        "total_detections": 42,  # Test value
        "class_counts": {
            "wereng": 25,
            "ulat": 17
        },
        "detection_details": [
            {
                "class": "wereng",
                "confidence": 0.85,
                "bbox": [100, 100, 200, 200]
            }
        ],
        "latitude": -6.2088,
        "longitude": 106.8456,
        "status": "Completed"
    }
    
    print(f"\n📡 Sending test detection data: {test_detection_data['total_detections']} pests")
    
    # Simulate MQTT message processing
    mqtt_client = MQTTClient()
    mqtt_client.save_detection_data(test_detection_data)
    
    # Wait a moment for processing
    time.sleep(1)
    
    # Check if sensor data was updated
    updated_sensor = SensorData.objects.first()
    updated_detection = DetectionData.objects.first()
    
    print(f"\n📊 After test:")
    print(f"   SensorData pest_count: {updated_sensor.pest_count if updated_sensor else 'No data'}")
    print(f"   DetectionData total_detections: {updated_detection.total_detections if updated_detection else 'No data'}")
    
    # Verify synchronization
    if updated_sensor and updated_detection:
        if updated_sensor.pest_count == updated_detection.total_detections:
            print("✅ SUCCESS: Pest data is now synchronized!")
            print(f"   Both show: {updated_sensor.pest_count} pests")
        else:
            print("❌ FAILED: Pest data is still not synchronized")
            print(f"   SensorData: {updated_sensor.pest_count}")
            print(f"   DetectionData: {updated_detection.total_detections}")
    else:
        print("❌ FAILED: Missing data after test")

if __name__ == "__main__":
    test_sync_fix() 