#!/bin/bash

# Text colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_status() {
    echo -e "${2}$1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
        print_status "Found Python version: $python_version" "$GREEN"
        if python3 -c 'import sys; assert sys.version_info >= (3,8)' 2>/dev/null; then
            return 0
        else
            print_status "Python 3.8 or higher is required!" "$RED"
            return 1
        fi
    else
        print_status "Python 3 not found!" "$RED"
        return 1
    fi
}

# Function to create virtual environment
create_venv() {
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..." "$YELLOW"
        python3 -m venv venv
        if [ $? -eq 0 ]; then
            print_status "Virtual environment created successfully" "$GREEN"
        else
            print_status "Failed to create virtual environment" "$RED"
            exit 1
        fi
    else
        print_status "Virtual environment already exists" "$YELLOW"
    fi
}

# Function to install system dependencies
install_system_deps() {
    print_status "Checking system dependencies..." "$YELLOW"
    
    # Check if we're on a Debian-based system
    if command_exists apt-get; then
        print_status "Detected Debian-based system" "$GREEN"
        
        # Update package list
        print_status "Updating package list..." "$YELLOW"
        sudo apt-get update
        
        # Install required packages
        print_status "Installing system dependencies..." "$YELLOW"
        sudo apt-get install -y \
            ffmpeg \
            python3-pip \
            python3-venv \
            build-essential \
            python3-dev \
            portaudio19-dev \
            libffi-dev \
            libssl-dev
            
    # Check if we're on a Red Hat-based system
    elif command_exists yum || command_exists dnf; then
        print_status "Detected Red Hat-based system" "$GREEN"
        
        # Use dnf if available, otherwise use yum
        if command_exists dnf; then
            PKG_MANAGER="dnf"
        else
            PKG_MANAGER="yum"
        fi
        
        # Install required packages
        print_status "Installing system dependencies..." "$YELLOW"
        sudo $PKG_MANAGER install -y \
            ffmpeg \
            python3-pip \
            python3-devel \
            gcc \
            portaudio-devel \
            libffi-devel \
            openssl-devel
            
    else
        print_status "Unsupported package manager. Please install dependencies manually." "$RED"
        print_status "Required packages: ffmpeg, python3-pip, python3-venv" "$YELLOW"
        exit 1
    fi
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..." "$YELLOW"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..." "$YELLOW"
    pip install --upgrade pip
    
    # Install requirements
    print_status "Installing required Python packages..." "$YELLOW"
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        print_status "Python dependencies installed successfully" "$GREEN"
    else
        print_status "Failed to install Python dependencies" "$RED"
        exit 1
    fi
}

# Function to create .env file
create_env_file() {
    if [ ! -f ".env" ]; then
        print_status "Creating .env file..." "$YELLOW"
        read -p "Enter your AssemblyAI API key: " api_key
        echo "ASSEMBLYAI_API_KEY=$api_key" > .env
        print_status ".env file created successfully" "$GREEN"
    else
        print_status ".env file already exists" "$YELLOW"
    fi
}

# Main installation process
main() {
    print_status "Starting setup process..." "$YELLOW"
    
    # Check Python version
    check_python_version
    if [ $? -ne 0 ]; then
        exit 1
    fi
    
    # Install system dependencies
    install_system_deps
    
    # Create virtual environment
    create_venv
    
    # Install Python dependencies
    install_python_deps
    
    # Create .env file
    create_env_file
    
    # Run test script
    print_status "Running setup tests..." "$YELLOW"
    source venv/bin/activate
    python test_setup.py
    
    if [ $? -eq 0 ]; then
        print_status "\nSetup completed successfully! 🎉" "$GREEN"
        print_status "\nTo start using the application:" "$YELLOW"
        print_status "1. Activate the virtual environment: source venv/bin/activate" "$NC"
        print_status "2. Run the application: python main.py" "$NC"
    else
        print_status "\nSetup completed with some warnings. Please check the messages above." "$YELLOW"
    fi
}

# Run main installation
main
