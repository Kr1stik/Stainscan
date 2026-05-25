# Stain Detection Model Integration Setup

This guide explains how to run the trained YOLOv11 model as an API server and connect it to the Flutter app.

## Architecture

```
┌─────────────────┐         HTTP          ┌──────────────────┐
│  Flutter App    │◄──────────────────────►│  Flask API Server│
│  (Mobile)       │      JSON API          │  (localhost:5000)│
└─────────────────┘                        └──────────────────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │  YOLOv11 Model  │
                                            │stain_detection   │
                                            │_yolov11.pt      │
                                            └─────────────────┘
```

## Setup Instructions

### 1. Install Flask and Dependencies

```bash
cd ml_training

# Activate your venv (if not already)
python -m venv venv_gpu_311
venv_gpu_311\Scripts\activate

# Install required packages
pip install flask flask-cors
```

### 2. Start the Inference Server

**Option A: Using the batch script (Windows)**
```bash
cd ml_training
start_server.bat
```

**Option B: Manual start**
```bash
cd ml_training
venv_gpu\Scripts\activate
python inference_server.py
```

You should see:
```
Starting Stain Detection API Server...
Model path: ml_training/models/stain_detection_yolov11.pt
Model exists: True
✓ Model loaded successfully!
 * Running on http://0.0.0.0:5000
```

### 3. Configure Flutter App

The Flutter app is already set up to call the Flask API at `http://localhost:5000`.

If you need to change the API URL (e.g., for a remote server), modify the service:
```dart
// In lib/services/image_analysis_service_io.dart
ImageAnalysisService.setApiBaseUrl('http://192.168.1.100:5000');
```

### 4. Run the Flutter App

In a new terminal:
```bash
cd stain_scanner
flutter pub get
flutter run -d chrome  # or windows, or your device
```

## API Endpoints

### POST /analyze
Analyze an image and return stain type classification.

**Request (Base64 Image):**
```json
{
  "base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFhAJ/wlseKgAAAABJRU5ErkJggg=="
}
```

**Response:**
```json
{
  "stain_type": "mud",
  "success": true
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true
}
```

## Troubleshooting

### "Cannot reach Flask API at localhost:5000"
- Make sure the Flask server is running
- Check that port 5000 is not blocked by firewall
- Try: `netstat -ano | findstr :5000` to see if port is in use

### "ModuleNotFoundError: No module named 'ultralytics'"
```bash
pip install ultralytics
```

### Model loading fails
- Ensure `stain_detection_yolov11.pt` exists in `ml_training/models/`
- Check file permissions
- Try rebuilding/retraining if model file is corrupted

### Slow inference
- The first inference loads the model into GPU/CPU (slower)
- Subsequent inferences are faster (cached model)
- GPU inference is faster than CPU

## Development Notes

- The Flask API supports both **base64 image data** and **file uploads**
- The Flutter app uses base64 encoding to send images over HTTP
- The API includes CORS headers to allow cross-origin requests
- Fallback to mock detection if API is unavailable (for testing)

## Performance

- **Model:** YOLOv11 trained on 3 stain types (Mud, Ink, Cooking Oil)
- **Classes:** `mud`, `ink`, `cooking oil`, `unknown`
- **Inference Time:** ~500ms-2s (depending on hardware)
- **API Response Time:** ~1-3s (including network latency)

## Next Steps

- [ ] Deploy Flask API to production server (AWS, Google Cloud, etc.)
- [ ] Add authentication/API keys for production
- [ ] Implement image caching and batch processing
- [ ] Add inference logging and analytics
- [ ] Set up model versioning and auto-updates
