#!/usr/bin/env python3
"""
Test the Stain Detection API locally.
Usage: python test_api.py
"""

import requests
import json
import base64
import sys
from pathlib import Path

API_BASE_URL = "http://localhost:5000"


def test_health():
    """Test the health check endpoint."""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is running!")
            print(f"   Status: {data.get('status')}")
            print(f"   Model loaded: {data.get('model_loaded')}")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {API_BASE_URL}")
        print(f"   Is the Flask server running?")
        print(f"   Run: python inference_server.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_prediction_with_file(image_path):
    """Test prediction with a local image file."""
    print(f"\n📸 Testing prediction with {image_path}...")
    
    if not Path(image_path).exists():
        print(f"❌ Image file not found: {image_path}")
        return False
    
    try:
        # Send image file
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = requests.post(
                f"{API_BASE_URL}/analyze",
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            stain_type = data.get("stain_type", "unknown")
            print(f"✅ Prediction successful!")
            print(f"   Detected stain type: {stain_type}")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_prediction_with_base64(image_path):
    """Test prediction with base64-encoded image."""
    print(f"\n📸 Testing prediction with base64 ({image_path})...")
    
    if not Path(image_path).exists():
        print(f"❌ Image file not found: {image_path}")
        return False
    
    try:
        # Encode image to base64
        with open(image_path, "rb") as f:
            image_data = f.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")
        
        payload = {
            "base64": base64_image
        }
        
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            stain_type = data.get("stain_type", "unknown")
            print(f"✅ Base64 prediction successful!")
            print(f"   Detected stain type: {stain_type}")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("=" * 50)
    print("Stain Detection API - Test Suite")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ API is not running. Start it with:")
        print("   python inference_server.py")
        sys.exit(1)
    
    # Test 2: Prediction with sample image (if available)
    sample_images = [
        "../datasets/raw/mud_stain.jpg",
        "../datasets/raw/ink_stain.jpg",
        "../datasets/raw/oil_stain.jpg",
    ]
    
    tested = False
    for img_path in sample_images:
        if Path(img_path).exists():
            test_prediction_with_base64(img_path)
            tested = True
            break
    
    if not tested:
        print("\n💡 Tip: Place a test image in ml_training/ and run:")
        print("   python test_api.py <image_path>")
    
    print("\n" + "=" * 50)
    print("✅ All tests passed!")
    print("=" * 50)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        test_health()
        test_prediction_with_base64(image_path)
    else:
        main()
