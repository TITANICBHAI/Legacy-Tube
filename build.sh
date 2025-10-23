#!/usr/bin/env bash

set -o errexit

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing system dependencies..."
apt-get update
apt-get install -y ffmpeg

chmod +x bin/ffmpeg bin/ffprobe


echo "Creating download folder..."
mkdir -p /tmp/downloads

echo "Build completed successfully!"
