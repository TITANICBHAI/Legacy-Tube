#!/usr/bin/env bash

set -o errexit

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing system dependencies..."
apt-get update
apt-get install -y ffmpeg

echo "Creating required folders..."
mkdir -p /tmp/downloads
mkdir -p /tmp/cookies

echo "Build completed successfully!"
