# 📊 Train YOLOv11 on Your Annotated Datasets - Quick Start

## ⚡ Super Quick (3 Steps)

### Step 1: Place Your Datasets
```
You have 3 stain types:

ml_training/datasets/raw/
├── oil/    ← All cooking oil stain images
├── mud/    ← All mud stain images
└── ink/    ← All ink stain images
```

### Step 2: Install Dependencies (One Time)
```bash
pip install -r requirements.txt
```

### Step 3: Run Training
**On Windows:**
```bash
train_dataset.bat
```

**On Mac/Linux:**
```bash
python scripts/organize_and_train.py
```

Then select option **1** from the menu.

---

## 🚀 What Happens Automatically

1. **Detects** your dataset format (already organized, flat, pre-split, etc.)
2. **Organizes** images into `train/val/test` folders (70/15/15 split)
3. **Verifies** everything looks correct
4. **Trains** YOLOv11 model (5-20 minutes depending on data size)
5. **Saves** the trained model to `runs/classify/stain_detection_yolov11/weights/best.pt`

---

## 📁 Dataset Formats Supported

### ✅ Format 1: Class Folders (Easiest)
```
datasets/raw/
├── coffee/
│   ├── img1.jpg
│   ├── img2.jpg
│   └── ...
├── wine/
│   ├── img1.jpg
│   └── ...
└── ... (other classes)
```

### ✅ Format 2: Already Split
```
datasets/raw/
├── coffee/
│   ├── train/
│   │   ├── img1.jpg
│   │   └── ...
│   ├── val/
│   └── test/
├── wine/
│   ├── train/
│   ├── val/
│   └── test/
└── ...
```

### ✅ Format 3: Flat Folder (Images not organized)
```
datasets/raw/
├── coffee_stain_001.jpg
├── coffee_stain_002.jpg
├── wine_stain_001.jpg
└── ... (must rename/organize to class folders first)
```

---

## 📊 Training Time Estimates

| Dataset Size | Training Time | Accuracy | GPU |
|--------------|---------------|----------|-----|
| 400 images (50/class) | 5-8 min | 80-85% | NVIDIA |
| 800 images (100/class) | 8-12 min | 88-92% | NVIDIA |
| 1,600 images (200/class) | 12-18 min | 93-96% | NVIDIA |
| 400 images | 15-30 min | 80-85% | CPU |

---

## 🎯 Commands Reference

### Automatic Training (Recommended)
```bash
# Windows
train_dataset.bat

# Mac/Linux
python scripts/organize_and_train.py
```

### Just Check Organization (No Training)
```bash
python scripts/organize_and_train.py --verify-only
```

### Train on Pre-Organized Data
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
    --image path/to/image.jpg
```

### Batch Inference on Folder
```bash
python scripts/inference_yolov11.py \
    --model runs/classify/stain_detection_yolov11/weights/best.pt \
    --batch path/to/images/ \
    --output results.json
```

---

## ✅ Check Training Status

### Model Created?
```bash
# Windows
dir runs/classify/stain_detection_yolov11/weights/best.pt

# Mac/Linux
ls -lh runs/classify/stain_detection_yolov11/weights/best.pt
```

### View Training Plots
```bash
# Open this file to see training results
runs/classify/stain_detection_yolov11/results.png
```

### See All Metrics
```bash
# View CSV file with all metrics
runs/classify/stain_detection_yolov11/results.csv
```

---

## ⚙️ Customize Training

Edit `config.yaml` before training:

```yaml
training:
  model_size: "m"        # n(nano), s(small), m(medium), l(large), x(xlarge)
  epochs: 100            # How long to train
  batch_size: 32         # Reduce if out of memory
  learning_rate: 0.01    # Training speed
  patience: 20           # Early stopping patience
  device: 0              # 0=GPU, 'cpu'=CPU only
```

Then retrain:
```bash
python scripts/organize_and_train.py
```

---

## 🐛 Troubleshooting

### "Images not found"
- Check folder names are exactly: `coffee`, `wine`, `blood`, etc.
- Verify images are in `datasets/raw/coffee/`, not `datasets/raw/`

### "Out of Memory" Error
In `config.yaml`:
```yaml
batch_size: 16    # Reduce from 32
# OR
model_size: "s"   # Use smaller model
```

### Training is Very Slow
- Make sure you have GPU enabled: `device: 0`
- Check with: `python -c "import torch; print(torch.cuda.is_available())"`
- If False, either install CUDA or use CPU (slower)

### Low Accuracy After Training
- Make sure images are clear and well-labeled
- Ensure balanced dataset (same images per class)
- Train longer: increase `epochs` to 200
- Use larger model: `model_size: "l"`

---

## 📱 Deploy to Flutter App

After training:

```bash
# Export to TFLite (mobile-optimized)
python scripts/train_yolov11.py --export tflite

# Copy to Flutter assets
cp runs/classify/stain_detection_yolov11/weights/best.tflite \
   ../stain_scanner/assets/models/stain_detection_model.tflite

# Update your Flutter code to use the model
```

---

## 📈 Monitor Training Live

While training runs, open another terminal:

```bash
tensorboard --logdir runs/classify/
```

Then go to: http://localhost:6006

---

## 🎓 Next Steps After Training

1. ✅ **Evaluate Results**
   ```bash
   python scripts/evaluate_yolov11.py
   ```

2. ✅ **Test on Your Images**
   ```bash
   python scripts/inference_yolov11.py --model runs/classify/stain_detection_yolov11/weights/best.pt --image test.jpg
   ```

3. ✅ **Deploy to App**
   - Export to TFLite
   - Copy to Flutter assets
   - Update image_analysis_service.dart

---

## 📞 Help

**See detailed docs:**
- [TRAIN_ON_ANNOTATED_DATA.md](TRAIN_ON_ANNOTATED_DATA.md) - Full guide
- [README_YOLOV11.md](README_YOLOV11.md) - Technical documentation
- [config.yaml](config.yaml) - All settings explained

**Common Issues:**
1. Datasets not being found → Check folder structure
2. Out of memory → Reduce `batch_size`
3. Poor accuracy → Ensure quality annotations & more images
4. Slow training → Enable GPU in `config.yaml`

---

## 🚀 You're Ready!

1. **Place your datasets** in `datasets/raw/`
2. **Run:** `train_dataset.bat` (Windows) or `python scripts/organize_and_train.py` (Mac/Linux)
3. **Wait** 5-20 minutes
4. **Done!** Your model is ready in `runs/classify/stain_detection_yolov11/weights/best.pt`

**Good luck! 🎉**
