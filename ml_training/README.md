# Stain Detection ML Training Pipeline

Complete machine learning pipeline for training a stain detection model using TensorFlow.

## Directory Structure

```
ml_training/
├── datasets/
│   ├── raw/                    # Raw images organized by class
│   │   ├── coffee/
│   │   ├── wine/
│   │   ├── blood/
│   │   ├── grass/
│   │   ├── oil/
│   │   ├── ink/
│   │   ├── chocolate/
│   │   └── makeup/
│   └── processed/              # Processed images ready for training
│       ├── train/
│       ├── val/
│       └── test/
├── scripts/
│   ├── prepare_dataset.py      # Data preparation script
│   ├── train_model.py          # Model training script
│   ├── evaluate_model.py       # Model evaluation script
│   └── inference.py            # Inference on new images
├── models/                      # Trained model weights
├── logs/                        # TensorBoard logs
├── metrics/                     # Performance metrics
├── plots/                       # Training plots and visualizations
├── config.yaml                 # Configuration file
└── requirements.txt            # Python dependencies
```

## Setup Instructions

### 1. Install Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Prepare Dataset

#### Option A: Using Directory Structure

1. Create subdirectories in `datasets/raw/` for each stain type
2. Place your stain images in the corresponding class folders:
   ```
   datasets/raw/
   ├── coffee/
   │   ├── image1.jpg
   │   ├── image2.jpg
   │   └── ...
   ├── wine/
   │   ├── image1.jpg
   │   ├── image2.jpg
   │   └── ...
   └── ... (other stain types)
   ```

3. Run data preparation script:
   ```bash
   python scripts/prepare_dataset.py --format directory
   ```

#### Option B: Using Numpy Format

If you have your data in numpy arrays:

```bash
python scripts/prepare_dataset.py --format numpy
```

The script will:
- Validate all images
- Resize images to 224x224 pixels
- Split data into train/val/test (70/15/15)
- Save processed data

### 3. Train Model

```bash
# Basic training with default settings
python scripts/train_model.py

# Custom configuration
python scripts/train_model.py --config config.yaml --data-path datasets/processed
```

**Configuration Options** (edit `config.yaml`):
- `model_type`: `efficientnet` (recommended), `resnet50`, or `mobilenet`
- `epochs`: Number of training epochs
- `batch_size`: Batch size for training
- `learning_rate`: Learning rate for optimizer
- `augmentation`: Enable/disable data augmentation
- Early stopping patience and other hyperparameters

**Training Output:**
- Model weights saved to `models/`
- TensorBoard logs in `logs/`
- Training history plot in `plots/training_history.png`

### 4. Evaluate Model

```bash
# Auto-detect latest model
python scripts/evaluate_model.py --data-path datasets/processed

# Use specific model
python scripts/evaluate_model.py --model models/model.h5 --data-path datasets/processed
```

**Evaluation Metrics:**
- Accuracy and Top-3 Accuracy
- Confusion Matrix (saved as PNG)
- Classification Report (Precision, Recall, F1-Score)
- Class Distribution visualization

### 5. Run Inference

```bash
# Single image prediction
python scripts/inference.py --model models/latest_model.h5 --image path/to/image.jpg

# Batch prediction on directory
python scripts/inference.py --model models/latest_model.h5 --batch path/to/images/ --output results.json
```

## Data Requirements

### Minimum Dataset Size
- **Per class**: At least 50 images (100+ recommended)
- **Total**: Minimum 400 images for 8 classes

### Image Quality Requirements
- **Format**: JPG, PNG, or JPEG
- **Size**: Can be any size (will be resized to 224x224)
- **Color**: RGB (black & white may work but color is preferred)
- **Quality**: Clear, well-lit images for best results

### Best Practices
1. **Balance**: Keep roughly equal number of images per class
2. **Variety**: Include images with different lighting, angles, and backgrounds
3. **Cleanliness**: Remove corrupted or mislabeled images
4. **Augmentation**: The pipeline includes automatic augmentation (rotation, flip, zoom)

## Configuration Guide

### Key Parameters in `config.yaml`

**Model Architecture:**
```yaml
training:
  model_type: "efficientnet"  # Lighter: mobilenet, Standard: efficientnet, Heavier: resnet50
  epochs: 50                   # Increase for better accuracy, decrease for faster training
  batch_size: 32              # Increase if you have GPU memory
  learning_rate: 0.001        # Lower = slower but potentially better convergence
```

**Data Augmentation:**
```yaml
augmentation:
  enabled: true               # Enable/disable augmentation
  rotation_range: 20         # Degrees for random rotation
  width_shift_range: 0.2     # Fraction of width to shift
  horizontal_flip: true      # Flip images horizontally
```

**Output Format:**
```yaml
model:
  format: "h5"               # Options: h5 (Keras), savedmodel, tflite (mobile)
```

## Model Formats

### H5 Format (Recommended for Development)
- Standard Keras format
- Smaller file size
- Fast loading
- Use: `format: "h5"`

### SavedModel Format (Recommended for Production)
- TensorFlow native format
- Better for deployment
- Version control
- Use: `format: "savedmodel"`

### TFLite Format (For Mobile/Edge)
- Optimized for mobile devices
- Reduced size (50-80% smaller)
- Faster inference on mobile
- Use: `format: "tflite"` in config and convert with inference script

## Monitoring Training

### TensorBoard Visualization
```bash
tensorboard --logdir logs/
```

Then open http://localhost:6006 in browser to monitor:
- Loss and accuracy curves
- Histogram of weights/biases
- Training time

## Troubleshooting

### Out of Memory (GPU)
- Reduce `batch_size` in config.yaml
- Use smaller model (`mobilenet` instead of `resnet50`)
- Reduce image resolution (224x224 is already optimized)

### Poor Model Performance
- Increase dataset size
- Enable augmentation (check `augmentation.enabled`)
- Train for more epochs
- Verify image quality in dataset
- Check class balance

### Images Not Loading
- Verify image format (JPG, PNG, JPEG only)
- Check file permissions
- Ensure correct directory structure
- Use validation script: `python scripts/prepare_dataset.py` to identify invalid images

## Integration with Flutter App

After training, convert and integrate the model:

1. **Export to TFLite** (for on-device inference):
   ```bash
   # Update config.yaml with format: "tflite"
   python scripts/train_model.py
   ```

2. **Copy model to Flutter app**:
   ```bash
   cp models/stain_detection_model.tflite ../stain_scanner/assets/models/
   ```

3. **Update image_analysis_service.dart** to use the trained model instead of random predictions

## Performance Metrics

Typical results on a balanced dataset (100 images per class):
- **Accuracy**: 85-95%
- **Training time**: 10-30 minutes (GPU)
- **Model size**: 50-150 MB (depending on format)
- **Inference time**: <500ms per image

## Advanced Usage

### Custom Data Split
Edit `config.yaml`:
```yaml
dataset:
  train_split: 0.7   # 70% training
  val_split: 0.15   # 15% validation
  test_split: 0.15  # 15% testing
```

### Fine-tuning Existing Model
Uncomment in `train_model.py` after loading base model:
```python
base_model.trainable = True  # Instead of False
```

### Custom Model Architecture
Edit the model building section in `train_model.py` to add/modify layers.

## References

- TensorFlow: https://www.tensorflow.org/
- EfficientNet: https://arxiv.org/abs/1905.11946
- Data Augmentation: https://www.tensorflow.org/tutorials/images/data_augmentation
