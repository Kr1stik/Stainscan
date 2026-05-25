"""
YOLOv11 Training Script for Stain Detection
Trains a YOLOv11 model for stain classification using organized image folders.
"""

import yaml
import argparse
from pathlib import Path
from ultralytics import YOLO
import torch
import shutil
import os

class YOLOv11StainDetector:
    def __init__(self, config_path='config.yaml'):
        config_file = Path(config_path)
        if not config_file.is_absolute() and not config_file.exists():
            # Look in the parent directory (ml_training)
            config_file = Path(__file__).resolve().parent.parent / config_path

        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")

        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.classes = self.config['classes']
        self.num_classes = len(self.classes)
        self.image_size = self.config['preprocessing']['image_size'][0]
        self.batch_size = self.config['training']['batch_size']
        self.epochs = self.config['training']['epochs']
        self.learning_rate = self.config['training']['learning_rate']
        self.model_size = self.config['training']['model_size']
        self.task = self.config['training']['task']
        self.patience = self.config['training']['patience']
        self.device = self.config['training']['device']
        
        self.model = None
        
        # Create output directories
        Path(self.config['output']['logs_dir']).mkdir(parents=True, exist_ok=True)
        Path(self.config['model']['save_path']).mkdir(parents=True, exist_ok=True)
    
    def check_device(self):
        """Check GPU availability."""
        print("\n" + "="*60)
        print("DEVICE CHECK")
        print("="*60)
        
        if isinstance(self.device, int):
            if torch.cuda.is_available():
                print(f"✓ GPU Available: {torch.cuda.get_device_name(self.device)}")
                print(f"  CUDA Version: {torch.version.cuda}")
                print(f"  PyTorch Version: {torch.__version__}")
            else:
                print("⚠ GPU not available. Using CPU (slower)")
                self.device = 'cpu'
        else:
            print(f"Using device: {self.device}")
    
    def build_model(self):
        """Load YOLOv11 model."""
        print("\n" + "="*60)
        print(f"Building YOLOv11-{self.model_size} for {self.task}")
        print("="*60)
        
        # Map size to model name
        model_map = {
            'n': 'yolov8n',
            's': 'yolov8s',
            'm': 'yolov8m',
            'l': 'yolov8l',
            'x': 'yolov8x',
        }
        
        base_model = model_map.get(self.model_size, 'yolov11m')
        
        if self.task == 'classify':
            model_name = f"{base_model}-cls"
        elif self.task == 'detect':
            model_name = f"{base_model}"
        else:
            model_name = f"{base_model}-seg"
        
        print(f"Loading: {model_name}")
        try:
            self.model = YOLO(model_name)
        except Exception as e:
            print(f"Failed to load model with default settings: {e}")
            print("Trying with weights_only=False...")
            # Monkey-patch torch.load temporarily for PyTorch 2.6 compatibility
            import torch
            original_load = torch.load
            torch.load = lambda *args, **kwargs: original_load(*args, weights_only=False, **{k: v for k, v in kwargs.items() if k != 'weights_only'})
            try:
                self.model = YOLO(model_name)
                torch.load = original_load
            except Exception as e2:
                print(f"Failed to load model: {e2}")
                raise
        
        print("\n✓ Model loaded successfully!")
        return self.model
    
    def prepare_dataset_structure(self, data_path):
        """
        Prepare dataset in YOLO format.
        YOLOv11 expects the following structure for classification:
        
        dataset/
        ├── train/
        │   ├── class1/
        │   │   ├── image1.jpg
        │   │   └── ...
        │   ├── class2/
        │   └── ...
        ├── val/
        │   ├── class1/
        │   ├── class2/
        │   └── ...
        └── test/
            ├── class1/
            ├── class2/
            └── ...
        """
        data_path = Path(data_path)
        
        print("\n" + "="*60)
        print("VERIFYING DATASET STRUCTURE")
        print("="*60)
        
        required_splits = ['train', 'val']
        for split in required_splits:
            split_path = data_path / split
            if not split_path.exists():
                raise ValueError(f"Missing {split} split at {split_path}")
            
            # Check classes
            for cls in self.classes:
                cls_path = split_path / cls
                if not cls_path.exists():
                    print(f"⚠ Warning: {split}/{cls} folder not found")
                else:
                    image_count = len(list(cls_path.glob('*.[jJ][pP]*')))
                    print(f"✓ {split}/{cls:15} - {image_count} images")
        
        print("\n✓ Dataset structure verified!")
        return str(data_path)
    
    def train(self, train_data_path):
        """Train YOLOv11 model."""
        print("\n" + "="*60)
        print("STARTING YOLOV11 TRAINING")
        print("="*60)
        
        # Resolve paths relative to this script's directory
        script_dir = Path(__file__).resolve().parent.parent
        train_data_abs = script_dir / train_data_path
        
        if self.task == 'detect':
            # Allow passing either a YAML file or a dataset folder path.
            if train_data_abs.suffix in ['.yaml', '.yml']:
                if not train_data_abs.exists():
                    raise FileNotFoundError(f"Could not find data.yaml at {train_data_abs}")
                data_path = str(train_data_abs)
            else:
                data_yaml = train_data_abs.parent / 'data.yaml'
                if not data_yaml.exists():
                    data_yaml = train_data_abs / 'data.yaml'
                if not data_yaml.exists():
                    raise FileNotFoundError(f"Could not find data.yaml at {data_yaml}")
                data_path = str(data_yaml)
            print(f"Using data config: {data_path}")
        else:
            # Prepare dataset
            data_path = self.prepare_dataset_structure(train_data_path)
        
        print("\nTraining configuration:")
        print(f"  Model: YOLOv11-{self.model_size}")
        print(f"  Task: {self.task}")
        print(f"  Epochs: {self.epochs}")
        print(f"  Batch size: {self.batch_size}")
        print(f"  Image size: {self.image_size}x{self.image_size}")
        print(f"  Device: {self.device}")
        print(f"  Patience: {self.patience}")
        
        # Train model
        results = self.model.train(
            data=data_path,
            epochs=self.epochs,
            imgsz=self.image_size,
            batch=self.batch_size,
            device=self.device,
            project=self.config['output']['project'],
            name=self.config['model']['name'],
            exist_ok=False,
            save=True,
            save_period=self.config['output']['save_period'],
            val=True,
            verbose=True,
            # Data augmentation
            hsv_h=self.config['augmentation']['hsv_h'],
            hsv_s=self.config['augmentation']['hsv_s'],
            hsv_v=self.config['augmentation']['hsv_v'],
            degrees=self.config['augmentation']['degrees'],
            translate=self.config['augmentation']['translate'],
            scale=self.config['augmentation']['scale'],
            flipud=self.config['augmentation']['flipud'],
            fliplr=self.config['augmentation']['fliplr'],
            mosaic=self.config['augmentation']['mosaic'],
            mixup=self.config['augmentation']['mixup'],
            # Learning rate
            lr0=self.learning_rate,
            lrf=0.01,
            # Early stopping
            patience=self.patience,
        )
        
        print("\n" + "="*60)
        print("Training complete!")
        print("="*60)
        
        return results
    
    def save_model(self, export_format='pt'):
        """Save and export model."""
        if self.model is None:
            print("Error: Model not trained yet.")
            return
        
        print("\n" + "="*60)
        print("SAVING MODEL")
        print("="*60)
        
        save_path = Path(self.config['model']['save_path']) / f"{self.config['model']['name']}.{export_format}"
        
        if export_format == 'pt':
            # PyTorch format (default)
            self.model.save(str(save_path))
            print(f"✓ Model saved: {save_path}")
        
        elif export_format == 'onnx':
            # ONNX format (for cross-platform deployment)
            print("Exporting to ONNX format...")
            exported_model = self.model.export(format='onnx', imgsz=self.image_size, half=False)
            print(f"✓ ONNX model exported: {exported_model}")
        
        elif export_format == 'tflite':
            # TensorFlow Lite (for mobile)
            print("Exporting to TFLite format...")
            exported_model = self.model.export(format='tflite', imgsz=self.image_size, half=True)
            print(f"✓ TFLite model exported: {exported_model}")
        
        elif export_format == 'engine':
            # TensorRT (for NVIDIA GPUs)
            print("Exporting to TensorRT...")
            exported_model = self.model.export(format='engine', imgsz=self.image_size, half=True)
            print(f"✓ TensorRT model exported: {exported_model}")
        
        return str(save_path)

def main():
    parser = argparse.ArgumentParser(description='Train YOLOv11 stain detection model')
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to config file')
    parser.add_argument('--data-path', type=str, default='datasets/processed', help='Path to dataset')
    parser.add_argument('--export', type=str, default='pt', choices=['pt', 'onnx', 'tflite', 'engine'],
                       help='Export format after training')
    parser.add_argument('--resume', type=str, help='Resume training from checkpoint')
    args = parser.parse_args()
    
    trainer = YOLOv11StainDetector(args.config)
    trainer.check_device()
    trainer.build_model()
    
    # Resume training if checkpoint provided
    if args.resume:
        print(f"\nResuming training from: {args.resume}")
        trainer.model = YOLO(args.resume)
    
    trainer.train(args.data_path)
    trainer.save_model(export_format=args.export)
    
    print("\n" + "="*60)
    print("YOLOv11 Training Pipeline Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Evaluate model: python scripts/evaluate_yolov11.py")
    print("2. Run inference: python scripts/inference_yolov11.py --model <model_path> --image <image_path>")

if __name__ == '__main__':
    main()
