#!/usr/bin/env python3
"""
Setup script for the pest detection system
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8+")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    
    # Check if pip is available
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ pip is not available. Please install pip first.")
        return False
    
    # Install requirements
    requirements_file = Path(__file__).parent / "requirements.txt"
    if requirements_file.exists():
        success = run_command(
            f"{sys.executable} -m pip install -r {requirements_file}",
            "Installing Python dependencies"
        )
        return success
    else:
        print("❌ requirements.txt not found")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    base_dir = Path(__file__).parent
    directories = [
        base_dir / "media" / "detections",
        base_dir / "models",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def setup_django():
    """Setup Django project"""
    print("\n🐍 Setting up Django...")
    
    base_dir = Path(__file__).parent
    
    # Check if manage.py exists
    manage_py = base_dir / "manage.py"
    if not manage_py.exists():
        print("❌ manage.py not found. Are you in the correct directory?")
        return False
    
    # Run Django migrations
    success = run_command(
        f"cd {base_dir} && {sys.executable} manage.py migrate",
        "Running Django migrations"
    )
    
    return success

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🧪 Testing imports...")
    
    required_modules = [
        'django',
        'cv2',
        'numpy',
        'PIL',
        'ultralytics'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Please install missing dependencies manually.")
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 Pest Detection System Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create directories
    if not create_directories():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Test imports
    if not test_imports():
        return False
    
    # Setup Django
    if not setup_django():
        return False
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the server: python manage.py runserver")
    print("2. Open your browser to: http://localhost:8000/detection/")
    print("3. Login with your credentials")
    print("4. Test camera capture or image upload")
    print("\n📚 For more information, see DETECTION_README.md")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 