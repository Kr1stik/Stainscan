"""
Inference script for using trained stain detection model.
Allows real-time prediction on new images.
"""

import yaml
import numpy as np
import tensorflow as tf
import cv2
from pathlib import Path
import argparse
import json

class StainDetectionInference:
    def __init__(self, model_path, config_path='config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.model = tf.keras.models.load_model(model_path)
        self.classes = self.config['classes']
        self.image_size = tuple(self.config['preprocessing']['image_size'])
        
        print(f"Model loaded from: {model_path}")
        print(f"Classes: {self.classes}")
    
    def preprocess_image(self, image_path):
        """Load and preprocess image for inference."""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, self.image_size)
        img = img.astype('float32') / 255.0
        
        return np.expand_dims(img, axis=0)
    
    def predict(self, image_path, top_k=3, confidence_threshold=0.0):
        """
        Predict stain type for given image.
        
        Args:
            image_path: Path to image
            top_k: Return top k predictions
            confidence_threshold: Minimum confidence to report
        
        Returns:
            Dictionary with predictions
        """
        img = self.preprocess_image(image_path)
        predictions = self.model.predict(img, verbose=0)[0]
        
        # Get top predictions
        top_indices = np.argsort(predictions)[::-1][:top_k]
        
        results = {
            'image': image_path,
            'predictions': []
        }
        
        for idx in top_indices:
            confidence = float(predictions[idx])
            if confidence >= confidence_threshold:
                results['predictions'].append({
                    'class': self.classes[idx],
                    'confidence': round(confidence, 4),
                    'percentage': f"{confidence*100:.2f}%"
                })
        
        return results
    
    def predict_batch(self, image_dir, output_json=None):
        """Predict on all images in a directory."""
        image_dir = Path(image_dir)
        results = {}
        
        for img_file in image_dir.glob('*.[jJ][pP]*'):
            try:
                result = self.predict(str(img_file))
                results[img_file.name] = result['predictions']
                print(f"✓ {img_file.name}")
            except Exception as e:
                print(f"✗ {img_file.name}: {str(e)}")
        
        if output_json:
            with open(output_json, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to: {output_json}")
        
        return results

def main():
    parser = argparse.ArgumentParser(description='Run inference on stain detection model')
    parser.add_argument('--model', type=str, required=True, help='Path to trained model')
    parser.add_argument('--image', type=str, help='Path to single image for inference')
    parser.add_argument('--batch', type=str, help='Path to directory of images for batch inference')
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to config file')
    parser.add_argument('--output', type=str, help='Output JSON file for batch results')
    args = parser.parse_args()
    
    if not (args.image or args.batch):
        parser.print_help()
        return
    
    inference = StainDetectionInference(args.model, args.config)
    
    if args.image:
        print("\n" + "="*60)
        print("SINGLE IMAGE PREDICTION")
        print("="*60)
        result = inference.predict(args.image)
        print(f"\nImage: {result['image']}")
        for pred in result['predictions']:
            print(f"  {pred['class']:15} - {pred['percentage']} confidence")
    
    if args.batch:
        print("\n" + "="*60)
        print("BATCH PREDICTION")
        print("="*60)
        inference.predict_batch(args.batch, args.output)

if __name__ == '__main__':
    main()
