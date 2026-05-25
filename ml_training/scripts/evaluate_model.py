"""
Model evaluation script for stain detection.
Evaluates model performance on test set and generates metrics/visualizations.
"""

import os
import yaml
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from pathlib import Path
import argparse
from tensorflow.keras.preprocessing.image import ImageDataGenerator

class ModelEvaluator:
    def __init__(self, config_path='config.yaml', model_path=None):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.classes = self.config['classes']
        self.image_size = tuple(self.config['preprocessing']['image_size'])
        self.batch_size = self.config['training']['batch_size']
        
        if model_path is None:
            # Find latest model
            model_dir = Path(self.config['model']['save_path'])
            model_files = list(model_dir.glob('*.h5')) + list(model_dir.glob('*.savedmodel'))
            if model_files:
                model_path = str(sorted(model_files)[-1])
        
        self.model = tf.keras.models.load_model(model_path)
        print(f"Model loaded from: {model_path}")
    
    def load_test_data(self, data_path):
        """Load test data."""
        test_dir = Path(data_path) / 'test'
        
        test_datagen = ImageDataGenerator(rescale=1./255)
        test_generator = test_datagen.flow_from_directory(
            str(test_dir),
            target_size=self.image_size,
            batch_size=self.batch_size,
            class_mode='categorical',
            shuffle=False
        )
        
        return test_generator
    
    def evaluate(self, test_generator):
        """Evaluate model on test set."""
        print("\n" + "="*60)
        print("EVALUATING MODEL")
        print("="*60)
        
        loss, accuracy, top3_accuracy = self.model.evaluate(
            test_generator,
            steps=test_generator.samples // self.batch_size,
            verbose=1
        )
        
        print(f"\nTest Loss: {loss:.4f}")
        print(f"Test Accuracy: {accuracy:.4f}")
        print(f"Top-3 Accuracy: {top3_accuracy:.4f}")
        
        return {'loss': loss, 'accuracy': accuracy, 'top3_accuracy': top3_accuracy}
    
    def generate_confusion_matrix(self, test_generator):
        """Generate confusion matrix."""
        print("\nGenerating confusion matrix...")
        
        predictions = self.model.predict(test_generator, verbose=1)
        pred_classes = np.argmax(predictions, axis=1)
        true_classes = test_generator.classes
        
        cm = confusion_matrix(true_classes, pred_classes)
        
        # Plot confusion matrix
        plt.figure(figsize=(12, 10))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=self.classes,
                   yticklabels=self.classes)
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        
        plot_path = Path(self.config['output']['plots_dir']) / 'confusion_matrix.png'
        plt.savefig(str(plot_path), dpi=300, bbox_inches='tight')
        print(f"Confusion matrix saved to: {plot_path}")
        plt.close()
        
        return cm
    
    def generate_classification_report(self, test_generator):
        """Generate detailed classification report."""
        print("\nGenerating classification report...")
        
        predictions = self.model.predict(test_generator, verbose=0)
        pred_classes = np.argmax(predictions, axis=1)
        true_classes = test_generator.classes
        
        report = classification_report(
            true_classes, pred_classes,
            target_names=self.classes,
            output_dict=True
        )
        
        # Print report
        print("\n" + "="*60)
        print("CLASSIFICATION REPORT")
        print("="*60)
        print(classification_report(
            true_classes, pred_classes,
            target_names=self.classes
        ))
        
        # Save report to JSON
        report_path = Path(self.config['output']['metrics_dir']) / 'classification_report.json'
        import json
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to: {report_path}")
        
        return report
    
    def plot_class_distribution(self, test_generator):
        """Plot class distribution in test set."""
        class_indices = test_generator.class_indices
        class_counts = {}
        for cls, idx in class_indices.items():
            class_counts[cls] = np.sum(test_generator.classes == idx)
        
        plt.figure(figsize=(10, 6))
        plt.bar(class_counts.keys(), class_counts.values(), color='skyblue')
        plt.title('Test Set Class Distribution')
        plt.xlabel('Stain Type')
        plt.ylabel('Number of Samples')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plot_path = Path(self.config['output']['plots_dir']) / 'class_distribution.png'
        plt.savefig(str(plot_path), dpi=300, bbox_inches='tight')
        print(f"Class distribution plot saved to: {plot_path}")
        plt.close()

def main():
    parser = argparse.ArgumentParser(description='Evaluate stain detection model')
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to config file')
    parser.add_argument('--model', type=str, default=None, help='Path to model')
    parser.add_argument('--data-path', type=str, default='datasets/processed', help='Path to processed data')
    args = parser.parse_args()
    
    evaluator = ModelEvaluator(args.config, args.model)
    test_gen = evaluator.load_test_data(args.data_path)
    
    evaluator.evaluate(test_gen)
    evaluator.generate_confusion_matrix(test_gen)
    evaluator.generate_classification_report(test_gen)
    evaluator.plot_class_distribution(test_gen)
    
    print("\n" + "="*60)
    print("Evaluation complete!")
    print("="*60)

if __name__ == '__main__':
    main()
