#!/usr/bin/env python3
"""
Test script for the SAHI pest detection system
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from dashboard.yolo_detector import SAHIDetector, detect_pests
import cv2
import numpy as np

def test_detection():
    """Test the SAHI detection system"""
    print("Testing SAHI Pest Detection System")
    print("=" * 40)
    
    # Create a test image (simple colored rectangles)
    test_image = np.zeros((1080, 1920, 3), dtype=np.uint8)
    cv2.rectangle(test_image, (100, 100), (300, 300), (0, 255, 0), -1)
    cv2.rectangle(test_image, (400, 200), (500, 350), (255, 0, 0), -1)
    cv2.rectangle(test_image, (800, 400), (900, 500), (0, 0, 255), -1)
    
    print("Created test image with 3 rectangles (1080p)")
    
    # Test detection
    try:
        results = detect_pests(test_image)
        print("Detection successful!")
        print(f"Total detections: {results['total_detections']}")
        print(f"Average confidence: {results['average_confidence']:.2f}")
        print(f"Processing time: {results['processing_time']:.2f}s")
        
        if 'class_counts' in results and results['class_counts']:
            print("\nClass counts:")
            for class_name, count in results['class_counts'].items():
                print(f"  - {class_name}: {count}")
        
        if results['detections']:
            print("\nDetections:")
            for i, detection in enumerate(results['detections']):
                print(f"  {i+1}. {detection['class']}: {detection['confidence']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"Detection failed: {e}")
        return False

def test_detector_initialization():
    """Test SAHI detector initialization"""
    print("\nTesting SAHI Detector Initialization")
    print("=" * 40)
    
    try:
        detector = SAHIDetector()
        print("SAHI detector initialized successfully")
        
        # Test with a simple image
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        results = detector.detect(test_image)
        print("Detection test passed")
        
        return True
        
    except Exception as e:
        print(f"SAHI detector initialization failed: {e}")
        return False

def test_image_resizing():
    """Test image resizing functionality"""
    print("\nTesting Image Resizing")
    print("=" * 40)
    
    try:
        detector = SAHIDetector()
        
        # Create test images of different sizes
        test_sizes = [(640, 480), (1920, 1080), (800, 600), (1280, 720)]
        
        for width, height in test_sizes:
            test_image = np.zeros((height, width, 3), dtype=np.uint8)
            resized = detector._resize_image(test_image)
            print(f"Resized {width}x{height} -> {resized.shape[1]}x{resized.shape[0]}")
        
        print("Image resizing test passed")
        return True
        
    except Exception as e:
        print(f"Image resizing test failed: {e}")
        return False

if __name__ == "__main__":
    print("SAHI Pest Detection System Test")
    print("=" * 50)
    
    # Test detector initialization
    init_success = test_detector_initialization()
    
    # Test image resizing
    resize_success = test_image_resizing()
    
    # Test detection
    detection_success = test_detection()
    
    print("\n" + "=" * 50)
    if init_success and resize_success and detection_success:
        print("✅ All tests passed! The SAHI detection system is working.")
    else:
        print("❌ Some tests failed. Check the error messages above.")
    
    print("\nTo use the web interface:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run migrations: python manage.py migrate")
    print("3. Start server: python manage.py runserver")
    print("4. Visit: http://localhost:8000/detection/")
    
    print("\nSAHI Features:")
    print("- Slicing Aided Hyper Inference for better detection")
    print("- Automatic image resizing to 1080p")
    print("- Overlapping slices for improved accuracy")
    print("- Class counting and detailed results") 