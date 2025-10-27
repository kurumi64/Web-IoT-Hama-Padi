#!/usr/bin/env python
"""
Test script to simulate MQTT messages with location data
This script publishes test messages with latitude and longitude to test the dynamic map
"""

import os
import sys
import django
import time
import json
import random

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from dashboard.models import SensorData
from django.utils import timezone
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_location_data():
    """Create test sensor data with location information"""
    
    # Test locations around Indonesia (you can modify these coordinates)
    test_locations = [
        {"lat": -6.2088, "lng": 106.8456, "name": "Jakarta"},
        {"lat": -7.7971, "lng": 110.3708, "name": "Yogyakarta"},
        {"lat": -6.9175, "lng": 107.6191, "name": "Bandung"},
        {"lat": -7.2575, "lng": 112.7521, "name": "Surabaya"},
        {"lat": -3.1190, "lng": 104.8447, "name": "Palembang"},
    ]
    
    # Select a random location
    location = random.choice(test_locations)
    
    # Create test sensor data
    sensor_data = SensorData(
        temperature=random.uniform(20, 35),
        humidity=random.uniform(40, 80),
        rainfall=random.uniform(0, 50),
        thunder=random.randint(0, 1),
        pest_count=random.randint(0, 10),
        battery_level=random.uniform(20, 100),
        cpu_usage=random.uniform(5, 30),
        status='Online',
        latitude=location["lat"],
        longitude=location["lng"]
    )
    
    sensor_data.save()
    logger.info(f"Created test data for {location['name']}: Lat={location['lat']}, Lng={location['lng']}")
    return sensor_data

def simulate_mqtt_messages():
    """Simulate MQTT messages with location data"""
    logger.info("Starting MQTT location simulation...")
    
    try:
        while True:
            # Create test data
            sensor_data = create_test_location_data()
            
            # Display the created data
            print(f"\n📍 New Location Data:")
            print(f"   Location: {sensor_data.latitude}, {sensor_data.longitude}")
            print(f"   Temperature: {sensor_data.temperature:.1f}°C")
            print(f"   Humidity: {sensor_data.humidity:.1f}%")
            print(f"   Pest Count: {sensor_data.pest_count}")
            print(f"   Timestamp: {sensor_data.timestamp}")
            print(f"   Status: {sensor_data.status}")
            
            # Wait for 10 seconds before next message
            print("⏳ Waiting 10 seconds for next message...")
            time.sleep(10)
            
    except KeyboardInterrupt:
        logger.info("Simulation stopped by user")
    except Exception as e:
        logger.error(f"Error during simulation: {e}")

def show_latest_location():
    """Show the latest location data in the database"""
    latest_location = SensorData.objects.filter(
        latitude__isnull=False, 
        longitude__isnull=False
    ).first()
    
    if latest_location:
        print(f"\n📍 Latest Location in Database:")
        print(f"   Latitude: {latest_location.latitude}")
        print(f"   Longitude: {latest_location.longitude}")
        print(f"   Timestamp: {latest_location.timestamp}")
        print(f"   Status: {latest_location.status}")
    else:
        print("No location data found in database")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test MQTT location functionality')
    parser.add_argument('--show', action='store_true', help='Show latest location data')
    parser.add_argument('--simulate', action='store_true', help='Simulate MQTT messages with location')
    
    args = parser.parse_args()
    
    if args.show:
        show_latest_location()
    elif args.simulate:
        simulate_mqtt_messages()
    else:
        print("Usage:")
        print("  python test_location_mqtt.py --show     # Show latest location data")
        print("  python test_location_mqtt.py --simulate # Simulate MQTT messages with location")
        print("\nExample MQTT message format:")
        print(json.dumps({
            "temperature": 25.5,
            "humidity": 60.0,
            "rainfall": 0.0,
            "thunder": 0,
            "pest_count": 5,
            "battery_level": 85,
            "cpu_usage": 15.2,
            "status": "Online",
            "latitude": -6.2088,
            "longitude": 106.8456
        }, indent=2)) 