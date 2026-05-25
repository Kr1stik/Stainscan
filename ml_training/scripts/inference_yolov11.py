"""
YOLOv11 Inference Script
Run predictions on images using trained YOLOv11 model.
"""

import yaml
import argparse
import json
from pathlib import Path
from ultralytics import YOLO
import cv2
import numpy as np

class YOLOv11Inference:
    def __init__(self, model_path, config_path='config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.model = YOLO(model_path)
        self.classes = self.config['classes']
        self.image_size = self.config['preprocessing']['image_size'][0]
        self.task = self.config['training']['task']
        
        print(f"✓ Model loaded: {model_path}")
        print(f"  Task: {self.task}")
        print(f"  Classes: {len(self.classes)}")
    
    def predict_single(self, image_path, confidence_threshold=0.0, top_k=3):
        """
        Predict stain type for single image.
        
        Args:
            image_path: Path to image
            confidence_threshold: Minimum confidence score
            top_k: Return top K predictions
        
        Returns:
            Dictionary with predictions
        """
        print(f"\nAnalyzing: {image_path}")
        
        # Run inference
        results = self.model.predict(
            source=image_path,
            imgsz=self.image_size,
            conf=confidence_threshold,
            verbose=False
        )
        
        predictions = []
        
        if self.task == 'classify':
            # Classification task
            for result in results:
                if result.probs is not None:
                    # Get top predictions
                    top_indices = np.argsort(result.probs.data.cpu().numpy())[::-1][:top_k]
                    
                    for idx in top_indices:
                        confidence = float(result.probs.data[idx])
                        if confidence >= confidence_threshold:
                            predictions.append({
                                'class': self.classes[idx],
                                'confidence': round(confidence, 4),
                                'percentage': f"{confidence*100:.2f}%"
                            })
        
        elif self.task == 'detect':
            # Detection task
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        if conf >= confidence_threshold:
                            predictions.append({
                                'class': self.classes[cls_id] if cls_id < len(self.classes) else f'class_{cls_id}',
                                'confidence': round(conf, 4),
                                'percentage': f"{conf*100:.2f}%",
                                'bbox': [round(x, 2) for x in box.xyxy[0].tolist()]
                            })
        
        return {
            'image': str(image_path),
            'task': self.task,
            'predictions': predictions
        }
    
    def predict_batch(self, image_dir, output_json=None, confidence_threshold=0.0):
        """
        Predict on all images in directory.
        
        Args:
            image_dir: Directory containing images
            output_json: Save results to JSON file
            confidence_threshold: Minimum confidence
        """
        image_dir = Path(image_dir)
        results = {}
        
        image_files = list(image_dir.glob('*.[jJ][pP]*')) + \
                     list(image_dir.glob('*.[pP][nN][gG]'))
        
        print(f"\nProcessing {len(image_files)} images...")
        
        for img_file in image_files:
            try:
                result = self.predict_single(str(img_file), confidence_threshold)
                results[img_file.name] = result['predictions']
                print(f"  ✓ {img_file.name}")
                
                # Print predictions
                if result['predictions']:
                    for pred in result['predictions']:
                        print(f"    → {pred['class']:15} ({pred['percentage']})")
                else:
                    print(f"    → No detections")
            
            except Exception as e:
                print(f"  ✗ {img_file.name}: {str(e)}")
                results[img_file.name] = {'error': str(e)}
        
        if output_json:
            with open(output_json, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n✓ Results saved to: {output_json}")
        
        return results
    
    def predict_with_visualization(self, image_path, output_path=None):
        """
        Predict and visualize results on image.
        
        Args:
            image_path: Path to input image
            output_path: Path to save annotated image
        """
        print(f"\nProcessing image: {image_path}")
        
        # Run inference with visualization
        results = self.model.predict(
            source=image_path,
            imgsz=self.image_size,
            verbose=False,
            save=False
        )
        
        if len(results) > 0:
            result = results[0]
            
            # For classification, create simple annotation
            if self.task == 'classify' and result.probs is not None:
                img = cv2.imread(str(image_path))
                if img is not None:
                    height, width = img.shape[:2]
                    
                    # Add predictions as text
                    top_idx = result.probs.top1
                    top_conf = result.probs.top1conf
                    
                    text = f"{self.classes[top_idx]}: {top_conf:.2%}"
                    cv2.putText(img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    if output_path is None:
                        output_path = Path(image_path).stem + '_annotated.jpg'
                    
                    cv2.imwrite(str(output_path), img)
                    print(f"✓ Annotated image saved: {output_path}")
            
            # For detection, visualization is automatic
            elif self.task == 'detect':
                # The model.predict with save=True would save visualizations
                results_with_vis = self.model.predict(
                    source=image_path,
                    imgsz=self.image_size,
                    verbose=False,
                    save=True,
                    project='inference_output',
                    name='results'
                )
                print(f"✓ Visualized results saved to: inference_output/results/")

def main():
    parser = argparse.ArgumentParser(description='Run YOLOv11 inference for stain detection')
    parser.add_argument('--model', type=str, required=True, help='Path to trained model')
    parser.add_argument('--image', type=str, help='Path to single image')
    parser.add_argument('--batch', type=str, help='Path to image directory for batch inference')
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to config file')
    parser.add_argument('--output', type=str, help='Output JSON file for results')
    parser.add_argument('--confidence', type=float, default=0.0, help='Confidence threshold')
    parser.add_argument('--visualize', action='store_true', help='Save visualized predictions')
    args = parser.parse_args()
    
    if not (args.image or args.batch):
        parser.print_help()
        return
    
    inference = YOLOv11Inference(args.model, args.config)
    
    if args.image:
        print("\n" + "="*60)
        print("SINGLE IMAGE PREDICTION")
        print("="*60)
        result = inference.predict_single(args.image, confidence_threshold=args.confidence)
        print(f"\n{'Class':<20} {'Confidence':<15} {'Percentage':<15}")
        print("-" * 50)
        for pred in result['predictions']:
            print(f"{pred['class']:<20} {pred['confidence']:<15} {pred['percentage']:<15}")
        
        if args.visualize:
            inference.predict_with_visualization(args.image)
    
    if args.batch:
        print("\n" + "="*60)
        print("BATCH PREDICTION")
        print("="*60)
        inference.predict_batch(args.batch, args.output, args.confidence)

if __name__ == '__main__':
    main()
