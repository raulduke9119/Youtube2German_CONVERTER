#!/usr/bin/env python3
import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if all required packages are installed."""
    print("\nChecking dependencies...")
    required_packages = [
        'assemblyai',
        'pytube',
        'gTTS',
        'moviepy',
        'pydub',
        'python-dotenv'
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"❌ {package} is not installed")
            all_installed = False
    return all_installed

def check_ffmpeg():
    """Check if ffmpeg is installed."""
    print("\nChecking ffmpeg installation...")
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True)
        print("✓ ffmpeg")
        return True
    except FileNotFoundError:
        print("❌ ffmpeg is not installed")
        return False

def check_directories():
    """Check if required directories exist."""
    print("\nChecking directory structure...")
    required_dirs = [
        'data/input',
        'data/output',
        'data/temp',
        'data/logs',
        'data/cache'
    ]
    
    project_root = Path(__file__).parent
    all_exist = True
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if not full_path.exists():
            try:
                full_path.mkdir(parents=True)
                print(f"✓ Created {dir_path}")
            except Exception as e:
                print(f"❌ Could not create {dir_path}: {str(e)}")
                all_exist = False
        else:
            print(f"✓ {dir_path}")
    return all_exist

def check_env_file():
    """Check if .env file exists and contains required variables."""
    print("\nChecking .env file...")
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print("❌ .env file not found")
        return False
    
    with open(env_path) as f:
        contents = f.read()
        if 'ASSEMBLYAI_API_KEY' not in contents:
            print("❌ ASSEMBLYAI_API_KEY not found in .env file")
            return False
    
    print("✓ .env file")
    return True

def main():
    """Run all checks."""
    print("Running setup checks...\n")
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_ffmpeg(),
        check_directories(),
        check_env_file()
    ]
    
    print("\nSummary:")
    if all(checks):
        print("✓ All checks passed! The system is ready to use.")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
