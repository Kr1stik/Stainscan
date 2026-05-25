"""
Auto-organize and train YOLOv11 on annotated datasets
Handles multiple dataset formats and organizes them for training.
"""

import os
import shutil
import yaml
from pathlib import Path
import argparse
from ultralytics import YOLO
import subprocess
import sys

class DatasetOrganizer:
    def __init__(self, config_path='config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.classes = self.config['classes']
        self.raw_path = Path(self.config['dataset']['raw_path'])
        self.processed_path = Path(self.config['dataset']['processed_path'])
    
    def detect_dataset_format(self):
        """Detect the format of your uploaded datasets."""
        print("\n" + "="*60)
        print("DETECTING DATASET FORMAT")
        print("="*60)
        
        if not self.raw_path.exists():
            print(f"⚠ Raw dataset path not found: {self.raw_path}")
            return None
        
        # Check for class folders
        class_folders = [d for d in self.raw_path.iterdir() if d.is_dir()]
        
        if class_folders:
            print(f"✓ Found {len(class_folders)} class folders")
            for cf in class_folders:
                images = list(cf.glob('*.[jJ][pP]*')) + list(cf.glob('*.[pP][nN][gG]'))
                print(f"  - {cf.name}: {len(images)} images")
            return 'class_folders'
        
        # Check for flat structure
        images = list(self.raw_path.glob('*.[jJ][pP]*')) + list(self.raw_path.glob('*.[pP][nN][gG]'))
        if images:
            print(f"✓ Found {len(images)} images in flat structure")
            return 'flat'
        
        print("✗ No images found in raw dataset path")
        return None
    
    def organize_class_folders(self):
        """Organize images that are already in class folders."""
        print("\n" + "="*60)
        print("ORGANIZING DATASET FROM CLASS FOLDERS")
        print("="*60)
        
        # Create processed directory structure
        for split in ['train', 'val', 'test']:
            split_dir = self.processed_path / split
            split_dir.mkdir(parents=True, exist_ok=True)
            for cls in self.classes:
                (split_dir / cls).mkdir(parents=True, exist_ok=True)
        
        total_images = 0
        
        # Process each class folder
        for cls in self.classes:
            cls_path = self.raw_path / cls
            if not cls_path.exists():
                print(f"⚠ Skipping: {cls} folder not found")
                continue
            
            images = list(cls_path.glob('*.[jJ][pP]*')) + list(cls_path.glob('*.[pP][nN][gG]'))
            
            if not images:
                print(f"⚠ No images in: {cls}")
                continue
            
            print(f"\nProcessing {cls}: {len(images)} images")
            
            # If it's already split (train/val/test folders inside class)
            if (cls_path / 'train').exists() or (cls_path / 'val').exists():
                self._copy_presplit_data(cls_path, cls)
            else:
                # Auto-split the images
                self._auto_split_images(images, cls)
            
            total_images += len(images)
        
        print(f"\n✓ Total images organized: {total_images}")
        return True
    
    def _copy_presplit_data(self, cls_path, cls_name):
        """Copy pre-split data (if already organized in train/val/test)."""
        for split in ['train', 'val', 'test']:
            split_src = cls_path / split
            if split_src.exists():
                images = list(split_src.glob('*.[jJ][pP]*')) + list(split_src.glob('*.[pP][nN][gG]'))
                for img in images:
                    dst = self.processed_path / split / cls_name / img.name
                    shutil.copy2(img, dst)
                    print(f"  ✓ {split}/{cls_name}/{img.name}")
    
    def _auto_split_images(self, images, cls_name):
        """Auto-split images into train/val/test."""
        from sklearn.model_selection import train_test_split
        
        train_split = self.config['dataset']['train_split']
        val_split = self.config['dataset']['val_split']
        test_split = self.config['dataset']['test_split']
        
        # Split
        train_val, test = train_test_split(images, test_size=test_split, random_state=42)
        train, val = train_test_split(train_val, test_size=val_split/(train_split + val_split), random_state=42)
        
        splits = {'train': train, 'val': val, 'test': test}
        
        for split, imgs in splits.items():
            for img in imgs:
                dst = self.processed_path / split / cls_name / img.name
                shutil.copy2(img, dst)
    
    def organize_flat_structure(self):
        """Organize images from flat folder - user must label them."""
        print("\n" + "="*60)
        print("FLAT STRUCTURE DETECTED")
        print("="*60)
        print("\n⚠ Images are in a flat folder, not organized by class.")
        print("\nTo use your dataset, you need to organize it like this:")
        print(f"\n{self.raw_path}/")
        for cls in self.classes:
            print(f"  {cls}/")
            print(f"    image1.jpg")
            print(f"    image2.jpg")
        
        print("\nOptions:")
        print("1. Manually organize your images into class folders")
        print("2. If you have YOLO annotations, run the annotation parser")
        print("3. Use a labeling tool (Roboflow, LabelImg, etc.)")
        
        return False
    
    def verify_organization(self):
        """Verify the organized dataset."""
        print("\n" + "="*60)
        print("VERIFYING ORGANIZED DATASET")
        print("="*60)
        
        for split in ['train', 'val', 'test']:
            split_path = self.processed_path / split
            if not split_path.exists():
                continue
            
            print(f"\n{split.upper()}:")
            total = 0
            for cls in self.classes:
                cls_path = split_path / cls
                if cls_path.exists():
                    images = list(cls_path.glob('*.[jJ][pP]*')) + list(cls_path.glob('*.[pP][nN][gG]'))
                    count = len(images)
                    total += count
                    if count > 0:
                        print(f"  {cls:15} - {count:4} images")
            print(f"  {'TOTAL':15} - {total:4} images")
        
        return True

class YOLOv11Trainer:
    def __init__(self, config_path='config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.epochs = self.config['training']['epochs']
        self.batch_size = self.config['training']['batch_size']
        self.model_size = self.config['training']['model_size']
        self.learning_rate = self.config['training']['learning_rate']
        self.patience = self.config['training']['patience']
        self.device = self.config['training']['device']
        self.image_size = self.config['preprocessing']['image_size'][0]
    
    def train(self, data_path):
        """Train YOLOv11 model."""
        print("\n" + "="*60)
        print("STARTING YOLOV11 TRAINING")
        print("="*60)
        
        print("\nTraining Configuration:")
        print(f"  Model: YOLOv11-{self.model_size}")
        print(f"  Epochs: {self.epochs}")
        print(f"  Batch Size: {self.batch_size}")
        print(f"  Learning Rate: {self.learning_rate}")
        print(f"  Image Size: {self.image_size}x{self.image_size}")
        print(f"  Device: {self.device}")
        print(f"  Data Path: {data_path}")
        
        # Load model
        model_map = {
            'n': 'yolov11n-cls',
            's': 'yolov11s-cls',
            'm': 'yolov11m-cls',
            'l': 'yolov11l-cls',
            'x': 'yolov11x-cls',
        }
        
        model_name = model_map.get(self.model_size, 'yolov11m-cls')
        
        print(f"\nLoading base model: {model_name}")
        model = YOLO(f"{model_name}.pt")
        
        print("\nStarting training...\n")
        
        # Train
        results = model.train(
            data=str(data_path),
            epochs=self.epochs,
            imgsz=self.image_size,
            batch=self.batch_size,
            device=self.device,
            patience=self.patience,
            project=self.config['output']['project'],
            name=self.config['model']['name'],
            save=True,
            exist_ok=False,
            verbose=True,
            hsv_h=self.config['augmentation']['hsv_h'],
            hsv_s=self.config['augmentation']['hsv_s'],
            hsv_v=self.config['augmentation']['hsv_v'],
            degrees=self.config['augmentation']['degrees'],
            translate=self.config['augmentation']['translate'],
            scale=self.config['augmentation']['scale'],
            flipud=self.config['augmentation']['flipud'],
            fliplr=self.config['augmentation']['fliplr'],
            lr0=self.learning_rate,
        )
        
        print("\n" + "="*60)
        print("✓ TRAINING COMPLETE!")
        print("="*60)
        print(f"\nModel saved to:")
        print(f"  runs/classify/{self.config['model']['name']}/weights/best.pt")
        
        return results

def main():
    parser = argparse.ArgumentParser(description='Organize datasets and train YOLOv11')
    parser.add_argument('--config', type=str, default='config.yaml', help='Config file')
    parser.add_argument('--skip-organize', action='store_true', help='Skip organization, train directly')
    parser.add_argument('--verify-only', action='store_true', help='Only verify, don\'t train')
    args = parser.parse_args()
    
    # Step 1: Organize dataset
    organizer = DatasetOrganizer(args.config)
    
    if not args.skip_organize:
        format_type = organizer.detect_dataset_format()
        
        if format_type == 'class_folders':
            organizer.organize_class_folders()
        elif format_type == 'flat':
            organizer.organize_flat_structure()
            return
        else:
            print("\n✗ No valid datasets found!")
            print(f"Expected path: {organizer.raw_path}")
            return
    
    # Step 2: Verify organization
    organizer.verify_organization()
    
    if args.verify_only:
        print("\n✓ Verification complete. Ready to train!")
        return
    
    # Step 3: Train model
    print("\n" + "="*60)
    response = input("Ready to start training? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("Training cancelled.")
        return
    
    trainer = YOLOv11Trainer(args.config)
    trainer.train(organizer.processed_path)
    
    print("\n📊 Next Steps:")
    print("1. Evaluate: python scripts/evaluate_yolov11.py")
    print("2. Inference: python scripts/inference_yolov11.py --model <model_path> --image <image>")

if __name__ == '__main__':
    main()
