"""
Dataset preparation script for stain detection model.
Handles image loading, validation, and splitting into train/val/test sets.
"""

import os
import cv2
import numpy as np
import yaml
from pathlib import Path
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import shutil
import json
from PIL import Image
import argparse

class DatasetPreparer:
    def __init__(self, config_path='config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.raw_path = Path(self.config['dataset']['raw_path'])
        self.processed_path = Path(self.config['dataset']['processed_path'])
        self.classes = self.config['classes']
        self.image_size = tuple(self.config['preprocessing']['image_size'])
        
    def validate_dataset_structure(self):
        """Validate that dataset has correct structure."""
        print("Validating dataset structure...")
        
        if not self.raw_path.exists():
            print(f"Error: Raw dataset path '{self.raw_path}' does not exist.")
            print("Please create the following structure:")
            print(f"{self.raw_path}/")
            for cls in self.classes:
                print(f"  {cls}/")
                print(f"    image1.jpg")
                print(f"    image2.jpg")
            return False
        
        for cls in self.classes:
            cls_path = self.raw_path / cls
            if not cls_path.exists():
                print(f"Warning: Class folder '{cls}' not found.")
            else:
                images = list(cls_path.glob('*.[jJ][pP][gG]')) + \
                         list(cls_path.glob('*.[pP][nN][gG]')) + \
                         list(cls_path.glob('*.[jJ][pP][eE][gG]'))
                print(f"  {cls}: {len(images)} images found")
        
        return True
    
    def is_valid_image(self, image_path):
        """Check if image is valid and readable."""
        try:
            img = Image.open(image_path)
            img.verify()
            return True
        except Exception as e:
            print(f"Invalid image: {image_path} - {str(e)}")
            return False
    
    def load_and_resize_image(self, image_path):
        """Load and resize image to standard size."""
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                return None
            
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, self.image_size, interpolation=cv2.INTER_LANCZOS4)
            return img
        except Exception as e:
            print(f"Error loading image {image_path}: {str(e)}")
            return None
    
    def prepare_dataset(self, output_format='numpy'):
        """
        Prepare dataset by loading, validating, and splitting images.
        
        Args:
            output_format: 'numpy' for numpy arrays, 'directory' for organized directories
        """
        print("\n" + "="*60)
        print("PREPARING DATASET")
        print("="*60)
        
        if not self.validate_dataset_structure():
            return False
        
        # Create output directories
        self.processed_path.mkdir(parents=True, exist_ok=True)
        
        if output_format == 'directory':
            self._prepare_directory_format()
        else:
            self._prepare_numpy_format()
        
        print("\n" + "="*60)
        print("Dataset preparation complete!")
        print("="*60)
        return True
    
    def _prepare_directory_format(self):
        """Prepare dataset in directory structure (train/val/test)."""
        splits = ['train', 'val', 'test']
        for split in splits:
            split_path = self.processed_path / split
            for cls in self.classes:
                (split_path / cls).mkdir(parents=True, exist_ok=True)
        
        train_split = self.config['dataset']['train_split']
        val_split = self.config['dataset']['val_split']
        
        total_images = 0
        valid_images = 0
        stats = {cls: {'total': 0, 'valid': 0, 'invalid': 0} for cls in self.classes}
        
        for cls in self.classes:
            cls_path = self.raw_path / cls
            if not cls_path.exists():
                continue
            
            image_files = list(cls_path.glob('*.[jJ][pP]*')) + list(cls_path.glob('*.[pP][nN][gG]'))
            
            if not image_files:
                print(f"No images found for class: {cls}")
                continue
            
            print(f"\nProcessing class: {cls}")
            valid_files = []
            
            # Validate images
            for img_file in tqdm(image_files, desc=f"Validating {cls}"):
                if self.is_valid_image(img_file):
                    valid_files.append(img_file)
                    stats[cls]['valid'] += 1
                else:
                    stats[cls]['invalid'] += 1
                total_images += 1
            
            valid_images += len(valid_files)
            stats[cls]['total'] = len(valid_files)
            
            # Split dataset
            train_val, test = train_test_split(valid_files, test_size=val_split + self.config['dataset']['test_split'],
                                               random_state=42)
            train, val = train_test_split(train_val, 
                                         test_size=val_split/(train_split + val_split),
                                         random_state=42)
            
            # Copy files to split directories
            splits_data = {
                'train': train,
                'val': val,
                'test': test
            }
            
            for split, files in splits_data.items():
                for img_file in tqdm(files, desc=f"Copying {split}/{cls}"):
                    img = self.load_and_resize_image(img_file)
                    if img is not None:
                        output_path = self.processed_path / split / cls / img_file.name
                        cv2.imwrite(str(output_path), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        
        # Print statistics
        print("\n" + "="*60)
        print("DATASET STATISTICS")
        print("="*60)
        for cls in self.classes:
            print(f"{cls:15} - Total: {stats[cls]['total']:4}  Valid: {stats[cls]['valid']:4}  Invalid: {stats[cls]['invalid']:4}")
        print(f"{'TOTAL':15} - {total_images:4} images ({valid_images:4} valid, {total_images-valid_images:4} invalid)")
    
    def _prepare_numpy_format(self):
        """Prepare dataset as numpy arrays."""
        print("Preparing dataset in numpy format...")
        
        images = []
        labels = []
        class_mapping = {cls: idx for idx, cls in enumerate(self.classes)}
        
        for cls in self.classes:
            cls_path = self.raw_path / cls
            if not cls_path.exists():
                continue
            
            image_files = list(cls_path.glob('*.[jJ][pP]*')) + list(cls_path.glob('*.[pP][nN][gG]'))
            
            for img_file in tqdm(image_files, desc=f"Loading {cls}"):
                img = self.load_and_resize_image(img_file)
                if img is not None:
                    images.append(img)
                    labels.append(class_mapping[cls])
        
        images = np.array(images, dtype=np.uint8)
        labels = np.array(labels, dtype=np.int32)
        
        # Split dataset
        X_train, X_temp, y_train, y_temp = train_test_split(
            images, labels, test_size=0.3, random_state=42, stratify=labels
        )
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
        )
        
        # Save numpy arrays
        np.save(self.processed_path / 'X_train.npy', X_train)
        np.save(self.processed_path / 'y_train.npy', y_train)
        np.save(self.processed_path / 'X_val.npy', X_val)
        np.save(self.processed_path / 'y_val.npy', y_val)
        np.save(self.processed_path / 'X_test.npy', X_test)
        np.save(self.processed_path / 'y_test.npy', y_test)
        
        # Save class mapping
        with open(self.processed_path / 'class_mapping.json', 'w') as f:
            json.dump(class_mapping, f, indent=2)
        
        print(f"\nDataset splits:")
        print(f"  Train: {X_train.shape}")
        print(f"  Val:   {X_val.shape}")
        print(f"  Test:  {X_test.shape}")

def main():
    parser = argparse.ArgumentParser(description='Prepare dataset for stain detection model')
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to config file')
    parser.add_argument('--format', type=str, default='directory', choices=['directory', 'numpy'],
                       help='Output format')
    args = parser.parse_args()
    
    preparer = DatasetPreparer(args.config)
    preparer.prepare_dataset(output_format=args.format)

if __name__ == '__main__':
    main()
