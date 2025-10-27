# MQTT Auto-Start Configuration

This Django application is configured to automatically start the MQTT client when you run the development server.

## How It Works

The MQTT client automatically starts when you run:
```bash
python manage.py runserver
```

### Auto-Start Implementation

1. **Apps Configuration** (`dashboard/apps.py`):
   - The `DashboardConfig.ready()` method is called when Django starts
   - It checks if `runserver` is in the command line arguments
   - Starts the MQTT client in a separate daemon thread
   - Includes a 3-second delay to ensure Django is fully loaded

2. **MQTT Client** (`dashboard/mqtt_client.py`):
   - Connects to MQTT broker at `88.222.241.209:1883`
   - Subscribes to topic `alat/sensor`
   - Automatically saves received sensor data to the database
   - Includes comprehensive logging

3. **Logging Configuration** (`app/settings.py`):
   - Configured to show MQTT client logs in the console
   - Logs connection status, received messages, and errors

## Dynamic Map Feature

The application now includes a dynamic map that displays the device location based on latitude and longitude data received from MQTT messages.

### Map Features:
- **Real-time Updates**: Map updates automatically when new location data is received
- **Interactive**: Click on markers to see detailed information
- **Responsive**: Works on different screen sizes
- **Fallback**: Shows a placeholder when no location data is available

### Location Data Storage:
- Latitude and longitude are stored in the `SensorData` model
- Location data is automatically saved when received via MQTT
- Map updates every 10 seconds with the latest location

## Testing the MQTT Connection

### Method 1: Using the Test Script
```bash
cd system-dashboard/app
python test_mqtt_connection.py
```

### Method 2: Using Django Management Command
```bash
cd system-dashboard/app
python manage.py start_mqtt
```

### Method 3: Test Location Functionality
```bash
cd system-dashboard/app
# Show latest location data
python test_location_mqtt.py --show

# Simulate MQTT messages with location data
python test_location_mqtt.py --simulate
```

### Method 4: Check Logs During Runserver
When you run `python manage.py runserver`, you should see logs like:
```
INFO - dashboard.apps - MQTT client startup thread initiated
INFO - dashboard.mqtt_client - Initializing MQTT client
INFO - dashboard.mqtt_client - Connecting to MQTT broker: 88.222.241.209:1883
INFO - dashboard.mqtt_client - Connected to MQTT broker successfully
INFO - dashboard.mqtt_client - Subscribed to topic: alat/sensor
```

## Configuration

### MQTT Broker Settings
Edit `dashboard/mqtt_client.py` to change:
- **Broker**: `self.broker = "88.222.241.209"`
- **Port**: `self.port = 1883`
- **Topic**: `self.topic = "alat/sensor"`
- **Authentication**: Set `self.username` and `self.password` if needed

### Expected Message Format
The MQTT client expects JSON messages in this format:
```json
{
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
}
```

### Map Configuration
The map uses OpenStreetMap tiles and is configured with:
- **Default Location**: Jakarta, Indonesia (-6.2088, 106.8456)
- **Update Interval**: 10 seconds for location data
- **Zoom Level**: 15 for detailed view when location is available
- **Marker Popup**: Shows coordinates and timestamp

## API Endpoints

### Latest Data
- **URL**: `/api/latest-data/`
- **Method**: GET
- **Response**: JSON with all sensor data including location

### Location Data
- **URL**: `/api/location-data/`
- **Method**: GET
- **Response**: JSON with latest location coordinates

## Troubleshooting

### MQTT Client Not Starting
1. Check if you're running `runserver` command
2. Look for error messages in the console
3. Verify MQTT broker is accessible
4. Check firewall settings

### Connection Issues
1. Verify broker IP and port are correct
2. Check if broker requires authentication
3. Ensure network connectivity to the broker
4. Check broker logs for connection attempts

### No Messages Received
1. Verify the topic name matches your sensor device
2. Check if messages are being published to the correct topic
3. Use the test script to verify connection
4. Check broker logs for message delivery

### Map Not Updating
1. Verify location data is being received via MQTT
2. Check browser console for JavaScript errors
3. Ensure latitude and longitude are valid numbers
4. Test with the location simulation script

## Manual Control

If you need to manually control the MQTT client:

```python
from dashboard.mqtt_client import start_mqtt_client, stop_mqtt_client

# Start manually
mqtt_client = start_mqtt_client()

# Stop manually
stop_mqtt_client()
```

## Production Deployment

For production, consider:
1. Using a process manager like Supervisor or systemd
2. Implementing automatic reconnection on disconnection
3. Adding message queuing for reliability
4. Using SSL/TLS for secure connections
5. Implementing proper error handling and monitoring
6. Using a CDN for map tiles to improve performance
7. Implementing location history tracking
8. Adding geofencing capabilities 