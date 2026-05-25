"""
Simple Flask API server for stain detection with mock data.
Serves mock bounding boxes for demonstration purposes.
"""

import os
import json
import base64
import tempfile
from pathlib import Path
from io import BytesIO

from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np

app = Flask(__name__)
CORS(app)

# Mock data for demonstration
MOCK_STAIN_TYPES = ["mud", "ink", "cooking_oil"]
MOCK_DETECTIONS = [
    {
        "type": "ink",
        "confidence": 0.85,
        "bbox": [0.35, 0.30, 0.70, 0.62]
    },
    {
        "type": "mud",
        "confidence": 0.72,
        "bbox": [0.10, 0.18, 0.45, 0.52]
    }
]

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "model_loaded": False, "mode": "mock"})

@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Analyze an image and return mock stain type classification with bounding boxes.
    
    Expects:
    - JSON with base64: Base64-encoded image data
    - Multipart form data with file: Image file upload
    """
    try:
        # Handle base64 image (JSON request)
        if request.is_json and request.json and "base64" in request.json:
            base64_str = request.json["base64"]
            # Remove data URI prefix if present
            if "," in base64_str:
                base64_str = base64_str.split(",")[1]

            # Decode and validate image
            image_data = base64.b64decode(base64_str)
            image = Image.open(BytesIO(image_data))
            # Convert to ensure it's valid
            image.verify()

        # Handle file upload (multipart form data)
        elif "file" in request.files:
            file = request.files["file"]
            # Validate file
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            # Save temporarily to validate
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
                temp_path = temp_file.name
                file.save(temp_path)
            
            # Validate image
            image = Image.open(temp_path)
            image.verify()
            os.remove(temp_path)

        else:
            return jsonify({"error": "No image provided. Send either base64 JSON or multipart file."}), 400

        # Return mock results
        return jsonify({
            "stain_type": "ink",  # Primary detection
            "fabric_type": "cotton",
            "fabric_confidence": 0.95,
            "detections": MOCK_DETECTIONS,
            "success": True,
            "mode": "mock"
        })
    
    except Exception as e:
        print(f"Error during mock analysis: {e}")
        return jsonify({"error": str(e), "success": False}), 500

@app.route("/predict", methods=["POST"])
def predict():
    """
    Predict stain type from image file path (for local testing).
    """
    try:
        data = request.get_json()
        image_path = data.get("image_path")
        
        if not image_path or not os.path.exists(image_path):
            return jsonify({"error": "Invalid image path"}), 400
        
        # Return mock results
        return jsonify({
            "stain_type": "ink",
            "detections": MOCK_DETECTIONS,
            "success": True,
            "mode": "mock"
        })
    
    except Exception as e:
        print(f"Error during mock prediction: {e}")
        return jsonify({"error": str(e), "success": False}), 500

@app.route("/", methods=["GET"])
def index():
    """API info endpoint."""
    return jsonify({
        "name": "Mock Stain Detection API",
        "version": "1.0",
        "mode": "mock",
        "endpoints": {
            "GET /health": "Health check",
            "POST /analyze": "Analyze image (base64 or file upload). Returns mock stain_type, fabric_type, and detections with bounding boxes.",
            "POST /predict": "Predict from local image path",
        }
    })

if __name__ == "__main__":
    print("Starting Mock Stain Detection API Server...")
    print("Mode: Mock detection with bounding boxes")
    app.run(host="0.0.0.0", port=5000, debug=False)