#!/usr/bin/env bash

set -o errexit

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Making binaries executable..."
chmod +x bin/ffmpeg bin/ffprobe

# Add local bin to PATH for build and runtime
export PATH="$PWD/bin:$PATH"
echo "PATH set to: $PATH"

echo "Creating download folder..."
mkdir -p /tmp/downloads

echo "Build completed successfully!"
