from django.apps import AppConfig
import threading
import time
import logging

logger = logging.getLogger(__name__)

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'
    
    def ready(self):
        # Import here to avoid circular imports
        from . import signals  # Register signals
        
        # Start MQTT client in a separate thread to avoid blocking
        def start_mqtt():
            try:
                # Small delay to ensure Django is fully loaded
                time.sleep(3)
                from .mqtt_client import start_mqtt_client
                mqtt_client = start_mqtt_client()
                logger.info("MQTT client started successfully")
            except Exception as e:
                logger.error(f"Error starting MQTT client: {e}")
        
        # Only start MQTT client if we're running the server (not during migrations, etc.)
        import sys
        if 'runserver' in sys.argv:
            # Check if we're not in a subprocess (like during migrations)
            if not any(arg in sys.argv for arg in ['migrate', 'makemigrations', 'collectstatic', 'test']):
                mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
                mqtt_thread.start()
                logger.info("MQTT client startup thread initiated")
