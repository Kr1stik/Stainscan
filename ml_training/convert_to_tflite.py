"""
Convert trained YOLOv8m model to TFLite format for mobile deployment
Run this after training completes (around epoch 100)
"""

import os
from pathlib import Path
from ultralytics import YOLO
import shutil

def convert_model_to_tflite():
    """Convert best.pt to TFLite format and copy to Flutter app"""
    
    # Paths - use absolute path to find the model
    import os
    model_path = Path(r'C:\Users\LENOVO\runs\detect\stain_detection\stain_detection_yolov11-5\weights\best.pt')
    flutter_app_path = Path('../stain_scanner/assets/models')
    
    print("=" * 60)
    print("YOLOv8m Model Conversion to TFLite")
    print("=" * 60)
    
    # Check if trained model exists
    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        print("⏳ Training may still be in progress...")
        return False
    
    print(f"\n✅ Found trained model: {model_path}")
    
    try:
        # Load model
        print("\n📦 Loading YOLOv8m model...")
        model = YOLO(str(model_path))
        
        # Export to TFLite
        print("\n🔄 Converting to TFLite format (mobile optimized)...")
        export_result = model.export(format='tflite', imgsz=640)
        
        print(f"✅ Export completed: {export_result}")
        
        # Find the converted model
        tflite_file = Path(export_result) if isinstance(export_result, str) else Path('best.tflite')
        
        if tflite_file.exists():
            print(f"\n📋 TFLite model: {tflite_file}")
            print(f"   Size: {tflite_file.stat().st_size / (1024*1024):.2f} MB")
            
            # Copy to Flutter app
            flutter_app_path.mkdir(parents=True, exist_ok=True)
            dest_path = flutter_app_path / 'stain_detector.tflite'
            
            print(f"\n📱 Copying to Flutter app: {dest_path}")
            shutil.copy2(tflite_file, dest_path)
            print(f"✅ Model copied successfully!")
            
            # Also copy PyTorch version as fallback
            pt_dest = flutter_app_path / 'stain_detector.pt'
            shutil.copy2(model_path, pt_dest)
            print(f"✅ PyTorch model also copied: {pt_dest}")
            
            print("\n" + "=" * 60)
            print("✅ CONVERSION COMPLETE!")
            print("=" * 60)
            print(f"\n📍 Models ready for Flutter:")
            print(f"   • assets/models/stain_detector.tflite (mobile optimized)")
            print(f"   • assets/models/stain_detector.pt (fallback)")
            print(f"\n📚 Next steps:")
            print(f"   1. Update stain_scanner/pubspec.yaml with tflite_flutter")
            print(f"   2. Run: flutter pub get")
            print(f"   3. Implement inference in ImageAnalysisService")
            print(f"   4. Test on device/emulator")
            
            return True
            
        else:
            print(f"❌ TFLite conversion failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    convert_model_to_tflite()
