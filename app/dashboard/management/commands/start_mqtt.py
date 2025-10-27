from django.core.management.base import BaseCommand
from dashboard.mqtt_client import start_mqtt_client, stop_mqtt_client
import signal
import sys

class Command(BaseCommand):
    help = 'Start MQTT client to receive sensor data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting MQTT client...'))
        
        # Start MQTT client
        mqtt_client = start_mqtt_client()
        
        # Handle graceful shutdown
        def signal_handler(sig, frame):
            self.stdout.write(self.style.WARNING('Shutting down MQTT client...'))
            stop_mqtt_client()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # Keep the command running
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Shutting down MQTT client...'))
            stop_mqtt_client() 