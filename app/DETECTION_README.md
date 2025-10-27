# SAHI Pest Detection System

This system provides a web-based interface for detecting pests using SAHI (Slicing Aided Hyper Inference) with YOLO object detection. It supports both camera capture and image upload functionality with enhanced detection accuracy.

## Features

- **Camera Capture**: Real-time camera access for live pest detection
- **Image Upload**: Drag & drop or file selection for uploaded images
- **SAHI Integration**: Enhanced object detection using Slicing Aided Hyper Inference
- **Automatic Resizing**: Images automatically resized to 1080p for optimal detection
- **Detection History**: View and manage past detections
- **Class Counting**: Detailed breakdown of detected pest categories
- **Responsive Design**: Works on desktop and mobile devices

## SAHI Benefits

- **Improved Accuracy**: Slicing technique enhances detection of small objects
- **Better Performance**: Overlapping slices reduce missed detections
- **Scalable**: Works well with high-resolution images
- **Robust**: Handles various image sizes and aspect ratios

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create the media directory for storing uploaded images:
```bash
mkdir -p media/detections
```

3. Run Django migrations:
```bash
python manage.py migrate
```

4. Start the development server:
```bash
python manage.py runserver
```

## Usage

### Accessing the Detection Page

1. Navigate to the detection page: `http://localhost:8000/detection/`
2. Login with your credentials if required

### Camera Detection

1. Click "Mulai Kamera" to start the camera
2. Allow camera permissions when prompted
3. Click "Ambil Foto" to capture an image
4. Wait for the SAHI detection results to appear

### Image Upload

1. Drag and drop an image onto the upload area, or
2. Click the upload area to select a file
3. Supported formats: JPG, PNG, GIF (Max: 10MB)
4. Wait for the SAHI detection results to appear

### Detection Results

The system displays:
- **Total Detections**: Number of pests detected
- **Average Confidence**: Overall detection confidence
- **Processing Time**: Time taken for SAHI detection
- **Class Counts**: Breakdown by pest category
- **Individual Detections**: Each detected pest with confidence score

## SAHI Model Integration

### Using Custom Model

1. Place your trained YOLO model in the `models/` directory
2. Update the model path in `dashboard/yolo_detector.py`:
```python
model_path = os.path.join(settings.BASE_DIR, 'models', 'your_model.onnx')
```

### Model Requirements

- **Format**: `.pt` (PyTorch) or `.onnx` (recommended)
- **Classes**: Configure pest classes in `SAHIDetector.pest_classes`
- **Input**: RGB images (automatically resized to 1080p)
- **SAHI Settings**: Configurable slice size and overlap ratios

### SAHI Configuration

The system uses these SAHI parameters:
- **Slice Size**: 640x640 pixels
- **Overlap Ratio**: 50% (both height and width)
- **Confidence Threshold**: 0.8
- **Device**: CPU (configurable for GPU)

### Default Behavior

If no custom model is found, the system will:
- Use YOLOv8n for testing
- Apply SAHI slicing for enhanced detection
- Fall back to simulation mode if SAHI fails to load
- Log warnings about missing custom model

## API Endpoints

### Upload Image
- **URL**: `/api/upload-image/`
- **Method**: POST
- **Body**: JSON with base64 encoded image
- **Response**: SAHI detection results and image path

### Detection History
- **URL**: `/api/detection-history/`
- **Method**: GET
- **Response**: List of recent detections with class counts

## Configuration

### Media Settings

The system uses Django's media settings:
- `MEDIA_ROOT`: Base directory for uploaded files
- Images are stored in `media/detections/`
- File naming: `detection_YYYYMMDD_HHMMSS.jpg`

### SAHI Settings

Configure SAHI parameters in `yolo_detector.py`:
- Slice height/width: 640 pixels
- Overlap ratios: 0.5 (50%)
- Confidence threshold: 0.8
- Model path: Customize as needed

### Image Processing

- **Automatic Resizing**: All images resized to 1920x1080
- **Temporary Files**: SAHI uses temporary files for processing
- **Cleanup**: Temporary files automatically removed after processing

## Troubleshooting

### Camera Issues
- Ensure HTTPS for production (camera requires secure context)
- Check browser permissions for camera access
- Try different browsers if camera doesn't work

### SAHI Model Loading Issues
- Verify model file exists and is accessible
- Check model format compatibility (.onnx recommended)
- Review error logs for specific issues
- Ensure sufficient memory for model loading

### Performance Issues
- Use smaller model variants for faster inference
- Optimize image size before upload
- Consider GPU acceleration for large models
- Adjust SAHI slice size for performance vs accuracy trade-off

## Development

### Adding New Features

1. **Custom Classes**: Update `pest_classes` in `SAHIDetector`
2. **SAHI Parameters**: Modify slice size and overlap ratios
3. **UI Enhancements**: Modify `detection.html` template
4. **API Extensions**: Add new endpoints in `views.py`

### Testing

1. Test with various image formats and sizes
2. Verify camera functionality on different devices
3. Check SAHI detection accuracy with your specific model
4. Test with high-resolution images for slicing effectiveness

## Security Considerations

- File upload validation prevents malicious files
- Image size limits prevent DoS attacks
- CSRF protection enabled for all forms
- Input sanitization prevents XSS attacks
- Temporary file cleanup prevents disk space issues

## Production Deployment

1. Use HTTPS for camera functionality
2. Configure proper media file serving
3. Set up database for production
4. Configure logging and monitoring
5. Optimize SAHI model loading and inference
6. Consider GPU acceleration for better performance

## SAHI Technical Details

### How SAHI Works

1. **Image Slicing**: Large images divided into overlapping slices
2. **Detection**: Each slice processed independently
3. **Result Merging**: Detections from slices combined
4. **Duplicate Removal**: Overlapping detections filtered
5. **Final Output**: Consolidated detection results

### Performance Optimization

- **Slice Size**: Smaller slices = better small object detection
- **Overlap Ratio**: Higher overlap = fewer missed detections
- **Confidence Threshold**: Adjust for precision vs recall
- **Model Size**: Smaller models = faster processing

## Support

For issues or questions:
1. Check the Django logs for error messages
2. Verify all dependencies are installed (including SAHI)
3. Test with the default simulation mode first
4. Ensure proper file permissions for media directory
5. Check SAHI model compatibility and format 