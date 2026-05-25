#!/usr/bin/env python3
"""
Combine all stain datasets into a single YOLO dataset with adjusted class indices.
"""

import os
import shutil
from pathlib import Path
import argparse

def combine_datasets():
    base_path = Path("datasets")
    processed_path = base_path / "processed"
    
    # Dataset mappings: folder -> (class_index, image_folder_name)
    datasets = {
        "Cooking Oil_Stains YOLO1.1": (0, "Cooking Oil_cotton"),  # oil -> 0
        "Mud_Cotton_StainsYOLO1.1": (1, "Mud Oil_cotton"),        # mud -> 1  
        "Ballpen_Ink_Cotton": (2, "Ballpen Ink_cotton")           # ink -> 2
    }
    
    # Create combined folders
    combined_train = processed_path / "combined_train"
    combined_val = processed_path / "combined_val"
    
    combined_train.mkdir(exist_ok=True)
    combined_val.mkdir(exist_ok=True)
    
    total_images = 0
    
    for dataset_folder, (class_idx, image_folder) in datasets.items():
        dataset_path = processed_path / dataset_folder
        image_source = base_path / "raw" / image_folder
        
        if not dataset_path.exists():
            print(f"Warning: {dataset_path} not found, skipping")
            continue
            
        if not image_source.exists():
            print(f"Warning: Image source {image_source} not found, skipping")
            continue
            
        # Find the obj_train_data folder
        obj_folder = None
        for item in dataset_path.iterdir():
            if item.is_dir() and "obj" in item.name.lower():
                obj_folder = item
                break
        
        if obj_folder is None:
            print(f"Warning: No obj folder found in {dataset_path}")
            continue
            
        print(f"Processing {dataset_folder} (class {class_idx}) from {image_source}...")
        
        # Copy images and adjust annotations
        image_count = 0
        for txt_file in obj_folder.glob("*.txt"):
            # Find corresponding image
            image_path = None
            for ext in [".png", ".jpg", ".jpeg"]:
                test_path = image_source / (txt_file.stem + ext)
                if test_path.exists():
                    image_path = test_path
                    break
            
            if image_path is None:
                print(f"Warning: Image not found for {txt_file.stem} in {image_source}")
                continue
                
            # Copy image to combined_train
            shutil.copy2(image_path, combined_train / image_path.name)
            
            # Adjust annotation class indices
            with open(txt_file, 'r') as f:
                lines = f.readlines()
            
            adjusted_lines = []
            for line in lines:
                parts = line.strip().split()
                if parts:
                    # Replace class index
                    parts[0] = str(class_idx)
                    adjusted_lines.append(' '.join(parts) + '\n')
            
            # Save adjusted annotation
            with open(combined_train / txt_file.name, 'w') as f:
                f.writelines(adjusted_lines)
                
            image_count += 1
        
        print(f"  Added {image_count} images from {dataset_folder}")
        total_images += image_count
    
    # For now, use same data for val (you can split later if needed)
    for item in combined_train.iterdir():
        if item.is_file():
            shutil.copy2(item, combined_val / item.name)
    
    print(f"\nCombined dataset created!")
    print(f"Total images: {total_images}")
    print(f"Train folder: {combined_train}")
    print(f"Val folder: {combined_val}")

if __name__ == "__main__":
    combine_datasets()