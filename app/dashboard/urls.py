# type: ignore
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.index, name='index'),
    path('data-log/', views.data_log, name='data_log'),
    path('detection/', views.detection_page, name='detection'),
    path('download-csv/', views.download_csv, name='download_csv'),
    path('download-all-csv/', views.download_all_csv, name='download_all_csv'),
    path('api/latest-data/', views.get_latest_data, name='latest_data'),
    path('api/system-data/', views.get_system_data, name='system_data'),
    path('api/location-data/', views.get_location_data, name='location_data'),
    path('api/detection-statistics/', views.get_detection_statistics, name='detection_statistics'),
    path('api/latest-detection/', views.get_latest_detection, name='latest_detection'),
    path('api/upload-image/', views.upload_image, name='upload_image'),
    path('api/detection-history/', views.get_detection_history, name='detection_history'),
    path('api/delete-detection/<int:detection_id>/', views.delete_detection, name='delete_detection'),
]