# type: ignore
import paho.mqtt.client as mqtt
import json
import threading
import time
import logging
from django.utils import timezone
from .models import SensorData, SystemData, DetectionData

logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # MQTT Configuration
        self.broker = "localhost"  # Change to your MQTT broker address
        self.port = 1883
        self.topic = "alat/data"  # Change to your MQTT topic
        self.system_topic = "alat/data/system"  # New system monitoring topic
        self.detection_topic = "alat/data/detection"  # Pest detection topic
        self.cpu_topic = "alat/data/cpu"  # New CPU monitoring topic
        self.ram_topic = "alat/data/ram"  # New RAM monitoring topic
        self.storage_topic = "alat/data/storage"  # New storage monitoring topic
        self.username = "ahp123"  # MQTT broker username
        self.password = "kiki"  # MQTT broker password
        
        self.is_connected = False
        self.reconnect_delay = 5  # seconds
        self.max_reconnect_delay = 300  # maximum 5 minutes
        self.current_reconnect_delay = self.reconnect_delay
        self._lock = threading.Lock()  # Thread safety lock
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT broker successfully")
            self.is_connected = True
            self.current_reconnect_delay = self.reconnect_delay  # Reset reconnect delay
            
            # Subscribe to all topics
            client.subscribe(self.topic)
            client.subscribe(self.system_topic)
            client.subscribe(self.detection_topic)
            client.subscribe(self.cpu_topic)
            client.subscribe(self.ram_topic)
            client.subscribe(self.storage_topic)
            logger.info(f"Subscribed to topics: {self.topic}, {self.system_topic}, {self.detection_topic}, {self.cpu_topic}, {self.ram_topic}, {self.storage_topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker with code: {rc}")
            self.is_connected = False
    
    def on_message(self, client, userdata, msg):
        try:
            # Parse the JSON message
            payload = json.loads(msg.payload.decode())
            logger.info(f"Received message on topic {msg.topic}: {payload}")
            
            # Route message based on topic
            if msg.topic == self.topic:
                # Handle sensor data
                self.save_sensor_data(payload)
            elif msg.topic == self.detection_topic:
                # Handle detection data
                self.save_detection_data(payload)
            elif msg.topic == self.system_topic:
                # Handle complete system data
                self.save_system_data(payload)
            elif msg.topic == self.cpu_topic:
                # Handle CPU-only data
                self.save_cpu_data(payload)
            elif msg.topic == self.ram_topic:
                # Handle RAM-only data
                self.save_ram_data(payload)
            elif msg.topic == self.storage_topic:
                # Handle storage-only data
                self.save_storage_data(payload)
            
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def on_disconnect(self, client, userdata, rc):
        logger.warning(f"Disconnected from MQTT broker with code: {rc}")
        self.is_connected = False
        
        # Attempt to reconnect if not manually disconnected
        if rc != 0:
            self._schedule_reconnect()
    
    def _schedule_reconnect(self):
        """Schedule a reconnection attempt with improved error handling"""
        def reconnect():
            try:
                time.sleep(self.current_reconnect_delay)
                logger.info(f"Attempting to reconnect to MQTT broker...")
                
                # Check if already connected
                if self.is_connected:
                    logger.info("Already connected, skipping reconnection")
                    return
                    
                self.connect()
            except Exception as e:
                logger.error(f"Reconnection failed: {e}")
                # Increase reconnect delay exponentially
                self.current_reconnect_delay = min(self.current_reconnect_delay * 2, self.max_reconnect_delay)
                
                # Only schedule another reconnection if not manually disconnected
                if not self.is_connected:
                    self._schedule_reconnect()
        
        # Start reconnection in a separate thread
        reconnect_thread = threading.Thread(target=reconnect, daemon=True)
        reconnect_thread.start()
    
    def save_sensor_data(self, data):
        try:
            # Validate required data
            if not isinstance(data, dict):
                logger.error("Invalid data format: expected dictionary")
                return
                
            # Create sensor data with validation
            sensor_data = SensorData(
                temperature=data.get('temperature'),
                humidity=data.get('humidity'),
                rainfall=data.get('rainfall'),
                thunder=data.get('thunder', 0),
                pest_count=data.get('pest_count', 0),
                cpu_usage=data.get('cpu_usage'),
                status=data.get('status', 'Online'),
                latitude=data.get('latitude'),
                longitude=data.get('longitude')
            )
            sensor_data.save()
            logger.info(f"Saved sensor data: {sensor_data}")
            
            # Save battery_level to SystemData instead, if needed
            if data.get('battery_level') is not None:
                SystemData.objects.create(
                    battery_level=data.get('battery_level'),
                    status=data.get('status', 'Online'),
                    timestamp=timezone.now()
                )
        except Exception as e:
            logger.error(f"Error saving sensor data: {e}")
            # Log the problematic data for debugging
            logger.error(f"Problematic data: {data}")
    
    def save_detection_data(self, data):
        """Save pest detection data"""
        try:
            # Validate required data
            if not isinstance(data, dict):
                logger.error("Invalid detection data format: expected dictionary")
                return
                
            detection_data = DetectionData(
                total_detections=data.get('total_detections', 0),
                class_counts=data.get('class_counts', {}),
                detection_details=data.get('detection_details', []),
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                status=data.get('status', 'Completed')
            )
            detection_data.save()
            logger.info(f"Saved detection data: {detection_data}")
            
            # Also update the pest_count in the latest SensorData record
            try:
                # Use a more targeted approach to avoid deadlocks
                latest_sensor_data = SensorData.objects.order_by('-timestamp').first()
                if latest_sensor_data:
                    # Only update if the pest count has changed
                    if latest_sensor_data.pest_count != data.get('total_detections', 0):
                        latest_sensor_data.pest_count = data.get('total_detections', 0)
                        latest_sensor_data.save()
                        logger.info(f"Updated pest_count in latest sensor data: {latest_sensor_data.pest_count}")
            except Exception as e:
                logger.error(f"Error updating pest_count in sensor data: {e}")
                
        except Exception as e:
            logger.error(f"Error saving detection data: {e}")
            logger.error(f"Problematic detection data: {data}")
    
    def save_system_data(self, data):
        """Save complete system monitoring data"""
        try:
            # Validate required data
            if not isinstance(data, dict):
                logger.error("Invalid system data format: expected dictionary")
                return
                
            system_data = SystemData(
                cpu_percent=data.get('cpu_percent'),
                ram_percent=data.get('ram_percent'),
                ram_used_gb=data.get('ram_used_gb'),
                ram_total_gb=data.get('ram_total_gb'),
                storage_percent=data.get('storage_percent'),
                storage_used_gb=data.get('storage_used_gb'),
                storage_total_gb=data.get('storage_total_gb'),
                network_sent_mb=data.get('network_sent_mb'),
                network_recv_mb=data.get('network_recv_mb'),
                load_1min=data.get('load_1min'),
                load_5min=data.get('load_5min'),
                load_15min=data.get('load_15min'),
                status=data.get('status', 'Online'),
                cpu_temp=data.get('cpu_temp'),
                battery_level=data.get('battery_level'),
            )
            system_data.save()
            logger.info(f"Saved system data: {system_data}")
        except Exception as e:
            logger.error(f"Error saving system data: {e}")
            logger.error(f"Problematic system data: {data}")
    
    def save_cpu_data(self, data):
        """Save CPU-only monitoring data"""
        try:
            # Validate required data
            if not isinstance(data, dict):
                logger.error("Invalid CPU data format: expected dictionary")
                return
                
            with self._lock:  # Thread safety
                # Get latest system data or create new one
                latest_system = SystemData.objects.order_by('-timestamp').first()
                if latest_system and (timezone.now() - latest_system.timestamp).seconds < 60:
                    # Update existing record if it's recent (within 1 minute)
                    latest_system.cpu_percent = data.get('cpu_percent')
                    latest_system.status = data.get('status', 'Online')
                    if data.get('cpu_temp') is not None:
                        latest_system.cpu_temp = data.get('cpu_temp')
                    latest_system.save()
                    logger.info(f"Updated CPU data: {latest_system.cpu_percent}%")
                else:
                    # Create new record with only CPU data
                    system_data = SystemData(
                        cpu_percent=data.get('cpu_percent'),
                        status=data.get('status', 'Online'),
                        cpu_temp=data.get('cpu_temp')
                    )
                    system_data.save()
                    logger.info(f"Created new system data with CPU: {system_data.cpu_percent}%")
        except Exception as e:
            logger.error(f"Error saving CPU data: {e}")
            logger.error(f"Problematic CPU data: {data}")
    
    def save_ram_data(self, data):
        """Save RAM-only monitoring data"""
        try:
            # Validate required data
            if not isinstance(data, dict):
                logger.error("Invalid RAM data format: expected dictionary")
                return
                
            with self._lock:  # Thread safety
                # Get latest system data or create new one
                latest_system = SystemData.objects.order_by('-timestamp').first()
                if latest_system and (timezone.now() - latest_system.timestamp).seconds < 60:
                    # Update existing record if it's recent (within 1 minute)
                    latest_system.ram_percent = data.get('ram_percent')
                    latest_system.ram_used_gb = data.get('ram_used_gb')
                    latest_system.ram_total_gb = data.get('ram_total_gb')
                    latest_system.status = data.get('status', 'Online')
                    latest_system.save()
                    logger.info(f"Updated RAM data: {latest_system.ram_percent}%")
                else:
                    # Create new record with only RAM data
                    system_data = SystemData(
                        ram_percent=data.get('ram_percent'),
                        ram_used_gb=data.get('ram_used_gb'),
                        ram_total_gb=data.get('ram_total_gb'),
                        status=data.get('status', 'Online')
                    )
                    system_data.save()
                    logger.info(f"Created new system data with RAM: {system_data.ram_percent}%")
        except Exception as e:
            logger.error(f"Error saving RAM data: {e}")
            logger.error(f"Problematic RAM data: {data}")
    
    def save_storage_data(self, data):
        """Save storage-only monitoring data"""
        try:
            # Validate required data
            if not isinstance(data, dict):
                logger.error("Invalid storage data format: expected dictionary")
                return
                
            with self._lock:  # Thread safety
                # Get latest system data or create new one
                latest_system = SystemData.objects.order_by('-timestamp').first()
                if latest_system and (timezone.now() - latest_system.timestamp).seconds < 60:
                    # Update existing record if it's recent (within 1 minute)
                    latest_system.storage_percent = data.get('storage_percent')
                    latest_system.storage_used_gb = data.get('storage_used_gb')
                    latest_system.storage_total_gb = data.get('storage_total_gb')
                    latest_system.status = data.get('status', 'Online')
                    latest_system.save()
                    logger.info(f"Updated storage data: {latest_system.storage_percent}%")
                else:
                    # Create new record with only storage data
                    system_data = SystemData(
                        storage_percent=data.get('storage_percent'),
                        storage_used_gb=data.get('storage_used_gb'),
                        storage_total_gb=data.get('storage_total_gb'),
                        status=data.get('status', 'Online')
                    )
                    system_data.save()
                    logger.info(f"Created new system data with storage: {system_data.storage_percent}%")
        except Exception as e:
            logger.error(f"Error saving storage data: {e}")
            logger.error(f"Problematic storage data: {data}")
    
    def connect(self):
        try:
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
            
            logger.info(f"Connecting to MQTT broker: {self.broker}:{self.port}")
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Error connecting to MQTT broker: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from MQTT broker with proper cleanup"""
        try:
            logger.info("Disconnecting from MQTT broker")
            self.is_connected = False
            
            # Stop the network loop first
            if hasattr(self.client, '_thread') and self.client._thread:
                self.client.loop_stop()
            
            # Disconnect from broker
            self.client.disconnect()
            
            # Reset reconnection delay
            self.current_reconnect_delay = self.reconnect_delay
            
            logger.info("Successfully disconnected from MQTT broker")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
        finally:
            self.is_connected = False
    
    def publish(self, topic, message):
        """Publish message to MQTT topic with error handling"""
        if not self.is_connected:
            logger.warning("Cannot publish: MQTT client not connected")
            return False
        
        try:
            if not topic or not message:
                logger.error("Invalid topic or message for publishing")
                return False
                
            result = self.client.publish(topic, message)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published message to topic {topic}")
                return True
            else:
                logger.error(f"Failed to publish message to topic {topic}: {result.rc}")
                return False
        except Exception as e:
            logger.error(f"Error publishing message to topic {topic}: {e}")
            return False
    
    def check_connection_status(self):
        """Check if client is connected to MQTT broker"""
        return self.is_connected and self.client.is_connected()
    
    def get_connection_info(self):
        """Get connection information"""
        return {
            'connected': self.is_connected,
            'broker': self.broker,
            'port': self.port,
            'topics': [self.topic, self.system_topic, self.detection_topic, 
                      self.cpu_topic, self.ram_topic, self.storage_topic]
        }

# Global MQTT client instance with thread safety
_mqtt_client = None
_mqtt_lock = threading.Lock()

def start_mqtt_client():
    """Start MQTT client with error handling"""
    global _mqtt_client
    with _mqtt_lock:
        if _mqtt_client is None:
            try:
                logger.info("Initializing MQTT client")
                _mqtt_client = MQTTClient()
                _mqtt_client.connect()
                return _mqtt_client
            except Exception as e:
                logger.error(f"Failed to start MQTT client: {e}")
                _mqtt_client = None
                return None
        else:
            logger.info("MQTT client already running")
            return _mqtt_client

def stop_mqtt_client():
    """Stop MQTT client with proper cleanup"""
    global _mqtt_client
    with _mqtt_lock:
        if _mqtt_client:
            try:
                logger.info("Stopping MQTT client")
                _mqtt_client.disconnect()
            except Exception as e:
                logger.error(f"Error stopping MQTT client: {e}")
            finally:
                _mqtt_client = None

def get_mqtt_client():
    """Get the current MQTT client instance"""
    global _mqtt_client
    with _mqtt_lock:
        return _mqtt_client 
