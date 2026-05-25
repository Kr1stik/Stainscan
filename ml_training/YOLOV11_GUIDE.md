# YOLOv11 Training Setup - Complete Guide

## What is YOLOv11?

**YOLO** = "You Only Look Once" - A state-of-the-art real-time object detection framework.

**YOLOv11** is the latest version (2024) offering:
- ✅ **Faster training** (5-15 min vs 30-60 min)
- ✅ **Higher accuracy** (92-98% vs 85-92%)
- ✅ **Smaller models** (10-100 MB vs 50-150 MB)
- ✅ **Faster inference** (<50ms vs 100-200ms)
- ✅ **Easier to use** - Simple API with Python

## 🚀 Quick Start (Windows)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **ultralytics** - YOLOv11 framework
- **torch** - Deep learning library
- **opencv** - Image processing
- Other utilities

### Step 2: Organize Your Dataset

Create the following structure:

```
ml_training/datasets/raw/
├── coffee/          ← Put coffee stain images here
├── wine/            ← Put wine stain images here
├── blood/           
├── grass/
├── oil/
├── ink/
├── chocolate/
└── makeup/
```

**Recommended:** 100-200 images per class
**Minimum:** 50 images per class

### Step 3: Prepare Dataset

```bash
python scripts/prepare_dataset.py --format directory
```

This automatically:
- Validates all images
- Resizes to 640×640
- Splits into train/val/test (70/15/15)

Output will be in `datasets/processed/`

### Step 4: Train Model

```bash
python scripts/train_yolov11.py
```

**Output locations:**
- Model weights: `runs/classify/stain_detection_yolov11/weights/`
- Training plots: `runs/classify/stain_detection_yolov11/results.png`
- Metrics: `runs/classify/stain_detection_yolov11/results.csv`

### Step 5: Evaluate Model

```bash
python scripts/evaluate_yolov11.py
```

Generates:
- Confusion matrix visualization
- Classification metrics
- Performance plots

### Step 6: Test on Images

```bash
# Single image
python scripts/inference_yolov11.py \
    --model runs/classify/stain_detection_yolov11/weights/best.pt \
    --image path/to/image.jpg

# Multiple images
python scripts/inference_yolov11.py \
    --model runs/classify/stain_detection_yolov11/weights/best.pt \
    --batch path/to/image/folder \
    --output results.json
```

## 🎯 Model Sizes Explained

Choose based on your needs:

```
YOLOv11n (Nano)      3.3 MB    ⚡⚡⚡ FASTEST
 └─ Best for mobile phones and edge devices
 
YOLOv11s (Small)    11.2 MB    ⚡⚡ FAST
 └─ Good for real-time on moderate hardware
 
YOLOv11m (Medium)   35.3 MB    ⚡ BALANCED  ← RECOMMENDED
 └─ Great balance of speed and accuracy
 
YOLOv11l (Large)    88.3 MB    SLOWER
 └─ Better accuracy, needs more resources
 
YOLOv11x (XLarge)  335.4 MB    SLOWEST
 └─ Best accuracy, requires powerful GPU
```

**Quick Decision:**
- Mobile/Flutter app? → Use **n** or **s**
- Production server? → Use **m** or **l**
- Maximum accuracy? → Use **x**

## ⚙️ Configuration

Edit `config.yaml` to customize training:

```yaml
training:
  model_size: "m"              # n, s, m, l, x
  epochs: 100                  # Higher = better (but slower)
  batch_size: 32              # Higher = faster training (needs GPU memory)
  learning_rate: 0.01         # Usually 0.001-0.1
  patience: 20                # Stop if no improvement for 20 epochs
  device: 0                   # 0 = GPU, 'cpu' = CPU

preprocessing:
  image_size: [640, 640]      # YOLOv11 standard (don't change)

augmentation:
  enabled: true               # Auto data augmentation
  hsv_h: 0.015               # Hue shift
  hsv_s: 0.7                 # Saturation shift
  hsv_v: 0.4                 # Value shift
  degrees: 10.0              # Rotation
  translate: 0.1             # Translation
  scale: 0.5                 # Zoom
  flipud: 0.5                # Vertical flip
  fliplr: 0.5                # Horizontal flip
```

## 📊 Training Tips

### For Better Accuracy:
- Increase `epochs` to 150-200
- Collect more images (200+ per class)
- Use larger model (`model_size: "l"`)
- Ensure images are well-lit and clear

### For Faster Training:
- Use smaller model (`model_size: "n"`)
- Increase `batch_size` (16, 64, etc.)
- Reduce `epochs` (50-75)

### For Mobile Deployment:
- Use `model_size: "n"` or `"s"`
- Enable TFLite export after training
- Model will be <50 MB

## 📈 Monitoring Training

### TensorBoard (Real-time Monitoring)

```bash
# Start TensorBoard while training
tensorboard --logdir runs/classify/
```

Then open http://localhost:6006 in your browser

### Training Outputs

```
runs/classify/stain_detection_yolov11/
├── weights/
│   ├── best.pt              ← Best model (highest validation accuracy)
│   ├── last.pt              ← Last checkpoint (for resuming)
│   └── epoch*.pt            ← Checkpoints per epoch
├── results.csv              ← All metrics
├── results.png              ← Training/validation plots
├── confusion_matrix.png     ← Predictions analysis
└── ...
```

## 🔍 Understanding Results

### Training Output Example:

```
Epoch 1/100: 100%|████████████| 23/23 [00:15<00:00, 1.50/s]
  Class    Images   Instances   Box(P/R/mAP)  Cls(P/R/mAP)
  all      150      150       0.45/0.61/0.51  0.78/0.65/0.72
```

- **Box(P/R/mAP)** - Bounding box detection metrics (for detection mode)
- **Cls(P/R/mAP)** - Classification metrics
  - **P** (Precision): How many predictions are correct
  - **R** (Recall): How many actual stains were found
  - **mAP** (mean Average Precision): Overall accuracy score

### Expected Accuracy:

| Training Data | Accuracy | Notes |
|---------------|----------|-------|
| 50 images/class (400 total) | 80-85% | Minimum viable |
| 100 images/class (800 total) | 88-92% | Good performance |
| 200 images/class (1600 total) | 93-96% | Excellent results |
| 500+ images/class (4000+ total) | 96%+ | Production quality |

## 🐛 Troubleshooting

### GPU/CUDA Issues

```bash
# Check if GPU is available
python -c "import torch; print(torch.cuda.is_available())"

# If False, you may need to:
# 1. Install NVIDIA drivers
# 2. Install CUDA toolkit
# 3. Install cuDNN

# Force CPU mode in config.yaml:
training:
  device: 'cpu'
```

### Out of Memory (GPU)

```yaml
# In config.yaml, try:
training:
  batch_size: 16    # Reduce from 32
  # OR
  model_size: "s"   # Use smaller model
```

### Low Accuracy

1. **Check dataset:**
   - Are images clear and well-lit?
   - Is each class properly labeled?
   - Do you have enough images per class?

2. **Increase training:**
   ```yaml
   training:
     epochs: 200      # More iterations
     model_size: "l"  # Larger model
   ```

3. **Improve images:**
   - Collect more diverse examples
   - Include different lighting conditions
   - Vary angles and distances

### Training Too Slow

```yaml
training:
  batch_size: 64     # Increase batch size
  model_size: "n"    # Use nano model
  # Consider using GPU instead of CPU
  device: 0
```

## 📱 Mobile Deployment

### Export for Flutter/Mobile:

```bash
# After training, export to TFLite
python scripts/train_yolov11.py --export tflite

# Or manually:
# 1. Copy best.pt to your device
# 2. Use Python script to convert:
from ultralytics import YOLO
model = YOLO('best.pt')
model.export(format='tflite')
```

### Integration Steps:

1. Export model to TFLite format
2. Copy `.tflite` file to Flutter `assets/models/`
3. Update `image_analysis_service.dart` to use the model
4. Use TensorFlow Lite plugin for Flutter

## 🆚 YOLOv11 vs Previous Methods

| Feature | Transfer Learning | YOLOv11 |
|---------|------------------|---------|
| Training Time | 30-60 min | 5-15 min |
| Model Size | 50-150 MB | 10-100 MB |
| Accuracy | 85-92% | 92-98% |
| Inference Speed | 100-200ms | <50ms |
| Setup Difficulty | Moderate | Easy |
| Code Simplicity | Complex | Simple |

**Bottom line:** YOLOv11 is faster, smaller, more accurate, and easier to use!

## 📚 Files Overview

```
ml_training/
├── config.yaml                 ← Edit this for training settings
├── requirements.txt            ← Dependencies
├── README_YOLOV11.md          ← Detailed documentation
├── quickstart.bat             ← Windows menu script
├── scripts/
│   ├── prepare_dataset.py     ← Organize your images
│   ├── train_yolov11.py       ← Train the model
│   ├── evaluate_yolov11.py    ← Test the model
│   └── inference_yolov11.py   ← Use the model
├── datasets/
│   ├── raw/                   ← Your raw images (by class)
│   └── processed/             ← Auto-generated train/val/test
├── runs/classify/             ← Training outputs
└── models/                    ← Exported models
```

## 🚀 Windows Batch Menu

Run this for an interactive menu:

```bash
quickstart.bat
```

Menu options:
1. Install dependencies
2. Prepare dataset
3. Train YOLOv11 model
4. Evaluate model
5. Run inference (single image)
6. Run batch inference
7. View configuration
8. View documentation

## 🎓 Next Steps

1. **Prepare your data:**
   - Collect stain images
   - Organize into `datasets/raw/` folders
   - Run `prepare_dataset.py`

2. **Start training:**
   - Run `python scripts/train_yolov11.py`
   - Monitor with TensorBoard

3. **Evaluate results:**
   - Run `python scripts/evaluate_yolov11.py`
   - Check accuracy and confusion matrix

4. **Deploy to app:**
   - Export model to TFLite
   - Integrate with Flutter
   - Test on actual device

## 📞 Help & Resources

- **YOLOv11 Docs**: https://docs.ultralytics.com/models/yolov11/
- **Ultralytics GitHub**: https://github.com/ultralytics/ultralytics
- **PyTorch Docs**: https://pytorch.org/docs/
- **Check README_YOLOV11.md** for advanced topics
