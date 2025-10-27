# type: ignore
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import logging
import json

logger = logging.getLogger(__name__)

class SensorData(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    rainfall = models.FloatField(null=True, blank=True)
    thunder = models.IntegerField(default=0)
    pest_count = models.IntegerField(default=0)
    pest_types = models.JSONField(default=dict, help_text="Count of each pest type detected")
    cpu_usage = models.FloatField(null=True, blank=True, help_text="CPU usage percentage")
    status = models.CharField(max_length=20, default='Online')
    latitude = models.FloatField(null=True, blank=True, help_text="Latitude coordinate")
    longitude = models.FloatField(null=True, blank=True, help_text="Longitude coordinate")
    
    class Meta:
        ordering = ['-timestamp']
        # Add unique constraint to prevent duplicates within a short time window
        unique_together = ['timestamp', 'temperature', 'humidity', 'rainfall', 'thunder', 'pest_count']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Sensor Data - {self.timestamp}"
    
    @property
    def has_location(self):
        """Check if the sensor data has valid location coordinates"""
        return self.latitude is not None and self.longitude is not None
    
    def clean(self):
        """Validate the model data"""
        super().clean()
        
        # Validate temperature range
        if self.temperature is not None:
            if self.temperature < -50 or self.temperature > 100:
                raise ValidationError('Temperature must be between -50 and 100 degrees Celsius')
        
        # Validate humidity range
        if self.humidity is not None:
            if self.humidity < 0 or self.humidity > 100:
                raise ValidationError('Humidity must be between 0 and 100 percent')
        
        # Validate pest_types is a dictionary
        if self.pest_types is not None and not isinstance(self.pest_types, dict):
            raise ValidationError('Pest types must be a dictionary')
        
        # Validate coordinates if provided
        if self.latitude is not None:
            if self.latitude < -90 or self.latitude > 90:
                raise ValidationError('Latitude must be between -90 and 90 degrees')
        
        if self.longitude is not None:
            if self.longitude < -180 or self.longitude > 180:
                raise ValidationError('Longitude must be between -180 and 180 degrees')
    
    def save(self, *args, **kwargs):
        """Override save method to prevent duplicates and validate data"""
        # Clean and validate data
        self.clean()
        
        # Check for recent duplicate entries (within 30 seconds)
        from datetime import timedelta
        recent_window = self.timestamp + timedelta(seconds=30)
        recent_start = self.timestamp - timedelta(seconds=30)
        
        # Look for similar entries in the recent time window
        similar_entries = SensorData.objects.filter(
            timestamp__range=(recent_start, recent_window),
            temperature=self.temperature,
            humidity=self.humidity,
            rainfall=self.rainfall,
            thunder=self.thunder,
            pest_count=self.pest_count
        ).exclude(id=self.id)  # Exclude current record if updating
        
        if similar_entries.exists():
            logger.warning(f"Duplicate sensor data detected for timestamp {self.timestamp}. Skipping save.")
            # Don't save duplicate data
            return
        
        # Save the data
        super().save(*args, **kwargs)
        logger.info(f"Saved new sensor data: {self}")
    
    @classmethod
    def get_latest_unique_data(cls, limit=10):
        """Get the latest unique sensor data entries"""
        return cls.objects.all().order_by('-timestamp')[:limit]
    
    @classmethod
    def cleanup_duplicates(cls):
        """Clean up duplicate entries in the database"""
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Remove exact duplicates, keeping the first occurrence
            cursor.execute("""
                DELETE FROM dashboard_sensordata 
                WHERE id NOT IN (
                    SELECT MIN(id) 
                    FROM dashboard_sensordata 
                    GROUP BY timestamp, temperature, humidity, rainfall, thunder, pest_count
                )
            """)
        
        deleted_count = cursor.rowcount
        logger.info(f"Cleaned up {deleted_count} duplicate sensor data entries")
        return deleted_count

class SystemData(models.Model):
    """Model to store system monitoring data (CPU, RAM, Storage)"""
    timestamp = models.DateTimeField(default=timezone.now)
    cpu_percent = models.FloatField(null=True, blank=True, help_text="CPU usage percentage")
    ram_percent = models.FloatField(null=True, blank=True, help_text="RAM usage percentage")
    ram_used_gb = models.FloatField(null=True, blank=True, help_text="RAM used in GB")
    ram_total_gb = models.FloatField(null=True, blank=True, help_text="Total RAM in GB")
    storage_percent = models.FloatField(null=True, blank=True, help_text="Storage usage percentage")
    storage_used_gb = models.FloatField(null=True, blank=True, help_text="Storage used in GB")
    storage_total_gb = models.FloatField(null=True, blank=True, help_text="Total storage in GB")
    network_sent_mb = models.FloatField(null=True, blank=True, help_text="Network bytes sent in MB")
    network_recv_mb = models.FloatField(null=True, blank=True, help_text="Network bytes received in MB")
    load_1min = models.FloatField(null=True, blank=True, help_text="1-minute load average")
    load_5min = models.FloatField(null=True, blank=True, help_text="5-minute load average")
    load_15min = models.FloatField(null=True, blank=True, help_text="15-minute load average")
    status = models.CharField(max_length=20, default='Online')
    cpu_temp = models.FloatField(null=True, blank=True, help_text="CPU temperature in Celsius")
    battery_level = models.FloatField(null=True, blank=True, help_text="Battery level percentage")
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"System Data - {self.timestamp}"
    
    def clean(self):
        """Validate the model data"""
        super().clean()
        
        # Validate percentage fields (0-100)
        percentage_fields = ['cpu_percent', 'ram_percent', 'storage_percent']
        for field in percentage_fields:
            value = getattr(self, field)
            if value is not None:
                if value < 0 or value > 100:
                    raise ValidationError(f'{field.replace("_", " ").title()} must be between 0 and 100 percent')
        
        # Validate GB fields (positive values)
        gb_fields = ['ram_used_gb', 'ram_total_gb', 'storage_used_gb', 'storage_total_gb']
        for field in gb_fields:
            value = getattr(self, field)
            if value is not None:
                if value < 0:
                    raise ValidationError(f'{field.replace("_", " ").title()} must be a positive value')
        
        # Validate network fields (positive values)
        network_fields = ['network_sent_mb', 'network_recv_mb']
        for field in network_fields:
            value = getattr(self, field)
            if value is not None:
                if value < 0:
                    raise ValidationError(f'{field.replace("_", " ").title()} must be a positive value')
        
        # Validate load average fields (positive values)
        load_fields = ['load_1min', 'load_5min', 'load_15min']
        for field in load_fields:
            value = getattr(self, field)
            if value is not None:
                if value < 0:
                    raise ValidationError(f'{field.replace("_", " ").title()} must be a positive value')
    
    def save(self, *args, **kwargs):
        """Override save method to validate data and prevent duplicates"""
        # Clean and validate data
        self.clean()
        
        # Check for recent duplicate entries (within 30 seconds)
        from datetime import timedelta
        recent_window = self.timestamp + timedelta(seconds=30)
        recent_start = self.timestamp - timedelta(seconds=30)
        
        # Look for similar entries in the recent time window
        similar_entries = SystemData.objects.filter(
            timestamp__range=(recent_start, recent_window),
            cpu_percent=self.cpu_percent,
            ram_percent=self.ram_percent,
            storage_percent=self.storage_percent
        ).exclude(id=self.id)  # Exclude current record if updating
        
        if similar_entries.exists():
            logger.warning(f"Duplicate system data detected for timestamp {self.timestamp}. Skipping save.")
            # Don't save duplicate data
            return
        
        # Save the data
        super().save(*args, **kwargs)
        logger.info(f"Saved new system data: {self}")
    
    @classmethod
    def get_latest_data(cls):
        """Get the latest system data entry"""
        return cls.objects.first()
    
    @classmethod
    def get_recent_data(cls, hours=24):
        """Get system data for the last N hours"""
        from datetime import timedelta
        start_time = timezone.now() - timedelta(hours=hours)
        return cls.objects.filter(timestamp__gte=start_time).order_by('timestamp')


class DetectionData(models.Model):
    """Model to store pest detection results"""
    timestamp = models.DateTimeField(default=timezone.now)
    total_detections = models.IntegerField(default=0, help_text="Total number of pests detected")
    class_counts = models.JSONField(default=dict, help_text="Count of each pest class detected")
    growth_stage = models.CharField(max_length=50, default='Vegetatif', help_text="Rice paddy growth stage")
    image_path = models.CharField(max_length=255, null=True, blank=True, help_text="Path to the detection image")
    latitude = models.FloatField(null=True, blank=True, help_text="Latitude where detection occurred")
    longitude = models.FloatField(null=True, blank=True, help_text="Longitude where detection occurred")
    status = models.CharField(max_length=20, default='Completed')
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['total_detections']),
            models.Index(fields=['status']),
            models.Index(fields=['growth_stage']),
        ]
    
    def __str__(self):
        return f"Detection Data - {self.timestamp} ({self.total_detections} pests) - {self.growth_stage}"
    
    def clean(self):
        """Validate the model data"""
        super().clean()
        
        # Validate total_detections
        if self.total_detections < 0:
            raise ValidationError('Total detections must be a non-negative number')
        
        # Validate coordinates if provided
        if self.latitude is not None:
            if self.latitude < -90 or self.latitude > 90:
                raise ValidationError('Latitude must be between -90 and 90 degrees')
        
        if self.longitude is not None:
            if self.longitude < -180 or self.longitude > 180:
                raise ValidationError('Longitude must be between -180 and 180 degrees')
    
    def save(self, *args, **kwargs):
        """Override save method to validate data"""
        self.clean()
        super().save(*args, **kwargs)
        logger.info(f"Saved detection data: {self}")
    
    @classmethod
    def get_latest_detection(cls):
        """Get the latest detection data"""
        return cls.objects.first()
    
    @classmethod
    def get_detection_statistics(cls, days=7):
        """Get detection statistics for the specified number of days"""
        from datetime import timedelta
        from django.db.models import Sum, Count
        from django.db.models.functions import TruncHour, TruncDay, TruncWeek, TruncMonth
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        detections = cls.objects.filter(
            timestamp__range=(start_date, end_date)
        ).order_by('timestamp')
        
        # Calculate statistics
        total_detections = detections.count()
        total_pests = sum(d.total_detections for d in detections)
        
        # Aggregate class counts
        class_counts = {}
        for detection in detections:
            for class_name, count in detection.class_counts.items():
                class_counts[class_name] = class_counts.get(class_name, 0) + count
        
        # Time-based statistics based on period
        daily_stats = {}
        
        if days == 1:
            # For today, group by hour
            hourly_detections = detections.annotate(
                hour=TruncHour('timestamp')
            ).values('hour').annotate(
                total_detections=Count('id'),
                total_pests=Sum('total_detections')
            ).order_by('hour')
            
            for hour_data in hourly_detections:
                hour = hour_data['hour']
                if hour:
                    daily_stats[hour] = {
                        'total_detections': hour_data['total_detections'],
                        'pest_count': hour_data['total_pests'] or 0,
                        'class_counts': {}
                    }
                    
                    # Get class counts for this hour
                    hour_detections = detections.filter(
                        timestamp__hour=hour.hour,
                        timestamp__date=hour.date()
                    )
                    for detection in hour_detections:
                        for class_name, count in detection.class_counts.items():
                            daily_stats[hour]['class_counts'][class_name] = \
                                daily_stats[hour]['class_counts'].get(class_name, 0) + count
                                
        elif days <= 30:
            # For 1-30 days, group by day
            for detection in detections:
                date = detection.timestamp.date()
                if date not in daily_stats:
                    daily_stats[date] = {
                        'total_detections': 0,
                        'pest_count': 0,
                        'class_counts': {}
                    }
                
                daily_stats[date]['total_detections'] += 1
                daily_stats[date]['pest_count'] += detection.total_detections
                
                for class_name, count in detection.class_counts.items():
                    daily_stats[date]['class_counts'][class_name] = \
                        daily_stats[date]['class_counts'].get(class_name, 0) + count
                        
        elif days <= 90:
            # For 1-3 months, group by week
            weekly_detections = detections.annotate(
                week=TruncWeek('timestamp')
            ).values('week').annotate(
                total_detections=Count('id'),
                total_pests=Sum('total_detections')
            ).order_by('week')
            
            for week_data in weekly_detections:
                week = week_data['week']
                if week:
                    daily_stats[week] = {
                        'total_detections': week_data['total_detections'],
                        'pest_count': week_data['total_pests'] or 0,
                        'class_counts': {}
                    }
                    
                    # Get class counts for this week
                    week_detections = detections.filter(
                        timestamp__week=week.isocalendar()[1],
                        timestamp__year=week.year
                    )
                    for detection in week_detections:
                        for class_name, count in detection.class_counts.items():
                            daily_stats[week]['class_counts'][class_name] = \
                                daily_stats[week]['class_counts'].get(class_name, 0) + count
                                
        else:
            # For 1 year, group by month
            monthly_detections = detections.annotate(
                month=TruncMonth('timestamp')
            ).values('month').annotate(
                total_detections=Count('id'),
                total_pests=Sum('total_detections')
            ).order_by('month')
            
            for month_data in monthly_detections:
                month = month_data['month']
                if month:
                    daily_stats[month] = {
                        'total_detections': month_data['total_detections'],
                        'pest_count': month_data['total_pests'] or 0,
                        'class_counts': {}
                    }
                    
                    # Get class counts for this month
                    month_detections = detections.filter(
                        timestamp__month=month.month,
                        timestamp__year=month.year
                    )
                    for detection in month_detections:
                        for class_name, count in detection.class_counts.items():
                            daily_stats[month]['class_counts'][class_name] = \
                                daily_stats[month]['class_counts'].get(class_name, 0) + count
        
        return {
            'total_detections': total_detections,
            'total_pests': total_pests,
            'class_counts': class_counts,
            'daily_stats': daily_stats,
            'period_days': days
        }
