#!/usr/bin/env python
"""
Test script to verify MQTT client connection and functionality
Run this script to test if the MQTT client can connect and receive messages
"""

import os
import sys
import django
import time

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from dashboard.mqtt_client import start_mqtt_client, stop_mqtt_client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_mqtt_connection():
    """Test MQTT connection and functionality"""
    logger.info("Starting MQTT connection test...")
    
    try:
        # Start MQTT client
        mqtt_client = start_mqtt_client()
        
        # Wait for connection
        time.sleep(5)
        
        if mqtt_client and mqtt_client.is_connected:
            logger.info("✅ MQTT client connected successfully!")
            logger.info(f"Connected to broker: {mqtt_client.broker}:{mqtt_client.port}")
            logger.info(f"Subscribed to topic: {mqtt_client.topic}")
            
            # Keep running for a while to test message reception
            logger.info("Waiting for messages (press Ctrl+C to stop)...")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Stopping MQTT client...")
                stop_mqtt_client()
                logger.info("✅ MQTT client stopped successfully!")
        else:
            logger.error("❌ MQTT client failed to connect")
            
    except Exception as e:
        logger.error(f"❌ Error during MQTT test: {e}")
        stop_mqtt_client()

if __name__ == "__main__":
    test_mqtt_connection() 