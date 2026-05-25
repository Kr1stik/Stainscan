"""
Convert YOLOv11 model to TFLite for mobile deployment
"""
import torch
import torch.serialization
from pathlib import Path

# Disable weights_only to allow loading
import torch.serialization
torch.serialization.default_protocol = 4

def convert_to_tflite():
    model_path = Path('models/stain_detection_yolov11.pt')
    
    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        return False
    
    print(f"✅ Loading model from {model_path}...")
    
    try:
        # Use unsafe loading context for PyTorch 2.6
        with torch.serialization.safe_globals([]):
            # Monkey patch to disable weights_only check
            original_load = torch.load
            
            def unsafe_load(f, *args, **kwargs):
                kwargs['weights_only'] = False
                return original_load(f, *args, **kwargs)
            
            torch.load = unsafe_load
            
            # Now import and use YOLO
            from ultralytics import YOLO
            model = YOLO(str(model_path))
            
            # Restore original
            torch.load = original_load
        
        print("✅ Model loaded successfully!")
        
        # Export to TFLite
        print("\n🔄 Converting to TFLite format...")
        export_result = model.export(format='tflite', imgsz=640)
        print(f"✅ Export completed!")
        print(f"📁 TFLite model: {export_result}")
        
        # Copy to Flutter assets
        tflite_path = Path(export_result)
        if tflite_path.exists():
            flutter_assets = Path('../stain_scanner/assets/models')
            flutter_assets.mkdir(parents=True, exist_ok=True)
            
            import shutil
            dest = flutter_assets / 'stain_detector.tflite'
            shutil.copy(tflite_path, dest)
            print(f"✅ Copied to Flutter: {dest}")
            print(f"📊 Size: {dest.stat().st_size / (1024*1024):.2f} MB")
            return True
        else:
            print(f"❌ TFLite export failed")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    convert_to_tflite()
