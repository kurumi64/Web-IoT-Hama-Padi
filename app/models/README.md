# SAHI YOLO Models Directory

This directory is for storing your custom YOLO models for SAHI pest detection.

## Adding Your Model

1. **Place your model file here**: Copy your trained YOLO model (`.pt` or `.onnx` format) to this directory
2. **Update the detector**: Modify `dashboard/yolo_detector.py` to point to your model:
   ```python
   model_path = os.path.join(settings.BASE_DIR, 'models', 'your_model.onnx')
   ```
3. **Configure classes**: Update the `pest_classes` list in `SAHIDetector` to match your model's classes

## Model Requirements

- **Format**: PyTorch (`.pt`) or ONNX (`.onnx` - recommended)
- **Input**: RGB images (automatically resized to 1920x1080)
- **Output**: Standard YOLO format with bounding boxes and class predictions
- **Size**: Recommended under 100MB for web deployment
- **SAHI Compatible**: Must work with SAHI slicing and merging

## SAHI Model Configuration

### Recommended Settings

- **Model Type**: `yolo11` (for YOLOv8/v11 models)
- **Confidence Threshold**: 0.8 (configurable)
- **Device**: CPU (configurable for GPU)
- **Slice Size**: 640x640 pixels
- **Overlap Ratio**: 50% (both height and width)

### Model Optimization

For best SAHI performance:
- Use ONNX format for faster inference
- Optimize model size for web deployment
- Test with high-resolution images
- Verify slicing compatibility

## Example Model Structure

```
models/
├── pest_detection.onnx        # Your custom SAHI model (recommended)
├── pest_detection.pt          # Alternative PyTorch format
└── README.md                  # This file
```

## Testing Your Model

1. Start the Django server: `python manage.py runserver`
2. Navigate to: `http://localhost:8000/detection/`
3. Upload an image or use the camera
4. Check the SAHI detection results
5. Verify class counts and confidence scores

## SAHI-Specific Considerations

### Model Compatibility

- **Slicing Support**: Model must work with image slices
- **Batch Processing**: Efficient processing of multiple slices
- **Memory Usage**: Consider memory requirements for slicing
- **Inference Speed**: Balance accuracy vs processing time

### Performance Tuning

- **Slice Size**: Adjust for your specific use case
- **Overlap Ratio**: Higher overlap = better accuracy, slower speed
- **Confidence Threshold**: Balance precision vs recall
- **Model Size**: Smaller models = faster slicing

## Troubleshooting

- **Model not loading**: Check file permissions and path
- **Wrong predictions**: Verify class names match your training data
- **Slow inference**: Consider using a smaller model variant
- **Memory issues**: Reduce model size or use GPU acceleration
- **SAHI errors**: Check model compatibility with slicing
- **Slice processing**: Verify model works with image slices

## Default Behavior

If no custom model is found, the system will:
- Use YOLOv8n for testing (automatically downloaded)
- Apply SAHI slicing for enhanced detection
- Fall back to simulation mode if SAHI fails to load
- Log warnings about missing custom model

## SAHI Technical Details

### How SAHI Works with Your Model

1. **Image Preparation**: Input image resized to 1920x1080
2. **Slicing**: Image divided into 640x640 overlapping slices
3. **Detection**: Each slice processed by your YOLO model
4. **Merging**: Results from all slices combined
5. **Filtering**: Duplicate detections removed
6. **Output**: Final consolidated detection results

### Model Requirements for SAHI

- **Input Format**: Must accept RGB images
- **Output Format**: Standard YOLO detection format
- **Batch Processing**: Should handle multiple inputs efficiently
- **Memory Efficient**: Should work with limited memory
- **Fast Inference**: Quick processing for real-time use 