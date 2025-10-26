#!/usr/bin/env bash

set -o errexit

echo "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    apt-get update -qq
    apt-get install -y -qq ffmpeg yt-dlp 2>/dev/null || true
elif command -v apk &> /dev/null; then
    apk add --no-cache ffmpeg yt-dlp
fi

echo "Verifying installations..."
python --version
ffmpeg -version | head -1
yt-dlp --version

echo "Creating required folders..."
mkdir -p /tmp/downloads
mkdir -p /tmp/cookies

echo "Build completed successfully!"
