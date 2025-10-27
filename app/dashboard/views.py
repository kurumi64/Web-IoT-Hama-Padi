# type: ignore
import logging
from django.shortcuts import render
from django.http import JsonResponse
from .models import SensorData, SystemData, DetectionData
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import csv
from io import StringIO
from django.core.paginator import Paginator
from django.db.models import Q, OuterRef, Subquery
from django.db.models import Max
import base64
import json
import os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import cv2
import numpy as np
from PIL import Image
import io

# Set up logger
logger = logging.getLogger(__name__)

def index(request):
    # Get the latest sensor data
    latest_data = SensorData.objects.first()
    
    # Get the latest system data
    latest_system_data = SystemData.get_latest_data()
    
    # Get data for the last 24 hours for charts
    yesterday = timezone.now() - timedelta(days=1)
    recent_data = SensorData.objects.filter(timestamp__gte=yesterday).order_by('timestamp')
    recent_system_data = SystemData.get_recent_data(hours=24)
    
    # Get the last 10 records for the table
    table_data = SensorData.objects.all()[:10]
    system_table_data = SystemData.objects.all()[:10]
    
    # Get the latest location data for the map
    latest_location = SensorData.objects.filter(
        latitude__isnull=False, 
        longitude__isnull=False
    ).first()
    
    context = {
        'latest_data': latest_data,
        'latest_system_data': latest_system_data,
        'recent_data': recent_data,
        'recent_system_data': recent_system_data,
        'table_data': table_data,
        'system_table_data': system_table_data,
        'latest_location': latest_location,
    }
    
    return render(request, 'dashboard/index.html', context)

def format_timestamp_local(timestamp):
    """Format timestamp in Jakarta timezone using Django's timezone utilities"""
    # Convert to Jakarta timezone
    jakarta_time = timezone.localtime(timestamp, timezone=timezone.get_fixed_timezone(420))  # UTC+7 for Jakarta
    return jakarta_time.strftime('%Y-%m-%d %H:%M:%S')

def format_timestamp_csv(timestamp):
    """Format timestamp for CSV export in Excel-friendly format"""
    # Convert to Jakarta timezone
    jakarta_time = timezone.localtime(timestamp, timezone=timezone.get_fixed_timezone(420))  # UTC+7 for Jakarta
    # Use Excel-friendly format: YYYY-MM-DD HH:MM:SS
    return jakarta_time.strftime('%Y-%m-%d %H:%M:%S')

def get_latest_data(request):
    """API endpoint to get latest sensor data for AJAX updates"""
    latest_data = SensorData.objects.first()
    latest_system_data = SystemData.get_latest_data()
    
    if latest_data:
        data = {
            'temperature': latest_data.temperature or 0,
            'humidity': latest_data.humidity or 0,
            'rainfall': latest_data.rainfall or 0,
            'thunder': latest_data.thunder or 0,
            'pest_count': latest_data.pest_count or 0,
            'cpu_usage': latest_data.cpu_usage or 0,
            'status': latest_data.status or 'Offline',
            'timestamp': format_timestamp_local(latest_data.timestamp),
            'latitude': latest_data.latitude,
            'longitude': latest_data.longitude,
            'has_location': latest_data.has_location
        }
    else:
        data = {
            'temperature': 0,
            'humidity': 0,
            'rainfall': 0,
            'thunder': 0,
            'pest_count': 0,
            'cpu_usage': 0,
            'status': 'Offline',
            'timestamp': 'No data',
            'latitude': None,
            'longitude': None,
            'has_location': False
        }
    
    # Add system data if available
    if latest_system_data:
        data.update({
            'system_cpu_percent': latest_system_data.cpu_percent or 0,
            'system_ram_percent': latest_system_data.ram_percent or 0,
            'system_ram_used_gb': latest_system_data.ram_used_gb or 0,
            'system_ram_total_gb': latest_system_data.ram_total_gb or 0,
            'system_storage_percent': latest_system_data.storage_percent or 0,
            'system_storage_used_gb': latest_system_data.storage_used_gb or 0,
            'system_storage_total_gb': latest_system_data.storage_total_gb or 0,
            'system_network_sent_mb': latest_system_data.network_sent_mb or 0,
            'system_network_recv_mb': latest_system_data.network_recv_mb or 0,
            'system_load_1min': latest_system_data.load_1min or 0,
            'system_load_5min': latest_system_data.load_5min or 0,
            'system_load_15min': latest_system_data.load_15min or 0,
            'system_status': latest_system_data.status or 'Offline',
            'system_timestamp': format_timestamp_local(latest_system_data.timestamp),
            'battery_level': latest_system_data.battery_level or 0,
        })
    else:
        data.update({
            'system_cpu_percent': 0,
            'system_ram_percent': 0,
            'system_ram_used_gb': 0,
            'system_ram_total_gb': 0,
            'system_storage_percent': 0,
            'system_storage_used_gb': 0,
            'system_storage_total_gb': 0,
            'system_network_sent_mb': 0,
            'system_network_recv_mb': 0,
            'system_load_1min': 0,
            'system_load_5min': 0,
            'system_load_15min': 0,
            'system_status': 'Offline',
            'system_timestamp': 'No system data',
            'battery_level': 0,
        })
    
    return JsonResponse(data)

def get_system_data(request):
    """API endpoint to get latest system data for AJAX updates"""
    latest_system_data = SystemData.get_latest_data()
    
    if latest_system_data:
        data = {
            'cpu_percent': latest_system_data.cpu_percent or 0,
            'ram_percent': latest_system_data.ram_percent or 0,
            'ram_used_gb': latest_system_data.ram_used_gb or 0,
            'ram_total_gb': latest_system_data.ram_total_gb or 0,
            'storage_percent': latest_system_data.storage_percent or 0,
            'storage_used_gb': latest_system_data.storage_used_gb or 0,
            'storage_total_gb': latest_system_data.storage_total_gb or 0,
            'network_sent_mb': latest_system_data.network_sent_mb or 0,
            'network_recv_mb': latest_system_data.network_recv_mb or 0,
            'load_1min': latest_system_data.load_1min or 0,
            'load_5min': latest_system_data.load_5min or 0,
            'load_15min': latest_system_data.load_15min or 0,
            'status': latest_system_data.status or 'Offline',
            'timestamp': format_timestamp_local(latest_system_data.timestamp),
            'cpu_temp': latest_system_data.cpu_temp or 0,
            'battery_level': latest_system_data.battery_level or 0,
        }
    else:
        data = {
            'cpu_percent': 0,
            'ram_percent': 0,
            'ram_used_gb': 0,
            'ram_total_gb': 0,
            'storage_percent': 0,
            'storage_used_gb': 0,
            'storage_total_gb': 0,
            'network_sent_mb': 0,
            'network_recv_mb': 0,
            'load_1min': 0,
            'load_5min': 0,
            'load_15min': 0,
            'status': 'Offline',
            'timestamp': 'No system data',
            'cpu_temp': 0,
            'battery_level': 0,
        }
    
    return JsonResponse(data)

def get_location_data(request):
    """API endpoint to get location data for the map"""
    latest_location = SensorData.objects.filter(
        latitude__isnull=False, 
        longitude__isnull=False
    ).first()
    
    if latest_location:
        data = {
            'latitude': latest_location.latitude,
            'longitude': latest_location.longitude,
            'timestamp': format_timestamp_local(latest_location.timestamp),
            'status': latest_location.status
        }
    else:
        data = {
            'latitude': None,
            'longitude': None,
            'timestamp': 'No location data',
            'status': 'Offline'
        }
    
    return JsonResponse(data)

def get_detection_statistics(request):
    """API endpoint to get pest detection statistics for charts"""
    try:
        # Get days parameter from request, default to 7 days
        days = int(request.GET.get('days', 7))
        
        # Get detection statistics with appropriate aggregation
        stats = DetectionData.get_detection_statistics(days=days)
        
        # Format data for Chart.js
        chart_data = {
            'labels': [],
            'datasets': []
        }
        
        # Prepare data for chart based on period
        if stats['daily_stats']:
            # Sort dates
            sorted_dates = sorted(stats['daily_stats'].keys())
            
            # Format labels based on period
            if days == 1:
                # For today, show hourly data
                chart_data['labels'] = [date.strftime('%H:%M') for date in sorted_dates]
            elif days <= 7:
                # For 1-7 days, show daily data
                chart_data['labels'] = [date.strftime('%d/%m') for date in sorted_dates]
            elif days <= 30:
                # For 8-30 days, show daily data
                chart_data['labels'] = [date.strftime('%d/%m') for date in sorted_dates]
            elif days <= 90:
                # For 1-3 months, show weekly data
                chart_data['labels'] = [f"Week {i+1}" for i in range(len(sorted_dates))]
            else:
                # For 1 year, show monthly data
                chart_data['labels'] = [date.strftime('%b %Y') for date in sorted_dates]
            
            # Create datasets for each pest class
            pest_classes = set()
            for date_stats in stats['daily_stats'].values():
                pest_classes.update(date_stats['class_counts'].keys())
            
            # Create a dataset for each pest class
            colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#FF6384', '#36A2EB']
            for i, pest_class in enumerate(sorted(pest_classes)):
                dataset = {
                    'label': pest_class,
                    'data': [],
                    'backgroundColor': colors[i % len(colors)],
                    'borderColor': colors[i % len(colors)],
                    'borderWidth': 2,
                    'fill': False,
                    'tension': 0.1
                }
                
                for date in sorted_dates:
                    date_stats = stats['daily_stats'][date]
                    count = date_stats['class_counts'].get(pest_class, 0)
                    dataset['data'].append(count)
                
                chart_data['datasets'].append(dataset)
        
        # Add summary statistics
        response_data = {
            'chart_data': chart_data,
            'summary': {
                'total_detections': stats['total_detections'],
                'total_pests': stats['total_pests'],
                'class_counts': stats['class_counts'],
                'period_days': stats['period_days']
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'chart_data': {'labels': [], 'datasets': []},
            'summary': {'total_detections': 0, 'total_pests': 0, 'class_counts': {}, 'period_days': 7}
        }, status=500)

def get_latest_detection(request):
    """API endpoint to get latest detection data"""
    latest_detection = DetectionData.get_latest_detection()
    
    if latest_detection:
        data = {
            'total_detections': latest_detection.total_detections,
            'class_counts': latest_detection.class_counts,
            'timestamp': format_timestamp_local(latest_detection.timestamp),
            'status': latest_detection.status,
        }
    else:
        data = {
            'total_detections': 0,
            'class_counts': {},
            'timestamp': 'No detection data',
            'status': 'No data',
        }
    
    return JsonResponse(data)

def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'dashboard/login.html', {'error': 'Invalid credentials'})
    return render(request, 'dashboard/login.html')

def logout_view(request):
    """Handle user logout"""
    logout(request)
    return redirect('login')

@login_required
def data_log(request):
    """Display data log page with filtering and pagination"""
    # Get filter parameters
    data_type = request.GET.get('type', 'sensor')
    period = request.GET.get('period', '7')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    search = request.GET.get('search', '')
    page = request.GET.get('page', 1)
    
    # Calculate date range based on period
    if period != 'all':
        days = int(period)
        start_datetime = timezone.now() - timedelta(days=days)
    else:
        start_datetime = None
    
    # Filter data based on type
    if data_type == 'sensor':
        queryset = SensorData.objects.all()
        if start_datetime:
            queryset = queryset.filter(timestamp__gte=start_datetime)
    elif data_type == 'system':
        queryset = SystemData.objects.all()
        if start_datetime:
            queryset = queryset.filter(timestamp__gte=start_datetime)
    elif data_type == 'detection':
        queryset = DetectionData.objects.all()
        if start_datetime:
            queryset = queryset.filter(timestamp__gte=start_datetime)
    else:
        queryset = SensorData.objects.all()
    
    # Apply date filters if provided
    if start_date:
        queryset = queryset.filter(timestamp__date__gte=start_date)
    if end_date:
        queryset = queryset.filter(timestamp__date__lte=end_date)
    
    # Apply search filter
    if search:
        if data_type == 'sensor':
            queryset = queryset.filter(
                Q(status__icontains=search) | 
                Q(timestamp__icontains=search)
            )
        elif data_type == 'system':
            queryset = queryset.filter(
                Q(status__icontains=search) | 
                Q(timestamp__icontains=search)
            )
        elif data_type == 'detection':
            queryset = queryset.filter(
                Q(status__icontains=search) | 
                Q(timestamp__icontains=search)
            )
    
    if data_type == 'sensor':
        # Only show the latest record for each unique timestamp
        latest_ids = SensorData.objects.filter(
            timestamp=OuterRef('timestamp')
        ).order_by('-id').values('id')[:1]
        queryset = queryset.filter(id__in=Subquery(latest_ids)).order_by('-timestamp')
    elif data_type == 'detection':
        # Deduplicate: only latest record per timestamp
        latest_ids = queryset.values('timestamp').annotate(
            latest_id=Max('id')
        ).values_list('latest_id', flat=True)
        queryset = queryset.filter(id__in=latest_ids)
    else:
        queryset = queryset.order_by('-timestamp')
    
    # Pagination
    paginator = Paginator(queryset, 50)  # 50 items per page
    try:
        page_obj = paginator.page(page)
    except:
        page_obj = paginator.page(1)
    
    # Calculate total records
    total_records = paginator.count
    
    # Get the latest sensor data for navbar
    latest_data = SensorData.objects.first()
    
    # Get the latest system data for navbar
    latest_system_data = SystemData.get_latest_data()
    
    context = {
        'page_obj': page_obj,
        'data_type': data_type,
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'search': search,
        'total_records': total_records,
        'latest_data': latest_data,
        'latest_system_data': latest_system_data,
    }
    
    return render(request, 'dashboard/data_log.html', context)

@login_required
def download_csv(request):
    """Download sensor data as CSV with filtering"""
    # Get filter parameters
    data_type = request.GET.get('type', 'sensor')
    period = request.GET.get('period', '7')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    search = request.GET.get('search', '')
    
    # Calculate date range based on period
    if period != 'all':
        days = int(period)
        start_datetime = timezone.now() - timedelta(days=days)
    else:
        start_datetime = None
    
    # Filter data based on type
    if data_type == 'sensor':
        queryset = SensorData.objects.all()
        if start_datetime:
            queryset = queryset.filter(timestamp__gte=start_datetime)
    elif data_type == 'system':
        queryset = SystemData.objects.all()
        if start_datetime:
            queryset = queryset.filter(timestamp__gte=start_datetime)
    elif data_type == 'detection':
        queryset = DetectionData.objects.all()
        if start_datetime:
            queryset = queryset.filter(timestamp__gte=start_datetime)
    else:
        queryset = SensorData.objects.all()
    
    # Apply date filters if provided
    if start_date:
        queryset = queryset.filter(timestamp__date__gte=start_date)
    if end_date:
        queryset = queryset.filter(timestamp__date__lte=end_date)
    
    # Apply search filter
    if search:
        if data_type == 'sensor':
            queryset = queryset.filter(
                Q(status__icontains=search) | 
                Q(timestamp__icontains=search)
            )
        elif data_type == 'system':
            queryset = queryset.filter(
                Q(status__icontains=search) | 
                Q(timestamp__icontains=search)
            )
        elif data_type == 'detection':
            queryset = queryset.filter(
                Q(status__icontains=search) | 
                Q(timestamp__icontains=search)
            )
    
    # Order by timestamp and remove duplicates for sensor data
    if data_type == 'sensor':
        # Use a more precise deduplication approach to ensure only one record per timestamp
        from django.db.models import Max
        # Get the latest ID for each unique timestamp
        latest_ids = queryset.values('timestamp').annotate(
            latest_id=Max('id')
        ).values_list('latest_id', flat=True)
        # Filter to only include the latest record for each timestamp
        queryset = queryset.filter(id__in=latest_ids).order_by('-timestamp')
    else:
        queryset = queryset.order_by('-timestamp')
    
    # Generate timestamp for filename
    current_time = timezone.now().strftime('%Y%m%d_%H%M%S')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{data_type}_data_{current_time}.csv"'
    
    writer = csv.writer(response)
    
    # Write headers based on data type
    if data_type == 'sensor':
        writer.writerow(['Timestamp', 'Temperature', 'Humidity', 'Rainfall', 'Thunder', 'Pest Count', 'Status', 'Latitude', 'Longitude'])
        
        for data in queryset:
            writer.writerow([
                format_timestamp_csv(data.timestamp),
                data.temperature,
                data.humidity,
                data.rainfall,
                data.thunder,
                data.pest_count,
                data.status,
                data.latitude,
                data.longitude
            ])
    elif data_type == 'system':
        writer.writerow(['Timestamp', 'CPU %', 'RAM %', 'RAM Used (GB)', 'RAM Total (GB)', 'Storage %', 'Storage Used (GB)', 'Storage Total (GB)', 'Network Sent (MB)', 'Network Received (MB)', 'Load 1min', 'CPU Temp (°C)', 'Battery Level (%)', 'Status'])
        
        for data in queryset:
            writer.writerow([
                format_timestamp_csv(data.timestamp),
                data.cpu_percent,
                data.ram_percent,
                data.ram_used_gb,
                data.ram_total_gb,
                data.storage_percent,
                data.storage_used_gb,
                data.storage_total_gb,
                data.network_sent_mb,
                data.network_recv_mb,
                data.load_1min,
                data.cpu_temp,
                data.battery_level,
                data.status
            ])
    elif data_type == 'detection':
        writer.writerow(['Timestamp', 'Total Detections', 'Class Counts', 'Detection Details', 'Status'])
        
        for data in queryset:
            writer.writerow([
                format_timestamp_csv(data.timestamp),
                data.total_detections,
                str(data.class_counts) if data.class_counts else '',
                str(data.detection_details) if data.detection_details else '',
                data.status
            ])
    
    return response

@login_required
def download_all_csv(request):
    """Download all data (sensor + system + detection) as ZIP with separate CSV files"""
    import zipfile
    from io import BytesIO
    
    # Get filter parameters
    period = request.GET.get('period', '7')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    search = request.GET.get('search', '')
    
    # Calculate date range based on period
    if period != 'all':
        days = int(period)
        start_datetime = timezone.now() - timedelta(days=days)
    else:
        start_datetime = None
    
    # Filter sensor data
    sensor_queryset = SensorData.objects.all()
    if start_datetime:
        sensor_queryset = sensor_queryset.filter(timestamp__gte=start_datetime)
    if start_date:
        sensor_queryset = sensor_queryset.filter(timestamp__date__gte=start_date)
    if end_date:
        sensor_queryset = sensor_queryset.filter(timestamp__date__lte=end_date)
    if search:
        sensor_queryset = sensor_queryset.filter(
            Q(status__icontains=search) | 
            Q(timestamp__icontains=search)
        )
    
    # Filter system data
    system_queryset = SystemData.objects.all()
    if start_datetime:
        system_queryset = system_queryset.filter(timestamp__gte=start_datetime)
    if start_date:
        system_queryset = system_queryset.filter(timestamp__date__gte=start_date)
    if end_date:
        system_queryset = system_queryset.filter(timestamp__date__lte=end_date)
    if search:
        system_queryset = system_queryset.filter(
            Q(status__icontains=search) | 
            Q(timestamp__icontains=search)
        )
    
    # Filter detection data
    detection_queryset = DetectionData.objects.all()
    if start_datetime:
        detection_queryset = detection_queryset.filter(timestamp__gte=start_datetime)
    if start_date:
        detection_queryset = detection_queryset.filter(timestamp__date__gte=start_date)
    if end_date:
        detection_queryset = detection_queryset.filter(timestamp__date__lte=end_date)
    if search:
        detection_queryset = detection_queryset.filter(
            Q(status__icontains=search) | 
            Q(timestamp__icontains=search)
        )
    
    # Order by timestamp and remove duplicates for sensor data
    from django.db.models import Max
    # Get the latest ID for each unique timestamp
    latest_ids = sensor_queryset.values('timestamp').annotate(
        latest_id=Max('id')
    ).values_list('latest_id', flat=True)
    # Filter to only include the latest record for each timestamp
    sensor_queryset = sensor_queryset.filter(id__in=latest_ids).order_by('-timestamp')
    system_queryset = system_queryset.order_by('-timestamp')
    detection_queryset = detection_queryset.order_by('-timestamp')
    
    # Generate timestamp for filename
    current_time = timezone.now().strftime('%Y%m%d_%H%M%S')
    
    # Create ZIP file in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        
        # Create sensor data CSV
        sensor_csv = StringIO()
        sensor_writer = csv.writer(sensor_csv)
        sensor_writer.writerow(['Timestamp', 'Temperature', 'Humidity', 'Rainfall', 'Thunder', 'Pest Count', 'Status', 'Latitude', 'Longitude'])
        
        for data in sensor_queryset:
            sensor_writer.writerow([
                format_timestamp_csv(data.timestamp),
                data.temperature,
                data.humidity,
                data.rainfall,
                data.thunder,
                data.pest_count,
                data.status,
                data.latitude,
                data.longitude
            ])
        
        zip_file.writestr(f'sensor_data_{current_time}.csv', sensor_csv.getvalue())
        
        # Create system data CSV
        system_csv = StringIO()
        system_writer = csv.writer(system_csv)
        system_writer.writerow(['Timestamp', 'CPU %', 'RAM %', 'RAM Used (GB)', 'RAM Total (GB)', 'Storage %', 'Storage Used (GB)', 'Storage Total (GB)', 'Network Sent (MB)', 'Network Received (MB)', 'Load 1min', 'CPU Temp (°C)', 'Battery Level (%)', 'Status'])
        
        for data in system_queryset:
            system_writer.writerow([
                format_timestamp_csv(data.timestamp),
                data.cpu_percent,
                data.ram_percent,
                data.ram_used_gb,
                data.ram_total_gb,
                data.storage_percent,
                data.storage_used_gb,
                data.storage_total_gb,
                data.network_sent_mb,
                data.network_recv_mb,
                data.load_1min,
                data.cpu_temp,
                data.battery_level,
                data.status
            ])
        
        zip_file.writestr(f'system_data_{current_time}.csv', system_csv.getvalue())
        
        # Create detection data CSV
        detection_csv = StringIO()
        detection_writer = csv.writer(detection_csv)
        detection_writer.writerow(['Timestamp', 'Total Detections', 'Class Counts', 'Detection Details', 'Status'])
        
        for data in detection_queryset:
            detection_writer.writerow([
                format_timestamp_csv(data.timestamp),
                data.total_detections,
                str(data.class_counts) if data.class_counts else '',
                str(data.detection_details) if data.detection_details else '',
                data.status
            ])
        
        zip_file.writestr(f'detection_data_{current_time}.csv', detection_csv.getvalue())
    
    # Prepare response
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="all_data_{current_time}.zip"'
    
    return response

@login_required
def detection_page(request):
    """View for the pest detection page with camera and upload functionality"""
    return render(request, 'dashboard/detection.html')

@csrf_exempt
def upload_image(request):
    """API endpoint for handling image uploads and YOLO detection"""
    if request.method == 'POST':
        try:
            # Get the image data from the request
            data = json.loads(request.body)
            image_data = data.get('image')
            growth_stage = data.get('growth_stage', 'Vegetatif')  # Default to Vegetatif
            
            if not image_data:
                return JsonResponse({'error': 'No image data provided'}, status=400)
            
            # Remove the data URL prefix if present
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to OpenCV format for YOLO processing
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Use YOLO detector for pest detection
            try:
                from .yolo_detector import detect_pests
                detection_results = detect_pests(opencv_image)
            except Exception as e:
                logger.error(f"Error importing or using YOLO detector: {str(e)}")
                return JsonResponse({'error': f'Detection model error: {str(e)}'}, status=500)
            
            # Save the image to media directory
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f'detection_{timestamp}.jpg'
            file_path = os.path.join('detections', filename)
            
            # Save the image
            image.save(os.path.join(settings.MEDIA_ROOT, file_path))
            
            # Create detection record in database
            detection_data = DetectionData.objects.create(
                timestamp=timezone.now(),
                total_detections=len(detection_results.get('detections', [])),
                class_counts=detection_results.get('class_counts', {}),
                growth_stage=growth_stage,
                image_path=file_path,
                status='Completed'
            )
            
            # Log detection results
            logger.info(f"Detection completed: {detection_results['total_detections']} objects found")
            logger.info(f"Growth stage: {growth_stage}")
            if 'class_counts' in detection_results:
                for class_name, count in detection_results['class_counts'].items():
                    logger.info(f"  - {class_name}: {count}")
            
            return JsonResponse({
                'success': True,
                'detection_results': detection_results,
                'image_path': file_path,
                'detection_id': detection_data.id,
                'growth_stage': growth_stage
            })
            
        except Exception as e:
            logger.error(f"Error in upload_image: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def get_detection_history(request):
    """API endpoint to get detection history"""
    try:
        # Get recent detections
        recent_detections = DetectionData.objects.all().order_by('-timestamp')[:10]
        
        detections = []
        for detection in recent_detections:
            detections.append({
                'id': detection.id,
                'timestamp': format_timestamp_local(detection.timestamp),
                'total_detections': detection.total_detections,
                'growth_stage': detection.growth_stage,
                'class_counts': detection.class_counts,
                'status': detection.status,
                'image_path': detection.image_path
            })
        
        return JsonResponse({
            'success': True,
            'detections': detections
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def delete_detection(request, detection_id):
    """API endpoint to delete a detection result"""
    if request.method == 'DELETE':
        try:
            # Get the detection record
            detection = DetectionData.objects.get(id=detection_id)
            
            # Delete the associated image file if it exists
            if detection.image_path:
                image_path = os.path.join(settings.MEDIA_ROOT, detection.image_path)
                if os.path.exists(image_path):
                    os.remove(image_path)
                    logger.info(f"Deleted image file: {image_path}")
            
            # Delete the detection record
            detection.delete()
            logger.info(f"Deleted detection record: {detection_id}")
            
            return JsonResponse({
                'success': True,
                'message': 'Detection result deleted successfully'
            })
            
        except DetectionData.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Detection result not found'
            }, status=404)
        except Exception as e:
            logger.error(f"Error deleting detection: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)