"""
Quick start script for the ML training pipeline.
Provides an interactive menu to set up and run the pipeline.
"""

import os
import sys
import subprocess
from pathlib import Path

class MLPipelineQuickStart:
    def __init__(self):
        self.script_dir = Path(__file__).parent.parent
        self.scripts_dir = self.script_dir / 'scripts'
        
    def run_command(self, command):
        """Run a shell command."""
        print(f"\n{'='*60}")
        print(f"Running: {' '.join(command)}")
        print('='*60)
        subprocess.run(command, cwd=str(self.script_dir))
    
    def check_setup(self):
        """Check if setup is complete."""
        print("\n" + "="*60)
        print("SETUP CHECK")
        print("="*60)
        
        checks = {
            'config.yaml': self.script_dir / 'config.yaml',
            'requirements.txt': self.script_dir / 'requirements.txt',
            'prepare_dataset.py': self.scripts_dir / 'prepare_dataset.py',
            'train_model.py': self.scripts_dir / 'train_model.py',
            'evaluate_model.py': self.scripts_dir / 'evaluate_model.py',
            'inference.py': self.scripts_dir / 'inference.py',
        }
        
        all_good = True
        for name, path in checks.items():
            if path.exists():
                print(f"✓ {name}")
            else:
                print(f"✗ {name} (missing)")
                all_good = False
        
        return all_good
    
    def show_menu(self):
        """Display main menu."""
        print("\n" + "="*60)
        print("STAIN DETECTION ML PIPELINE")
        print("="*60)
        print("\n1. Install dependencies")
        print("2. Prepare dataset")
        print("3. Train model")
        print("4. Evaluate model")
        print("5. Run inference on image")
        print("6. View configuration")
        print("7. Check setup status")
        print("8. View README")
        print("9. Exit")
        print("\nEnter choice (1-9): ", end="")
    
    def install_dependencies(self):
        """Install Python dependencies."""
        print("\nInstalling dependencies...")
        self.run_command([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("\n✓ Dependencies installed successfully!")
    
    def prepare_dataset(self):
        """Run dataset preparation."""
        print("\nDataset Preparation")
        print("-" * 40)
        print("Choose format:")
        print("1. Directory structure (train/val/test folders)")
        print("2. Numpy arrays")
        print("Enter choice (1-2): ", end="")
        
        choice = input().strip()
        format_type = 'directory' if choice == '1' else 'numpy'
        
        cmd = [sys.executable, str(self.scripts_dir / 'prepare_dataset.py'), 
               '--format', format_type]
        self.run_command(cmd)
    
    def train_model(self):
        """Run model training."""
        print("\nModel Training")
        print("-" * 40)
        print("Configuration options:")
        print("- Model type: efficientnet (recommended), resnet50, mobilenet")
        print("- Edit config.yaml to customize")
        print("\nStarting training...")
        
        cmd = [sys.executable, str(self.scripts_dir / 'train_model.py')]
        self.run_command(cmd)
    
    def evaluate_model(self):
        """Run model evaluation."""
        print("\nModel Evaluation")
        print("-" * 40)
        
        model_dir = self.script_dir / 'models'
        model_files = list(model_dir.glob('*.h5')) if model_dir.exists() else []
        
        if model_files:
            print("Available models:")
            for i, model in enumerate(sorted(model_files), 1):
                print(f"{i}. {model.name}")
            print("Latest model will be used automatically.")
        
        cmd = [sys.executable, str(self.scripts_dir / 'evaluate_model.py')]
        self.run_command(cmd)
    
    def run_inference(self):
        """Run inference on a single image."""
        print("\nInference")
        print("-" * 40)
        
        image_path = input("Enter path to image: ").strip()
        
        if not Path(image_path).exists():
            print(f"✗ Image not found: {image_path}")
            return
        
        model_path = input("Enter path to model (leave empty for latest): ").strip()
        if not model_path:
            model_dir = self.script_dir / 'models'
            model_files = list(model_dir.glob('*.h5')) if model_dir.exists() else []
            if model_files:
                model_path = str(sorted(model_files)[-1])
            else:
                print("✗ No model found. Train a model first.")
                return
        
        cmd = [sys.executable, str(self.scripts_dir / 'inference.py'),
               '--model', model_path,
               '--image', image_path]
        self.run_command(cmd)
    
    def view_config(self):
        """View current configuration."""
        config_path = self.script_dir / 'config.yaml'
        if config_path.exists():
            print("\n" + "="*60)
            print("CONFIGURATION (config.yaml)")
            print("="*60)
            with open(config_path, 'r') as f:
                print(f.read())
        else:
            print("✗ config.yaml not found")
    
    def view_readme(self):
        """View README."""
        readme_path = self.script_dir / 'README.md'
        if readme_path.exists():
            with open(readme_path, 'r') as f:
                content = f.read()
                # Show first 100 lines
                lines = content.split('\n')
                for line in lines[:100]:
                    print(line)
                if len(lines) > 100:
                    print(f"\n... ({len(lines) - 100} more lines) ...")
        else:
            print("✗ README.md not found")
    
    def run(self):
        """Main loop."""
        print("\n" + "="*60)
        print("QUICK START SETUP")
        print("="*60)
        
        if not self.check_setup():
            print("\n⚠ Warning: Some files are missing!")
        
        while True:
            self.show_menu()
            choice = input().strip()
            
            if choice == '1':
                self.install_dependencies()
            elif choice == '2':
                self.prepare_dataset()
            elif choice == '3':
                self.train_model()
            elif choice == '4':
                self.evaluate_model()
            elif choice == '5':
                self.run_inference()
            elif choice == '6':
                self.view_config()
            elif choice == '7':
                self.check_setup()
            elif choice == '8':
                self.view_readme()
            elif choice == '9':
                print("\nGoodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == '__main__':
    quickstart = MLPipelineQuickStart()
    quickstart.run()
