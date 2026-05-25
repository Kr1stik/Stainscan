# Training on Your Annotated Datasets

Since you already have exported and annotated datasets, here's how to train the YOLOv11 model.

## 📂 Dataset Preparation

### Step 1: Upload Your Datasets

Place your datasets in this folder structure:

```
ml_training/datasets/raw/
├── coffee/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── wine/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── blood/
│   ├── image1.jpg
│   └── ...
├── grass/
├── oil/
├── ink/
├── chocolate/
└── makeup/
```

**Or if already split:**

```
ml_training/datasets/raw/
├── coffee/
│   ├── train/
│   ├── val/
│   └── test/
├── wine/
│   ├── train/
│   ├── val/
│   └── test/
└── ... (other classes)
```

### Step 2: Automatically Organize & Train

```bash
# Install dependencies first
pip install -r requirements.txt

# Organize datasets and prepare for training
python scripts/organize_and_train.py

# The script will:
# 1. Detect your dataset format
# 2. Organize images into train/val/test splits
# 3. Verify the dataset
# 4. Ask for confirmation
# 5. Start training automatically
```

## 🚀 Quick Start Commands

### Option A: Full Automatic (Recommended)
```bash
python scripts/organize_and_train.py
```
This does everything automatically.

### Option B: Step by Step

**1. Organize dataset only:**
```bash
python scripts/organize_and_train.py --verify-only
```

**2. Then train:**
```bash
python scripts/train_yolov11.py --data-path datasets/processed
```

### Option C: If Already Organized
```bash
python scripts/train_yolov11.py --data-path datasets/processed --skip-organize
```

## 📊 What Happens During Training

```
Epoch 1/100: 100%|████████| 23/23 [00:15<00:00, 1.50/s]
  Class    Images  Instances  Cls(P/R/mAP)
  all      120     120        0.78/0.65/0.72

Epoch 2/100: 100%|████████| 23/23 [00:15<00:00, 1.50/s]
  all      120     120        0.82/0.72/0.78
...
```

### Output Metrics:
- **P** (Precision) - How many predictions are correct
- **R** (Recall) - How many actual stains were found
- **mAP** - Overall accuracy score

## 📈 Expected Results

Based on your dataset size:

| Images/Class | Accuracy | Training Time |
|--------------|----------|---------------|
| 50 | 80-85% | 5 min |
| 100 | 88-92% | 8 min |
| 200 | 93-96% | 12 min |
| 500+ | 96%+ | 20 min |

## 📁 Training Output

After training completes, find results here:

```
runs/classify/stain_detection_yolov11/
├── weights/
│   ├── best.pt          ← Use this for inference
│   └── last.pt          ← Last checkpoint
├── results.csv          ← All metrics
├── results.png          ← Training plots
├── confusion_matrix.png ← Prediction analysis
└── ...
```

## ✅ Verify Training Worked

```bash
# Check if model was created
ls runs/classify/stain_detection_yolov11/weights/best.pt

# Test on a single image
python scripts/inference_yolov11.py \
    --model runs/classify/stain_detection_yolov11/weights/best.pt \
    --image path/to/test/image.jpg
```

## 🔧 Customize Training

Edit `config.yaml` to change:

```yaml
training:
  model_size: "m"        # n, s, m, l, x
  epochs: 100            # More = better accuracy
  batch_size: 32         # Reduce if out of memory
  learning_rate: 0.01    # Training speed
  device: 0              # 0=GPU, 'cpu'=CPU
```

Then retrain:
```bash
python scripts/train_yolov11.py --data-path datasets/processed
```

## 🐛 Troubleshooting

### Memory Error (OOM)
```yaml
# Reduce in config.yaml:
batch_size: 16  # was 32
# OR
model_size: "s"  # was "m"
```

### Images Not Found
Check folder structure:
```bash
# On Windows PowerShell
Get-ChildItem ml_training/datasets/raw/ -Recurse -Include *.jpg, *.png | Measure-Object

# Should show your images
```

### Training Very Slow
- Use GPU: `device: 0` in config
- Use smaller model: `model_size: "n"`
- Reduce `batch_size`

### Low Accuracy
- Ensure images are clear and well-labeled
- Check dataset balance (equal images per class)
- Train longer: increase `epochs`
- Use larger model: `model_size: "l"`

## 📱 Deploy to Flutter

After training completes:

```bash
# Export to TFLite (mobile)
python scripts/train_yolov11.py --export tflite

# Copy to Flutter
cp runs/classify/stain_detection_yolov11/weights/best.tflite \
   ../stain_scanner/assets/models/

# Update image_analysis_service.dart to use the model
```

## 📊 Monitor Training Live

While training, open another terminal:

```bash
tensorboard --logdir runs/classify/
```

Then open http://localhost:6006 in your browser

## ⚡ Performance Tips

### For Faster Training:
- Use smaller model: `model_size: "n"`
- Reduce epochs: `epochs: 50`
- Increase batch_size (if GPU memory allows)

### For Better Accuracy:
- More data (collect more images)
- Increase epochs: `epochs: 200`
- Use larger model: `model_size: "l"`
- Ensure quality annotations

## 📞 Help

### If Dataset Format is Different

If your datasets have a different structure (e.g., YOLO format with `.txt` files), you can:

1. **Run the automatic organizer:**
   ```bash
   python scripts/organize_and_train.py
   ```

2. **Or manually reorganize** into class folders before running

### Common Formats Handled:

✅ **Class folders:**
```
raw/
├── coffee/
├── wine/
└── ...
```

✅ **Pre-split folders:**
```
raw/
├── coffee/
│   ├── train/
│   ├── val/
│   └── test/
└── ...
```

✅ **Flat with annotations** (requires manual organization or script modification)

## Next Steps

1. **Upload your annotated datasets** to `datasets/raw/`
2. **Run:** `python scripts/organize_and_train.py`
3. **Wait for training to complete** (5-20 minutes)
4. **Evaluate:** `python scripts/evaluate_yolov11.py`
5. **Deploy to app!**

## Quick Reference Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Organize and train (all in one)
python scripts/organize_and_train.py

# Just verify organization
python scripts/organize_and_train.py --verify-only

# Train on existing organized data
python scripts/train_yolov11.py --data-path datasets/processed

# Evaluate results
python scripts/evaluate_yolov11.py

# Test on images
python scripts/inference_yolov11.py --model runs/classify/stain_detection_yolov11/weights/best.pt --image image.jpg

# Export to mobile format
python scripts/train_yolov11.py --export tflite
```

Good luck! 🚀
