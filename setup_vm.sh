#!/bin/bash

# Setup script for VM dependencies
echo "🚀 Setting up VM dependencies for SaaS Backend..."

# Update package list
echo "📦 Updating package list..."
sudo apt update

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y \
    ffmpeg \
    yt-dlp \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    python3-venv

# Install Python dependencies using uv
echo "🐍 Installing Python dependencies..."
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
fi

# Sync dependencies
echo "📚 Syncing project dependencies..."
uv sync

echo "✅ Setup complete! You can now run the application with: uv run run.py"
