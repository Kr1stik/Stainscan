# ✅ Quick Setup Checklist - 3 Stain Types

## 📋 Your Dataset Configuration

You're training on **3 stain types only**:
- ✅ Oil Stain (cooking oil)
- ✅ Mud Stain
- ✅ Ink Stain

Everything is already configured in `config.yaml`

---

## 🚀 5-Minute Setup

### ✓ Step 1: Create Folder Structure
Create these 3 folders:
```
C:\Users\LENOVO\OneDrive\Desktop\MOBILE_APP\ml_training\datasets\raw\
├── oil\     
├── mud\     
└── ink\     
```

### ✓ Step 2: Copy Your Images
- Put all **oil stain images** into `raw/oil/`
- Put all **mud stain images** into `raw/mud/`
- Put all **ink stain images** into `raw/ink/`

**Expected:** At least 50 images per type (150+ total)

### ✓ Step 3: Install Python Dependencies
Open PowerShell in the `ml_training` folder:
```powershell
pip install -r requirements.txt
```

### ✓ Step 4: Start Training
Double-click or run:
```bash
train_dataset.bat
```

Then select **option 1** (Organize & Train)

### ✓ Step 5: Wait for Training to Complete
- ⏱️ Estimated time: **5-20 minutes** (depending on dataset size)
- Look for: `✓ TRAINING COMPLETE!`
- Your model: `runs/classify/stain_detection_yolov11/weights/best.pt`

---

## 📊 Expected Accuracy vs Time

| Images Per Type | Total Images | Training Time | Accuracy |
|-----------------|--------------|---------------|----------|
| 50 | 150 | 5-7 min | 82-87% |
| 75 | 225 | 7-10 min | 86-90% |
| 100 | 300 | 8-12 min | 89-93% |
| 150 | 450 | 12-15 min | 92-95% |
| 200 | 600 | 15-18 min | 94-97% |

---

## 🎯 What Gets Created After Training

```
runs/classify/stain_detection_yolov11/
│
├── weights/
│   ├── best.pt        ← YOUR TRAINED MODEL (use this!)
│   └── last.pt        (last checkpoint)
│
├── results.png        ← Training plot
├── confusion_matrix.png ← Accuracy by class
└── results.csv        ← All metrics
```

---

## ✨ Test Your Trained Model

After training completes:

### Test on Single Image
```powershell
python scripts/inference_yolov11.py `
    --model runs/classify/stain_detection_yolov11/weights/best.pt `
    --image C:\path\to\test\image.jpg
```

Output example:
```
Analyzing: C:\path\to\test\image.jpg
Class             Confidence         Percentage        
--------------------------------------------------
oil               0.9234             92.34%            
mud               0.0523             5.23%             
ink               0.0243             2.43%
```

### Evaluate on All Test Images
```powershell
python scripts/evaluate_yolov11.py
```

This shows:
- Confusion matrix
- Precision/Recall per stain type
- Overall accuracy

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Images not found" | Check folder names: `oil`, `mud`, `ink` (exact match) |
| Out of memory | Edit config.yaml: `batch_size: 16` (from 32) |
| Training is slow | Make sure GPU is enabled: `device: 0` |
| Low accuracy | Ensure images are clear and balanced (equal per type) |
| Model not found | Training failed - check error messages above |

---

## 🎓 Folder Structure Checklist

Before starting training, verify this structure:

```
ml_training/
├── config.yaml                      ✓ (already updated for 3 classes)
├── requirements.txt                 ✓
├── train_dataset.bat                ✓
├── scripts/
│   ├── organize_and_train.py        ✓
│   ├── train_yolov11.py             ✓
│   ├── evaluate_yolov11.py          ✓
│   └── inference_yolov11.py         ✓
├── datasets/
│   ├── raw/
│   │   ├── oil/         ← YOUR OIL IMAGES (50-200)
│   │   ├── mud/         ← YOUR MUD IMAGES (50-200)
│   │   └── ink/         ← YOUR INK IMAGES (50-200)
│   └── processed/       ← Created automatically during training
├── runs/                ← Created after training
│   └── classify/
│       └── stain_detection_yolov11/
│           └── weights/
│               ├── best.pt          ← YOUR TRAINED MODEL
│               └── last.pt
```

---

## 📱 Deploy to Flutter App (After Training)

Once training is complete:

### 1. Export to Mobile Format
```powershell
python scripts/train_yolov11.py --export tflite
```

### 2. Copy to Flutter Assets
```powershell
Copy-Item "runs/classify/stain_detection_yolov11/weights/best.tflite" `
          "..\stain_scanner\assets\models\stain_detection_model.tflite"
```

### 3. Update Flutter Code
Edit `lib/services/image_analysis_service.dart` to use the new model

---

## 💡 Tips for Better Results

1. **More images = Better accuracy**
   - With 50 images per type: 85-90% accuracy
   - With 200 images per type: 95%+ accuracy

2. **Diverse images matter**
   - Different lighting conditions
   - Different angles
   - Different fabric types
   - Different stain intensities

3. **Clear annotations**
   - Make sure stains are clearly labeled
   - Remove blurry images
   - Remove mislabeled images

4. **Balanced dataset**
   - Try to have roughly equal images per stain type
   - Don't have 200 oil images but only 50 mud images

---

## 📞 Detailed Guides

For more information:
- **[TRAIN_3_STAIN_TYPES.md](TRAIN_3_STAIN_TYPES.md)** - Full guide for 3 classes
- **[START_HERE.md](START_HERE.md)** - General quick start
- **[README_YOLOV11.md](README_YOLOV11.md)** - Technical documentation
- **[config.yaml](config.yaml)** - All configuration settings

---

## 🚀 Ready? Let's Go!

**Summary of what you need to do:**

1. ✅ Create folders: `datasets/raw/oil/`, `datasets/raw/mud/`, `datasets/raw/ink/`
2. ✅ Copy your images into each folder
3. ✅ Run: `pip install -r requirements.txt`
4. ✅ Run: `train_dataset.bat` (or `python scripts/organize_and_train.py`)
5. ✅ Select option 1 and wait for training

**That's it!** Your trained model will be ready in 5-20 minutes. 🎉

---

## ✅ Verification

After training, check:

```powershell
# Does the model exist?
ls runs/classify/stain_detection_yolov11/weights/best.pt

# Size should be ~30-40 MB for 3 classes
ls -n runs/classify/stain_detection_yolov11/weights/best.pt
```

If you see the file, you're done! Training was successful. 🎉
