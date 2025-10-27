#!/usr/bin/env python3
"""
Test script to send MQTT messages to verify the Django MQTT client is working
"""

import paho.mqtt.client as mqtt
import json
import time

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print(f"Failed to connect with code: {rc}")

def on_publish(client, userdata, mid):
    print(f"Message published with ID: {mid}")

# Create MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish

# Connect to broker
broker = "localhost"  # Change this to your MQTT broker address
port = 1883
topic = "sensor/data"  # Change this to match your Django MQTT topic

try:
    client.connect(broker, port, 60)
    client.loop_start()
    
    # Send test messages
    for i in range(5):
        test_data = {
            "temperature": 25.5 + i,
            "humidity": 40.2 + i * 2,
            "rainfall": 0.0,
            "thunder": i % 2,
            "pest_count": i,
            "battery_level": 85.5 - i * 2,
            "cpu_usage": 12.3 + i,
            "status": "Online"
        }
        
        message = json.dumps(test_data)
        client.publish(topic, message)
        print(f"Sent message {i+1}: {test_data}")
        time.sleep(2)
    
    # Wait a bit for messages to be processed
    time.sleep(5)
    
except Exception as e:
    print(f"Error: {e}")
finally:
    client.loop_stop()
    client.disconnect()
    print("Test completed") 