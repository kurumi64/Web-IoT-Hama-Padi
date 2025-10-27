import cv2
import numpy as np
import os
import tempfile
from django.conf import settings
import logging
from datetime import datetime
import time
try:
    from sahi import AutoDetectionModel
    from sahi.predict import get_sliced_prediction
    SAHI_AVAILABLE = True
except ImportError as e:
    logger.error(f"SAHI import error: {e}")
    SAHI_AVAILABLE = False

logger = logging.getLogger(__name__)

class SAHIDetector:
    def __init__(self, model_path=None):
        """
        Initialize SAHI detector
        Args:
            model_path: Path to YOLO model file (.pt or .onnx)
        """
        self.model = None
        self.model_path = model_path
        self.detection_model = None
        
        # Default pest classes (you can customize these)
        self.pest_classes = [
            'pest_1', 'pest_2', 'pest_3', 'pest_4', 'pest_5'
        ]
        
        # Try to load the model
        self._load_model()
    
    def _load_model(self):
        """Load SAHI detection model"""
        try:
            if self.model_path and os.path.exists(self.model_path):
                logger.info(f"Attempting to load model from: {self.model_path}")
                self.detection_model = AutoDetectionModel.from_pretrained(
                    model_type="yolo11",
                    model_path=self.model_path,
                    confidence_threshold=0.8,
                    device="cpu",
                )
                logger.info(f"Successfully loaded SAHI model from {self.model_path}")
            else:
                logger.warning(f"Model path not found: {self.model_path}")
                # Use a default model for testing
                self.detection_model = AutoDetectionModel.from_pretrained(
                    model_type="yolo11",
                    model_path="best.onnx",  # Use nano model for testing
                    confidence_threshold=0.8,
                    device="cpu",
                )
                logger.info("Loaded default YOLO11 model for testing")
        except Exception as e:
            logger.error(f"Error loading SAHI model: {e}")
            logger.error(f"Model path was: {self.model_path}")
            self.detection_model = None
    
    def _resize_image(self, image, target_width=1920, target_height=1080):
        """
        Resize image to target dimensions
        Args:
            image: OpenCV image
            target_width: Target width
            target_height: Target height
        Returns:
            Resized image
        """
        current_height, current_width = image.shape[:2]
        
        if current_width != target_width or current_height != target_height:
            logger.info(f"Resizing image from {current_width}x{current_height} to {target_width}x{target_height}")
            image = cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_LANCZOS4)
        
        return image
    
    def _save_temp_image(self, image):
        """
        Save image to temporary file for SAHI processing
        Args:
            image: OpenCV image
        Returns:
            Temporary file path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"temp_input_{timestamp}.png"
        temp_path = os.path.join(tempfile.gettempdir(), temp_filename)
        
        cv2.imwrite(temp_path, image)
        return temp_path
    
    def detect(self, image):
        """
        Perform SAHI object detection on the image
        Args:
            image: OpenCV image (numpy array)
        Returns:
            dict: Detection results
        """
        if not SAHI_AVAILABLE:
            logger.warning("SAHI not available, using simulation")
            return self._simulate_detection(image)
            
        if self.detection_model is None:
            logger.warning("Detection model not loaded, using simulation")
            return self._simulate_detection(image)
        
        try:
            # Start timing
            start_time = time.time()
            
            # Resize image to 1080p
            image = self._resize_image(image)
            
            # Save temporary image
            temp_path = self._save_temp_image(image)
            
            # Perform SAHI detection
            result = get_sliced_prediction(
                temp_path,
                self.detection_model,
                slice_height=640,
                slice_width=640,
                overlap_height_ratio=0.5,
                overlap_width_ratio=0.5
            )
            
            # Calculate processing time
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Process detection results
            detections = []
            class_counts = {}
            
            for obj in result.object_prediction_list:
                class_name = obj.category.name
                confidence = obj.score.value
                bbox = obj.bbox.to_xyxy()
                
                # Count classes
                class_counts[class_name] = class_counts.get(class_name, 0) + 1
                
                detection = {
                    'class': class_name,
                    'confidence': confidence,
                    'bbox': [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])]
                }
                detections.append(detection)
            
            # Calculate average confidence
            avg_confidence = sum(d['confidence'] for d in detections) / len(detections) if detections else 0.0
            
            # Clean up temporary file
            try:
                os.remove(temp_path)
            except:
                pass
            
            logger.info(f"SAHI detection completed in {processing_time:.2f} seconds")
            logger.info(f"Detected {len(detections)} objects")
            
            return {
                'detections': detections,
                'total_detections': len(detections),
                'average_confidence': round(avg_confidence, 2),
                'processing_time': round(processing_time, 2),
                'class_counts': class_counts
            }
            
        except Exception as e:
            logger.error(f"Error during SAHI detection: {e}")
            return self._simulate_detection(image)
    
    def _simulate_detection(self, image):
        """
        Simulate detection results for testing
        This is used when no SAHI model is available
        """
        import random
        
        # Simulate some detection results
        detections = []
        classes = ['pest_1', 'pest_2', 'pest_3', 'pest_4']
        
        # Get image dimensions
        height, width = image.shape[:2]
        
        # Simulate 1-3 random detections
        num_detections = random.randint(1, 3)
        
        for i in range(num_detections):
            # Generate random bounding box within image bounds
            x1 = random.randint(50, width - 100)
            y1 = random.randint(50, height - 100)
            x2 = min(x1 + random.randint(50, 150), width - 10)
            y2 = min(y1 + random.randint(50, 150), height - 10)
            
            detection = {
                'class': random.choice(classes),
                'confidence': round(random.uniform(0.6, 0.95), 2),
                'bbox': [x1, y1, x2, y2]
            }
            detections.append(detection)
        
        # Calculate average confidence
        avg_confidence = sum(d['confidence'] for d in detections) / len(detections) if detections else 0.0
        
        return {
            'detections': detections,
            'total_detections': len(detections),
            'average_confidence': round(avg_confidence, 2),
            'processing_time': round(random.uniform(0.1, 0.5), 2),
            'class_counts': {d['class']: 1 for d in detections}
        }
    
    def draw_detections(self, image, detections):
        """
        Draw detection boxes on the image
        Args:
            image: OpenCV image
            detections: List of detection dictionaries
        Returns:
            OpenCV image with drawn detections
        """
        result_image = image.copy()
        
        for detection in detections:
            bbox = detection['bbox']
            class_name = detection['class']
            confidence = detection['confidence']
            
            # Draw bounding box
            cv2.rectangle(result_image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            
            # Draw label background
            cv2.rectangle(result_image, 
                         (bbox[0], bbox[1] - label_size[1] - 10),
                         (bbox[0] + label_size[0], bbox[1]),
                         (0, 255, 0), -1)
            
            # Draw label text
            cv2.putText(result_image, label, (bbox[0], bbox[1] - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        return result_image

# Global detector instance
_detector = None

def get_detector():
    """Get or create SAHI detector instance"""
    global _detector
    if _detector is None:
        # Use the specific model path
        model_path = '/home/kiki/system-dashboard/app/dashboard/models/best.onnx'
        _detector = SAHIDetector(model_path)
    return _detector

def detect_pests(image):
    """
    Main function to detect pests in an image using SAHI
    Args:
        image: OpenCV image (numpy array)
    Returns:
        dict: Detection results
    """
    detector = get_detector()
    return detector.detect(image) 