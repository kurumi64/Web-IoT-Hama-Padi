#!/usr/bin/env python3
"""
Test script to simulate pest detection data for testing the dashboard
"""

import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime, timedelta
import random

# MQTT Configuration
MQTT_CONFIG = {
    "broker": "88.222.241.209",
    "port": 1883,
    "username": "ahp123",
    "password": "kiki",
    "topic": "alat/data"
}

def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    if rc == 0:
        print("✅ Connected to MQTT broker")
        print(f"📡 Publishing to: {MQTT_CONFIG['topic']}/detection")
    else:
        print(f"❌ Connection failed with code: {rc}")

def on_publish(client, userdata, mid):
    """Callback when message is published"""
    print(f"✅ Message published (ID: {mid})")

def simulate_detection_data():
    """Simulate pest detection data"""
    print("🔄 Starting pest detection simulation...")
    
    try:
        # Create MQTT client
        client = mqtt.Client(protocol=mqtt.MQTTv311)
        
        # Set credentials
        if MQTT_CONFIG['username'] and MQTT_CONFIG['password']:
            client.username_pw_set(MQTT_CONFIG['username'], MQTT_CONFIG['password'])
        
        # Set callbacks
        client.on_connect = on_connect
        client.on_publish = on_publish
        
        # Connect to broker
        client.connect(MQTT_CONFIG['broker'], MQTT_CONFIG['port'], 60)
        client.loop_start()
        
        # Wait for connection
        time.sleep(2)
        
        # Simulate detection data
        pest_classes = ['wereng', 'ulat', 'kutu', 'belalang', 'kumbang']
        
        for i in range(5):  # Send 5 detection messages
            # Generate random detection data
            total_detections = random.randint(1, 15)
            class_counts = {}
            
            # Generate random counts for each pest class
            for pest_class in random.sample(pest_classes, random.randint(1, 3)):
                class_counts[pest_class] = random.randint(1, 8)
            
            # Generate detection details
            detection_details = []
            for pest_class, count in class_counts.items():
                for j in range(count):
                    detection_details.append({
                        'class': pest_class,
                        'confidence': round(random.uniform(0.6, 0.95), 2),
                        'bbox': [
                            random.randint(100, 500),
                            random.randint(100, 500),
                            random.randint(600, 800),
                            random.randint(600, 800)
                        ]
                    })
            
            # Create detection data
            detection_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": "detection",
                "total_detections": total_detections,
                "class_counts": class_counts,
                "detection_details": detection_details,
                "latitude": -6.2088 + random.uniform(-0.01, 0.01),
                "longitude": 106.8456 + random.uniform(-0.01, 0.01),
                "status": "Completed"
            }
            
            # Publish to detection topic
            detection_topic = f"{MQTT_CONFIG['topic']}/detection"
            client.publish(detection_topic, json.dumps(detection_data))
            
            print(f"\n🔍 Detection Data {i+1}:")
            print(f"   Total Detections: {total_detections}")
            print(f"   Class Counts: {class_counts}")
            print(f"   Location: {detection_data['latitude']:.6f}, {detection_data['longitude']:.6f}")
            
            # Wait before next message
            time.sleep(10)
        
        # Wait for messages to be processed
        time.sleep(5)
        
    except Exception as e:
        print(f"❌ Error during simulation: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        print("✅ Simulation completed")

if __name__ == "__main__":
    print("Pest Detection Data Simulator")
    print("=" * 50)
    print(f"Broker: {MQTT_CONFIG['broker']}:{MQTT_CONFIG['port']}")
    print(f"Topic: {MQTT_CONFIG['topic']}/detection")
    print("=" * 50)
    
    simulate_detection_data() 