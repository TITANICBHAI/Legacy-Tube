# YouTube to 3GP Converter for Feature Phones

## Overview
This project is a web application that converts YouTube videos to the 3GP format (176x144 resolution) and MP3 audio, optimized for feature phones like the Nokia 5310 and older web browsers such as Opera Mini 4.4. Its main purpose is to enable access to YouTube content on 2G networks by providing ultra-low file sizes and minimal bandwidth usage. It aims to be a free and accessible tool for users with older devices. The application also includes advanced features for bypassing YouTube's anti-bot measures and efficient file splitting for easier downloads on constrained networks.

## User Preferences
- Target device: Nokia 5310 feature phone
- Browser: Opera Mini 4.4.39
- Network: 2G speeds
- No ads, 100% free for both developer and users
- Minimal bandwidth usage (no auto-refresh, no JavaScript)

## System Architecture

### Technology Stack
- **Backend**: Flask (Python 3.11)
- **Video Download**: yt-dlp
- **Video Conversion**: FFmpeg
- **Storage**: Temporary file system (`/tmp`) for downloads, cookies, and status tracking.
- **Background Processing**: Python threading for asynchronous operations.

### UI/UX Decisions
The application features ultra-lightweight HTML templates with no JavaScript, optimized for feature phone compatibility and older browsers like Opera Mini 4.4. It relies on manual page refreshes or meta refresh tags for status updates. The UI provides clear conversion status, time estimates, and step-by-step instructions for error recovery. Recent improvements include emoji indicators and prominent download buttons.

### Feature Specifications
- **Video Conversion** (3GP Format):
    - **Resolution**: 176x144 with aspect ratio padding.
    - **Format**: 3GP (MPEG-4 video, AAC audio).
    - **Quality Presets**: Ultra Low (150k, 10fps), Low (200k, 12fps), Medium (300k, 15fps), High (400k, 18fps) with variable bitrate and rate distortion optimization.
    - **Audio Settings**: 24kbps AAC, 16kHz, mono.
    - **Max Duration**: 6 hours.
    - **Max File Size**: 500MB.
- **Audio Conversion** (MP3 Format):
    - **Quality Presets**: 128kbps (default), 192kbps, 256kbps, 320kbps.
    - **Compression**: VBR mode, 44.1-48kHz sample rate, stereo channels.
- **YouTube Authentication**: Cookie-based authentication to bypass YouTube's bot detection and rate limiting.
- **Background Processing**: Asynchronous download and conversion with status updates.
- **File Management**: Automatic cleanup of converted files and failed jobs after 6 hours.
- **Network Optimization**: Designed for 2G networks with minimal data usage, intelligent retry logic, and reliable download strategies mimicking Android clients.
- **YouTube IP Block Bypass**: Supports IPv6, proxy configuration, rate limiting, enhanced user agents, custom browser headers, exponential backoff for retries, and smart error detection.
- **Disk Space Management**: Real-time monitoring of `/tmp` disk space, emergency cleanup, and pre-download checks, with configurable thresholds.
- **File Splitting**: Advanced splitting functionality by number of parts, size, or duration (for 3GP), with sequential numbering, auto-generated join commands, and smart validation.
- **Download History**: Tracks recent conversions (last 48 hours) with expiry countdowns, status indicators, and direct re-download links.
- **YouTube Search**: Integrated search interface without requiring an API key, including cookie support for better rate-limit handling.

### System Design Choices
- **Stateless Design**: Utilizes temporary file storage and a JSON file for status, avoiding a traditional database.
- **Robust Error Handling**: Comprehensive error messages, retry mechanisms, and timeout settings.
- **Deployment**: Optimized for cloud platforms (e.g., Render's free tier) using Gunicorn, with memory/CPU optimizations and graceful shutdown handlers. Docker support is available.

### Core Routes
- `GET /`: Homepage.
- `POST /convert`: Initiates conversion.
- `GET /status/<file_id>`: Displays conversion progress and splitting options.
- `GET /download/<file_id>`: Serves converted files.
- `POST /split/<file_id>`: Initiates file splitting.
- `GET /split_downloads/<file_id>`: Provides links for split parts.
- `GET /download_part/<filename>`: Downloads a specific split part.
- `GET /search`, `POST /search`: YouTube search interface.
- `GET /cookies`, `POST /cookies`: Cookie management.
- `GET /history`: Shows download history.
- `GET /health`: Health check.

## External Dependencies
- **yt-dlp**: Python library for downloading videos.
- **FFmpeg**: Multimedia framework for video/audio conversion.
- **Flask**: Python web framework.
- **Gunicorn**: WSGI HTTP Server (for production).