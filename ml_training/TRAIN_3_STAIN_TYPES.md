# 🎯 Training YOLOv11 for 3 Stain Types

Your dataset includes only **3 stain types**:
1. **Oil Stain** (cooking oil)
2. **Mud Stain**
3. **Ink Stain**

## ⚡ Quick Start

### Step 1: Organize Your Datasets

Create this folder structure:

```
ml_training/datasets/raw/
├── oil/           ← All cooking oil stain images
├── mud/           ← All mud stain images
└── ink/           ← All ink stain images
```

Each folder should contain your annotated stain images.

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Train the Model

**Windows:**
```bash
train_dataset.bat
```

**Mac/Linux:**
```bash
python scripts/organize_and_train.py
```

Select **option 1** to automatically organize and train.

---

## 📊 Expected Results

### With 50-100 images per stain type (150-300 total):
- ⏱️ Training time: **5-10 minutes**
- 📈 Accuracy: **85-90%**
- 📦 Model size: **~30-40 MB**

### With 100-200 images per stain type (300-600 total):
- ⏱️ Training time: **10-15 minutes**
- 📈 Accuracy: **92-96%**
- 📦 Model size: **~30-40 MB**

### With 200+ images per stain type (600+ total):
- ⏱️ Training time: **15-20 minutes**
- 📈 Accuracy: **96%+**
- 📦 Model size: **~30-40 MB**

---

## 📁 Dataset Structure

After uploading, your folder should look like:

```
ml_training/
├── datasets/
│   └── raw/
│       ├── oil/
│       │   ├── oil_stain_001.jpg
│       │   ├── oil_stain_002.jpg
│       │   ├── oil_stain_003.jpg
│       │   └── ... (50-200 images)
│       ├── mud/
│       │   ├── mud_stain_001.jpg
│       │   ├── mud_stain_002.jpg
│       │   └── ... (50-200 images)
│       └── ink/
│           ├── ink_stain_001.jpg
│           ├── ink_stain_002.jpg
│           └── ... (50-200 images)
```

---

## 🚀 Training Commands

### Auto-Train (Recommended)
```bash
# Windows
train_dataset.bat

# Mac/Linux
python scripts/organize_and_train.py
```

### Just Verify Organization
```bash
python scripts/organize_and_train.py --verify-only
```

### Train on Already Organized Data
```bash
python scripts/train_yolov11.py --data-path datasets/processed
```

### Evaluate Results
```bash
python scripts/evaluate_yolov11.py
```

### Test on Single Image
```bash
python scripts/inference_yolov11.py \
    --model runs/classify/stain_detection_yolov11/weights/best.pt \
    --image path/to/test_image.jpg
```

### Batch Test on Multiple Images
```bash
python scripts/inference_yolov11.py \
    --model runs/classify/stain_detection_yolov11/weights/best.pt \
    --batch path/to/image/folder/ \
    --output results.json
```

---

## ⚙️ Configuration

Your configuration is already set for 3 classes:

```yaml
classes:
  - oil
  - mud
  - ink

training:
  model_size: "m"        # m = balanced (recommended for 3 classes)
  epochs: 100            # Number of training iterations
  batch_size: 32         # Reduce to 16 if out of memory
  learning_rate: 0.01    # Training speed
  patience: 20           # Early stopping patience
  device: 0              # 0=GPU, 'cpu'=CPU
```

### Adjust if Needed:

**For Faster Training:**
```yaml
model_size: "s"        # Smaller model
epochs: 50             # Fewer iterations
batch_size: 64         # Larger batches
```

**For Better Accuracy:**
```yaml
model_size: "l"        # Larger model
epochs: 150            # More iterations
batch_size: 16         # Smaller batches
```

---

## 📈 Training Output

After training completes, you'll have:

```
runs/classify/stain_detection_yolov11/
├── weights/
│   ├── best.pt          ✓ Use this for inference
│   └── last.pt          (Last checkpoint)
├── results.png          ✓ Training plots
├── confusion_matrix.png ✓ Prediction analysis
├── results.csv          (All metrics)
└── ...
```

---

## ✅ Verify Training Success

### Check Model Was Created:
```bash
# Windows PowerShell
ls runs/classify/stain_detection_yolov11/weights/best.pt

# Mac/Linux
ls -lh runs/classify/stain_detection_yolov11/weights/best.pt
```

### Test the Model:
```bash
python scripts/inference_yolov11.py \
    --model runs/classify/stain_detection_yolov11/weights/best.pt \
    --image path/to/oil_stain.jpg
```

Expected output:
```
Analyzing: path/to/oil_stain.jpg
Class             Confidence         Percentage        
--------------------------------------------------
oil               0.9456             94.56%            
mud               0.0421             4.21%             
ink               0.0123             1.23%
```

---

## 🐛 Troubleshooting

### "Images not found"
**Solution:** Check folder names are EXACTLY:
```
datasets/raw/oil/
datasets/raw/mud/
datasets/raw/ink/
```

(Not: `datasets/raw/oil_stains/` or other variations)

### "Out of Memory" Error
**Solution:** In `config.yaml`:
```yaml
batch_size: 16    # Reduce from 32
# OR
model_size: "s"   # Use smaller model
```

### Training is Very Slow
**Solution:** Make sure GPU is enabled:
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

If it says `False`, you're using CPU (slower). Install CUDA for GPU support.

### Low Accuracy After Training
**Solution:**
- Ensure images are clear and well-labeled
- Check dataset balance (equal images per stain type)
- Train longer: increase `epochs` to 200
- Use larger model: `model_size: "l"`

---

## 📱 Deploy to Flutter App

After training succeeds:

### 1. Export to TFLite Format
```bash
python scripts/train_yolov11.py --export tflite
```

### 2. Copy to Flutter Assets
```bash
# Windows PowerShell
Copy-Item "runs/classify/stain_detection_yolov11/weights/best.tflite" `
          "../stain_scanner/assets/models/stain_detection_model.tflite"

# Mac/Linux
cp runs/classify/stain_detection_yolov11/weights/best.tflite \
   ../stain_scanner/assets/models/stain_detection_model.tflite
```

### 3. Update Flutter Code
Update `lib/services/image_analysis_service.dart` to use the trained model instead of random predictions.

---

## 📊 Example Training Session

Here's what you'll see during training:

```
============================================================
STARTING YOLOV11 TRAINING
============================================================

Training Configuration:
  Model: YOLOv11-m
  Epochs: 100
  Batch Size: 32
  Image Size: 640x640
  Device: 0 (GPU)
  Data Path: datasets/processed

Loading base model: yolov11m-cls

Starting training...

Epoch 1/100: 100%|████████████| 15/15 [00:12<00:00, 0.80/s]
  Class    Images  Instances  Cls(P/R/mAP)
  all      96      96         0.78/0.65/0.72

Epoch 2/100: 100%|████████████| 15/15 [00:12<00:00, 0.80/s]
  all      96      96         0.82/0.72/0.78

Epoch 3/100: 100%|████████████| 15/15 [00:12<00:00, 0.80/s]
  all      96      96         0.85/0.78/0.82

... (continues for 100 epochs) ...

============================================================
✓ TRAINING COMPLETE!
============================================================

Model saved to:
  runs/classify/stain_detection_yolov11/weights/best.pt
```

---

## 🎯 Quick Commands Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Auto-organize and train (easiest!)
python scripts/organize_and_train.py

# Just check organization (no training)
python scripts/organize_and_train.py --verify-only

# Train on organized data
python scripts/train_yolov11.py --data-path datasets/processed

# Evaluate performance
python scripts/evaluate_yolov11.py

# Test on single image
python scripts/inference_yolov11.py \
    --model runs/classify/stain_detection_yolov11/weights/best.pt \
    --image test.jpg

# Test on batch of images
python scripts/inference_yolov11.py \
    --model runs/classify/stain_detection_yolov11/weights/best.pt \
    --batch test_images/ \
    --output results.json

# Export to mobile format
python scripts/train_yolov11.py --export tflite
```

---

## 📝 Stain Type Guidelines

When organizing your datasets, make sure:

### Oil Stain Images
- Cooking oil, grease, engine oil
- May have shine/reflective properties
- Often appear as dark or oily patches

### Mud Stain Images
- Dried or wet mud
- Earthy brown colors
- May have texture patterns

### Ink Stain Images
- Pen ink, markers, printer ink
- Dark colors (black, blue, etc.)
- Usually sharper edges than natural stains

**Tip:** The more diverse your images (different lighting, angles, fabric types), the better the model performs!

---

## ✨ You're Ready!

1. **Organize datasets** in `datasets/raw/oil/`, `datasets/raw/mud/`, `datasets/raw/ink/`
2. **Run:** `python scripts/organize_and_train.py` (or `train_dataset.bat` on Windows)
3. **Select option 1** to automatically train
4. **Wait** 5-20 minutes for training to complete
5. **Use** the model for inference!

Good luck! 🚀
