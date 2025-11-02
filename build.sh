#!/usr/bin/env bash

set -o errexit

echo "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "Installing system dependencies..."
FFMPEG_INSTALLED=false

# Try system package managers first
if command -v apt-get &> /dev/null; then
    echo "Trying apt-get installation..."
    apt-get update -qq && apt-get install -y -qq ffmpeg && FFMPEG_INSTALLED=true || echo "apt-get failed, will try static binary"
elif command -v apk &> /dev/null; then
    echo "Trying apk installation..."
    apk add --no-cache ffmpeg && FFMPEG_INSTALLED=true || echo "apk failed, will try static binary"
fi

# Fallback: Download static FFmpeg binary for Render free tier
if [ "$FFMPEG_INSTALLED" = false ]; then
    echo "Downloading static FFmpeg binary..."
    mkdir -p /opt/bin
    
    # Download FFmpeg static build (latest version)
    wget -q https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -O /tmp/ffmpeg.tar.xz
    
    # Extract
    tar -xf /tmp/ffmpeg.tar.xz -C /tmp/
    
    # Find and copy the binaries
    FFMPEG_DIR=$(find /tmp -type d -name "ffmpeg-*-amd64-static" | head -n 1)
    cp "$FFMPEG_DIR/ffmpeg" /opt/bin/ffmpeg
    cp "$FFMPEG_DIR/ffprobe" /opt/bin/ffprobe
    chmod +x /opt/bin/ffmpeg
    chmod +x /opt/bin/ffprobe
    
    # Clean up
    rm -rf /tmp/ffmpeg.tar.xz /tmp/ffmpeg-*
    
    # Add to PATH
    export PATH="/opt/bin:$PATH"
    echo "Static FFmpeg and FFprobe installed to /opt/bin/"
fi

echo "Verifying installations..."
python --version

if command -v ffmpeg &> /dev/null; then
    ffmpeg -version | head -1
    echo "FFmpeg path: $(which ffmpeg)"
else
    echo "ERROR: FFmpeg not found!"
    exit 1
fi

if command -v yt-dlp &> /dev/null; then
    yt-dlp --version
else
    echo "yt-dlp installed via pip (requirements.txt)"
fi

echo "Creating required folders..."
mkdir -p /tmp/downloads
mkdir -p /tmp/cookies

echo "Build completed successfully!"
