#!/bin/bash
set -e

# Directory to install FFmpeg
FFMPEG_DIR="$HOME/bin"
mkdir -p "$FFMPEG_DIR"

# Check if FFmpeg is already installed
if ! command -v ffmpeg &> /dev/null; then
  echo "FFmpeg not found. Installing v7.1.1..."

  # Download the static build
  curl -L -o ffmpeg.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-7.1.1-amd64-static.tar.xz

  # Extract ffmpeg and ffprobe into $HOME/bin
  tar -xvf ffmpeg.tar.xz --strip-components=1 -C "$FFMPEG_DIR" ffmpeg-7.1.1-amd64-static/ffmpeg ffmpeg-7.1.1-amd64-static/ffprobe

  # Make them executable
  chmod +x "$FFMPEG_DIR/ffmpeg" "$FFMPEG_DIR/ffprobe"

  # Cleanup
  rm -rf ffmpeg.tar.xz ffmpeg-7.1.1-amd64-static

  echo "FFmpeg installed successfully in $FFMPEG_DIR."
else
  echo "FFmpeg already installed. Skipping download."
fi
