# Dataset Structure Guide

## Setting Up Your Dataset

Before training, you need to organize your stain images into the correct directory structure.

### Step 1: Create Raw Dataset Directory

```
ml_training/datasets/raw/
├── coffee/
├── wine/
├── blood/
├── grass/
├── oil/
├── ink/
├── chocolate/
└── makeup/
```

### Step 2: Add Images to Each Class

Place your stain images into each class folder:

```
ml_training/datasets/raw/
├── coffee/
│   ├── coffee_stain_001.jpg
│   ├── coffee_stain_002.jpg
│   ├── coffee_stain_003.jpg
│   └── ... (more images)
├── wine/
│   ├── wine_stain_001.jpg
│   ├── wine_stain_002.jpg
│   └── ... (more images)
└── ... (other classes)
```

### Step 3: Image Requirements

**Minimum Requirements:**
- **Per class**: At least 50 images (100+ recommended)
- **Total minimum**: 400 images (50 per class × 8 classes)
- **Recommended**: 1000+ images for production quality

**Image Format:**
- Supported: `.jpg`, `.jpeg`, `.png`
- Size: Any size (will be resized to 224×224)
- Color: RGB (color images preferred over grayscale)

**Image Quality:**
- Clear visibility of the stain
- Well-lit images
- Minimal background clutter
- Various angles and distances
- Different lighting conditions

### Step 4: Organize by Source

It's helpful to organize images during collection:

```
ml_training/datasets/raw/coffee/
├── indoor/
│   ├── image1.jpg
│   └── image2.jpg
├── outdoor/
│   ├── image3.jpg
│   └── image4.jpg
└── fabric_samples/
    ├── image5.jpg
    └── image6.jpg
```

**The prepare_dataset.py script will flatten this structure automatically.**

## Dataset Statistics

### For 8 Stain Classes (Recommended Setup)

| Class | Min Images | Recommended | Production |
|-------|-----------|-------------|-----------|
| Coffee | 50 | 100-200 | 500+ |
| Wine | 50 | 100-200 | 500+ |
| Blood | 50 | 100-200 | 500+ |
| Grass | 50 | 100-200 | 500+ |
| Oil | 50 | 100-200 | 500+ |
| Ink | 50 | 100-200 | 500+ |
| Chocolate | 50 | 100-200 | 500+ |
| Makeup | 50 | 100-200 | 500+ |
| **TOTAL** | **400** | **800-1600** | **4000+** |

### Train/Val/Test Split

Default split (configurable):
- **Training**: 70% (used to train the model)
- **Validation**: 15% (used to tune hyperparameters)
- **Testing**: 15% (final evaluation)

Example with 1000 total images:
- Train: 700 images
- Val: 150 images
- Test: 150 images

## Data Collection Tips

### 1. Real-World Stains
- Use actual stained fabric samples
- Capture different stages (fresh, dried)
- Vary fabric types if possible

### 2. Photography Tips
- Use consistent lighting
- Capture at multiple angles
- Include close-ups and wide shots
- Vary distances from camera
- Different backgrounds (white, colored, textured)

### 3. Include Variations
- Different materials (cotton, silk, wool)
- Different colors of fabric
- Different stain intensities
- Clean vs. worn fabrics

### 4. Avoid Issues
- ❌ Blurry images
- ❌ Over/underexposed images
- ❌ Images that are too dark
- ❌ Identical images (remove duplicates)
- ❌ Mislabeled stains

## Data Validation

Run the preparation script to validate your dataset:

```bash
python scripts/prepare_dataset.py --format directory
```

This script will:
- ✓ Check for missing class folders
- ✓ Validate all images are readable
- ✓ Report invalid images
- ✓ Count images per class
- ✓ Create train/val/test splits
- ✓ Resize images to standard size

### Expected Output:
```
coffee          - Total:  150  Valid:  150  Invalid:    0
wine            - Total:  150  Valid:  150  Invalid:    0
blood           - Total:  150  Valid:  150  Invalid:    0
...
TOTAL           - 1200 images (1200 valid, 0 invalid)
```

## Improving Model Performance

### If accuracy is low (<80%):

1. **Increase dataset size**
   - Collect more images per class
   - Ensure balanced distribution

2. **Improve image quality**
   - Remove blurry images
   - Remove mislabeled images
   - Check for corrupted files

3. **Class balance**
   - Ensure roughly equal images per class
   - If imbalanced, use class weighting in config

4. **Data diversity**
   - Include different lighting conditions
   - Different camera angles
   - Different fabric types
   - Different stain ages

### If model overfits (high train accuracy, low test accuracy):

1. **More data**
   - Collect more training images
   - Use data augmentation (enabled by default)

2. **Simplify model**
   - Use `mobilenet` instead of `efficientnet`
   - Reduce epochs

## Sample Directory Layout (Ready to Train)

```
ml_training/
├── datasets/
│   ├── raw/
│   │   ├── coffee/
│   │   │   ├── stain_001.jpg
│   │   │   ├── stain_002.jpg
│   │   │   └── ... (150 total)
│   │   ├── wine/
│   │   │   ├── stain_001.jpg
│   │   │   ├── stain_002.jpg
│   │   │   └── ... (150 total)
│   │   ├── blood/
│   │   │   └── ... (150 images)
│   │   ├── grass/
│   │   │   └── ... (150 images)
│   │   ├── oil/
│   │   │   └── ... (150 images)
│   │   ├── ink/
│   │   │   └── ... (150 images)
│   │   ├── chocolate/
│   │   │   └── ... (150 images)
│   │   └── makeup/
│   │       └── ... (150 images)
│   │
│   └── processed/
│       ├── train/
│       │   ├── coffee/ (105 images)
│       │   ├── wine/ (105 images)
│       │   └── ...
│       ├── val/
│       │   ├── coffee/ (22 images)
│       │   ├── wine/ (22 images)
│       │   └── ...
│       └── test/
│           ├── coffee/ (23 images)
│           ├── wine/ (23 images)
│           └── ...
```

## Next Steps

Once your dataset is ready:

1. Run: `python scripts/prepare_dataset.py --format directory`
2. Run: `python scripts/train_model.py`
3. Run: `python scripts/evaluate_model.py`
4. Use: `python scripts/inference.py`

For more information, see [README.md](README.md)
