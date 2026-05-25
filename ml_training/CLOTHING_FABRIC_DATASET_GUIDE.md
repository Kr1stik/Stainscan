# Clothing and Fabric Dataset Guide

## Why this is needed

Your current model is trained only to detect stain types (`oil`, `mud`, `ink`). That means the server can detect stains, but it cannot reliably recognize whether the image is actually clothing or fabric. To reduce false “not clothing or fabric” cases, the model needs training data that includes:

- clean clothing/fabric images
- clothing/fabric images with stains
- a clothing/fabric label or object class
- optionally negative examples (non-clothing images)

## Recommended strategy

### Option 1: Single YOLO model with both stain and fabric classes

Train a detection model with these classes:

- `clothing`
- `fabric`
- `oil`
- `mud`
- `ink`

This lets the model:

- detect clothing/fabric regions
- detect stains on those regions
- avoid labeling non-clothing objects as clothing/fabric

### Option 2: Two-step pipeline

1. First classify or detect if the image contains clothing/fabric.
2. Then run stain detection only on the clothing/fabric region.

This is more robust if you want a separate “is clothing/fabric?” check.

## Free dataset sources

### Public datasets

- Open Images Dataset
  - Use categories like `Clothing`, `Apparel`, `Textile`, `Fashion accessory`
  - https://storage.googleapis.com/openimages/web/index.html

- DeepFashion / DeepFashion2
  - Contains clothing images, annotations, and bounding boxes
  - Search on Kaggle or academic dataset pages

- Fashion Product Images
  - Kaggle has free fashion image datasets
  - https://www.kaggle.com/datasets

- Open Images V7/8 via TensorFlow Datasets
  - Many clothing labels are already annotated

### Free photography sites (manual download)

- Unsplash: https://unsplash.com/
- Pexels: https://www.pexels.com/
- Pixabay: https://pixabay.com/

These are useful for collecting diverse clothing/fabric photos, but you will need to annotate them manually.

## How to organize the dataset

For YOLO detection, use this structure:

```
ml_training/datasets/raw/
  clothing/
    image1.jpg
    image2.jpg
  fabric/
    image1.jpg
    image2.jpg
  oil/
    stain1.jpg
    stain2.jpg
  mud/
    stain1.jpg
  ink/
    stain1.jpg
```

If the model is trained as a detection model, each image also needs a matching annotation file (`.txt`) using YOLO format.

## How to label new data

For every image containing a clothing/fabric region and/or a stain:

- Create a `.txt` file with the same base name as the image
- Use YOLO format: `class x_center y_center width height`
- Normalize coordinates to [0, 1]
- Include one line per object

Example `image1.txt`:

```
3 0.45 0.50 0.80 0.90
2 0.55 0.60 0.20 0.15
```

Where class indexes match the dataset names list.

## Example training YAML for clothing/fabric

Use the template file `ml_training/datasets/data_fabric_clothing.yaml`.

If your dataset paths are:

- `ml_training/datasets/processed/combined_train_clothing`
- `ml_training/datasets/processed/combined_val_clothing`

then `data_fabric_clothing.yaml` should contain:

```yaml
train: processed/combined_train_clothing
val: processed/combined_val_clothing
nc: 5
names: ['oil', 'mud', 'ink', 'clothing', 'fabric']
```

## Training pipeline

1. Collect clothing/fabric images.
2. Annotate clothing/fabric and stain boxes.
3. Place images and `.txt` labels into `processed/combined_train_clothing` and `processed/combined_val_clothing`.
4. Run the training script.

## Important note

I cannot automatically download a fully labeled clothing/fabric dataset for you in this repository, because a labeled training set must be built from real images and annotations. What I can do is help you integrate those new classes into the existing YOLOv11 training pipeline.

## Next step

After you have clothing/fabric images and labels, use this command:

```bash
python scripts/train_yolov11.py --data-path datasets/data_fabric_clothing.yaml
```

This will train a YOLOv11 detection model with the expanded class list.
