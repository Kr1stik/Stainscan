"""
Model training script for stain detection.
Trains a deep learning model using transfer learning with EfficientNet/ResNet50/MobileNet.
"""

import os
import yaml
import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.applications import EfficientNetB0, ResNet50, MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from pathlib import Path
import matplotlib.pyplot as plt
from tqdm import tqdm
import argparse
from datetime import datetime

class StainDetectionModel:
    def __init__(self, config_path='config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.classes = self.config['classes']
        self.num_classes = len(self.classes)
        self.image_size = tuple(self.config['preprocessing']['image_size'])
        self.batch_size = self.config['training']['batch_size']
        self.epochs = self.config['training']['epochs']
        self.learning_rate = self.config['training']['learning_rate']
        self.model_type = self.config['training']['model_type']
        
        self.model = None
        self.history = None
        
        # Create output directories
        Path(self.config['output']['logs_dir']).mkdir(parents=True, exist_ok=True)
        Path(self.config['output']['metrics_dir']).mkdir(parents=True, exist_ok=True)
        Path(self.config['output']['plots_dir']).mkdir(parents=True, exist_ok=True)
        Path(self.config['model']['save_path']).mkdir(parents=True, exist_ok=True)
    
    def build_model(self):
        """Build model with transfer learning."""
        print("\n" + "="*60)
        print(f"Building {self.model_type} model...")
        print("="*60)
        
        # Load pre-trained base model
        input_shape = (*self.image_size, 3)
        
        if self.model_type == 'efficientnet':
            base_model = EfficientNetB0(input_shape=input_shape, include_top=False, weights='imagenet')
        elif self.model_type == 'resnet50':
            base_model = ResNet50(input_shape=input_shape, include_top=False, weights='imagenet')
        elif self.model_type == 'mobilenet':
            base_model = MobileNetV2(input_shape=input_shape, include_top=False, weights='imagenet')
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        # Freeze base model layers
        base_model.trainable = False
        
        # Build custom top layers
        model = models.Sequential([
            layers.Input(shape=input_shape),
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.1),
            layers.Rescaling(1./255),
            
            base_model,
            
            layers.GlobalAveragePooling2D(),
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            layers.Dense(128, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(self.num_classes, activation='softmax')
        ])
        
        # Compile model
        optimizer = keras.optimizers.Adam(learning_rate=self.learning_rate)
        model.compile(
            optimizer=optimizer,
            loss=self.config['training']['loss_function'],
            metrics=['accuracy', keras.metrics.TopKCategoricalAccuracy(k=3, name='top_3_accuracy')]
        )
        
        self.model = model
        print("\nModel summary:")
        model.summary()
        return model
    
    def create_data_generators(self, data_path):
        """Create image data generators with augmentation."""
        print("\nCreating data generators...")
        
        aug_config = self.config['augmentation']
        
        if aug_config['enabled']:
            train_datagen = ImageDataGenerator(
                rescale=1./255,
                rotation_range=aug_config['rotation_range'],
                width_shift_range=aug_config['width_shift_range'],
                height_shift_range=aug_config['height_shift_range'],
                horizontal_flip=aug_config['horizontal_flip'],
                zoom_range=aug_config['zoom_range'],
                brightness_range=[1-aug_config['brightness_range'], 1+aug_config['brightness_range']],
                fill_mode='nearest'
            )
        else:
            train_datagen = ImageDataGenerator(rescale=1./255)
        
        val_test_datagen = ImageDataGenerator(rescale=1./255)
        
        train_dir = Path(data_path) / 'train'
        val_dir = Path(data_path) / 'val'
        
        train_generator = train_datagen.flow_from_directory(
            str(train_dir),
            target_size=self.image_size,
            batch_size=self.batch_size,
            class_mode='categorical'
        )
        
        val_generator = val_test_datagen.flow_from_directory(
            str(val_dir),
            target_size=self.image_size,
            batch_size=self.batch_size,
            class_mode='categorical'
        )
        
        return train_generator, val_generator
    
    def train(self, train_data_path):
        """Train the model."""
        print("\n" + "="*60)
        print("STARTING TRAINING")
        print("="*60)
        
        train_gen, val_gen = self.create_data_generators(train_data_path)
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=self.config['training']['early_stopping_patience'],
                restore_best_weights=True,
                verbose=1
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=3,
                min_lr=1e-7,
                verbose=1
            ),
            keras.callbacks.TensorBoard(
                log_dir=self.config['output']['logs_dir'],
                histogram_freq=1
            )
        ]
        
        # Train model
        steps_per_epoch = train_gen.samples // self.batch_size
        validation_steps = val_gen.samples // self.batch_size
        
        self.history = self.model.fit(
            train_gen,
            epochs=self.epochs,
            steps_per_epoch=steps_per_epoch,
            validation_data=val_gen,
            validation_steps=validation_steps,
            validation_freq=self.config['training']['validation_frequency'],
            callbacks=callbacks,
            verbose=1
        )
        
        print("\n" + "="*60)
        print("Training complete!")
        print("="*60)
    
    def save_model(self):
        """Save trained model."""
        if self.model is None:
            print("Error: Model not trained yet.")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_name = f"{self.config['model']['name']}_{timestamp}"
        
        if self.config['model']['format'] == 'h5':
            save_path = Path(self.config['model']['save_path']) / f"{model_name}.h5"
            self.model.save(str(save_path))
        elif self.config['model']['format'] == 'savedmodel':
            save_path = Path(self.config['model']['save_path']) / model_name
            self.model.save(str(save_path))
        elif self.config['model']['format'] == 'tflite':
            converter = tf.lite.TFLiteConverter.from_keras_model(self.model)
            tflite_model = converter.convert()
            save_path = Path(self.config['model']['save_path']) / f"{model_name}.tflite"
            with open(save_path, 'wb') as f:
                f.write(tflite_model)
        
        print(f"Model saved to: {save_path}")
        return str(save_path)
    
    def plot_training_history(self):
        """Plot and save training history."""
        if self.history is None:
            print("No training history available.")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        
        # Accuracy plot
        axes[0].plot(self.history.history['accuracy'], label='Train Accuracy')
        axes[0].plot(self.history.history['val_accuracy'], label='Val Accuracy')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Accuracy')
        axes[0].set_title('Model Accuracy')
        axes[0].legend()
        axes[0].grid(True)
        
        # Loss plot
        axes[1].plot(self.history.history['loss'], label='Train Loss')
        axes[1].plot(self.history.history['val_loss'], label='Val Loss')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Loss')
        axes[1].set_title('Model Loss')
        axes[1].legend()
        axes[1].grid(True)
        
        plot_path = Path(self.config['output']['plots_dir']) / 'training_history.png'
        plt.savefig(str(plot_path), dpi=300, bbox_inches='tight')
        print(f"Training history plot saved to: {plot_path}")
        plt.close()

def main():
    parser = argparse.ArgumentParser(description='Train stain detection model')
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to config file')
    parser.add_argument('--data-path', type=str, default='datasets/processed', help='Path to processed data')
    parser.add_argument('--skip-train', action='store_true', help='Skip training (only build model)')
    args = parser.parse_args()
    
    # Check GPU availability
    print("GPU Available:", tf.config.list_physical_devices('GPU'))
    
    trainer = StainDetectionModel(args.config)
    trainer.build_model()
    
    if not args.skip_train:
        trainer.train(args.data_path)
        trainer.plot_training_history()
        trainer.save_model()

if __name__ == '__main__':
    main()
