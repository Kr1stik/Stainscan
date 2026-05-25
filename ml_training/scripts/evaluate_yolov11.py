"""
YOLOv11 Model Evaluation Script
Evaluates YOLOv11 stain detection model performance.
"""

import yaml
import argparse
from pathlib import Path
from ultralytics import YOLO
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import json

class YOLOv11Evaluator:
    def __init__(self, config_path='config.yaml', model_path=None):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.classes = self.config['classes']
        self.image_size = self.config['preprocessing']['image_size'][0]
        self.batch_size = self.config['training']['batch_size']
        self.task = self.config['training']['task']
        
        if model_path is None:
            # Find latest model
            runs_dir = Path(self.config['output']['logs_dir'])
            if runs_dir.exists():
                latest_run = sorted(runs_dir.glob('*'), key=lambda x: x.stat().st_mtime)[-1]
                model_path = latest_run / 'weights' / 'best.pt'
        
        if isinstance(model_path, str):
            model_path = Path(model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        self.model = YOLO(str(model_path))
        print(f"✓ Model loaded from: {model_path}")
    
    def evaluate(self, data_path):
        """Evaluate model on validation/test set."""
        print("\n" + "="*60)
        print("EVALUATING MODEL")
        print("="*60)
        
        results = self.model.val(
            data=str(data_path),
            imgsz=self.image_size,
            batch=self.batch_size,
            device=0,
            verbose=True,
            save_json=True
        )
        
        print("\n" + "="*60)
        print("EVALUATION RESULTS")
        print("="*60)
        
        # Print metrics
        if hasattr(results, 'results_dict'):
            for key, value in results.results_dict.items():
                if isinstance(value, (int, float)):
                    print(f"{key:20} : {value:.4f}")
        
        return results
    
    def generate_confusion_matrix(self, data_path):
        """Generate confusion matrix from validation predictions."""
        print("\nGenerating confusion matrix...")
        
        # Run predictions on validation set
        val_path = Path(data_path) / 'val'
        
        true_labels = []
        pred_labels = []
        
        # Get all class folders
        for class_idx, cls in enumerate(self.classes):
            cls_path = val_path / cls
            if cls_path.exists():
                for img_path in cls_path.glob('*.[jJ][pP]*'):
                    true_labels.append(class_idx)
                    
                    # Predict
                    results = self.model.predict(str(img_path), verbose=False)
                    if len(results) > 0:
                        pred_class = results[0].probs.top1
                        pred_labels.append(pred_class)
        
        if true_labels and pred_labels:
            cm = confusion_matrix(true_labels, pred_labels)
            
            # Plot confusion matrix
            plt.figure(figsize=(12, 10))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                       xticklabels=self.classes,
                       yticklabels=self.classes,
                       cbar_kws={'label': 'Count'})
            plt.title('Confusion Matrix - YOLOv11 Stain Detection')
            plt.ylabel('True Label')
            plt.xlabel('Predicted Label')
            plt.tight_layout()
            
            plot_path = Path('plots') / 'confusion_matrix_yolov11.png'
            plot_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(str(plot_path), dpi=300, bbox_inches='tight')
            print(f"✓ Confusion matrix saved: {plot_path}")
            plt.close()
    
    def plot_results(self):
        """Plot training results if available."""
        results_file = Path(self.config['output']['logs_dir']) / self.config['model']['name'] / 'results.csv'
        
        if not results_file.exists():
            print("⚠ Results file not found. Skipping plot generation.")
            return
        
        print("\nPlotting training results...")
        
        try:
            import pandas as pd
            
            df = pd.read_csv(results_file)
            
            # Create metrics plot
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            
            # Plot 1: Accuracy
            if 'top1' in df.columns:
                axes[0, 0].plot(df['epoch'], df['top1'], label='Train Top1', marker='o')
                axes[0, 0].set_xlabel('Epoch')
                axes[0, 0].set_ylabel('Top1 Accuracy')
                axes[0, 0].set_title('Top1 Accuracy')
                axes[0, 0].legend()
                axes[0, 0].grid(True)
            
            # Plot 2: Loss
            if 'loss' in df.columns:
                axes[0, 1].plot(df['epoch'], df['loss'], label='Train Loss', marker='o', color='orange')
                axes[0, 1].set_xlabel('Epoch')
                axes[0, 1].set_ylabel('Loss')
                axes[0, 1].set_title('Training Loss')
                axes[0, 1].legend()
                axes[0, 1].grid(True)
            
            # Plot 3: Val Accuracy
            if 'val/top1' in df.columns:
                axes[1, 0].plot(df['epoch'], df['val/top1'], label='Val Top1', marker='s', color='green')
                axes[1, 0].set_xlabel('Epoch')
                axes[1, 0].set_ylabel('Top1 Accuracy')
                axes[1, 0].set_title('Validation Top1 Accuracy')
                axes[1, 0].legend()
                axes[1, 0].grid(True)
            
            # Plot 4: Val Loss
            if 'val/loss' in df.columns:
                axes[1, 1].plot(df['epoch'], df['val/loss'], label='Val Loss', marker='s', color='red')
                axes[1, 1].set_xlabel('Epoch')
                axes[1, 1].set_ylabel('Loss')
                axes[1, 1].set_title('Validation Loss')
                axes[1, 1].legend()
                axes[1, 1].grid(True)
            
            plt.tight_layout()
            
            plot_path = Path('plots') / 'training_results_yolov11.png'
            plot_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(str(plot_path), dpi=300, bbox_inches='tight')
            print(f"✓ Training results plot saved: {plot_path}")
            plt.close()
        
        except Exception as e:
            print(f"⚠ Error generating plots: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Evaluate YOLOv11 stain detection model')
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to config file')
    parser.add_argument('--model', type=str, default=None, help='Path to model weights')
    parser.add_argument('--data-path', type=str, default='datasets/processed', help='Path to dataset')
    args = parser.parse_args()
    
    evaluator = YOLOv11Evaluator(args.config, args.model)
    results = evaluator.evaluate(args.data_path)
    evaluator.generate_confusion_matrix(args.data_path)
    evaluator.plot_results()
    
    print("\n" + "="*60)
    print("Evaluation complete!")
    print("="*60)

if __name__ == '__main__':
    main()
