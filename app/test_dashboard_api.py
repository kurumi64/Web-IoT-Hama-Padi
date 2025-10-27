#!/usr/bin/env python3
"""
Test script to verify dashboard API endpoints are working correctly
"""

import requests
import json
import time

def test_api_endpoints():
    """Test all dashboard API endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing Dashboard API Endpoints")
    print("=" * 50)
    
    # Test latest data endpoint
    print("\n1. Testing /api/latest-data/")
    try:
        response = requests.get(f"{base_url}/api/latest-data/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Latest Data API working:")
            print(f"   Temperature: {data.get('temperature')}°C")
            print(f"   Humidity: {data.get('humidity')}%")
            print(f"   Rainfall: {data.get('rainfall')}mm")
            print(f"   Thunder: {data.get('thunder')}")
            print(f"   Pest Count: {data.get('pest_count')}")
            print(f"   Battery: {data.get('battery_level')}%")
            print(f"   Status: {data.get('status')}")
            print(f"   Timestamp: {data.get('timestamp')}")
            print(f"   Location: {data.get('latitude')}, {data.get('longitude')}")
        else:
            print(f"❌ Latest Data API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Latest Data API error: {e}")
    
    # Test system data endpoint
    print("\n2. Testing /api/system-data/")
    try:
        response = requests.get(f"{base_url}/api/system-data/")
        if response.status_code == 200:
            data = response.json()
            print("✅ System Data API working:")
            print(f"   CPU: {data.get('cpu_percent')}%")
            print(f"   RAM: {data.get('ram_percent')}%")
            print(f"   Storage: {data.get('storage_percent')}%")
            print(f"   CPU Temp: {data.get('cpu_temp')}°C")
            print(f"   Timestamp: {data.get('timestamp')}")
        else:
            print(f"❌ System Data API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ System Data API error: {e}")
    
    # Test location data endpoint
    print("\n3. Testing /api/location-data/")
    try:
        response = requests.get(f"{base_url}/api/location-data/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Location Data API working:")
            print(f"   Latitude: {data.get('latitude')}")
            print(f"   Longitude: {data.get('longitude')}")
            print(f"   Timestamp: {data.get('timestamp')}")
        else:
            print(f"❌ Location Data API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Location Data API error: {e}")
    


def test_real_time_updates():
    """Test if data is updating in real-time"""
    print("\n" + "=" * 50)
    print("Testing Real-time Updates")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Get initial data
    try:
        response = requests.get(f"{base_url}/api/latest-data/")
        if response.status_code == 200:
            initial_data = response.json()
            print(f"Initial data timestamp: {initial_data.get('timestamp')}")
            
            # Wait and check again
            print("Waiting 10 seconds for new data...")
            time.sleep(10)
            
            response = requests.get(f"{base_url}/api/latest-data/")
            if response.status_code == 200:
                new_data = response.json()
                print(f"New data timestamp: {new_data.get('timestamp')}")
                
                if new_data.get('timestamp') != initial_data.get('timestamp'):
                    print("✅ Data is updating in real-time!")
                else:
                    print("⚠️  Data timestamp hasn't changed (no new MQTT data)")
            else:
                print("❌ Failed to get new data")
        else:
            print("❌ Failed to get initial data")
    except Exception as e:
        print(f"❌ Real-time test error: {e}")

if __name__ == "__main__":
    test_api_endpoints()
    test_real_time_updates() 