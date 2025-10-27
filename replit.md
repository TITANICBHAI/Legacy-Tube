# YouTube to 3GP Converter for Feature Phones

## Overview
This project is a web application designed to convert YouTube videos into the 3GP format (176x144 resolution), specifically optimized for feature phones like the Nokia 5310 and older web browsers such as Opera Mini 4.4. The primary goal is to provide a solution for accessing YouTube content on 2G networks, emphasizing ultra-low file sizes and minimal bandwidth usage. It aims to be a free and accessible tool for users with older devices.

## User Preferences
- Target device: Nokia 5310 feature phone
- Browser: Opera Mini 4.4.39
- Network: 2G speeds
- No ads, 100% free for both developer and users
- Minimal bandwidth usage (no auto-refresh, no JavaScript)

## System Architecture

### Technology Stack
- **Backend**: Flask (Python 3.11)
- **Video Download**: yt-dlp (no API required)
- **Video Conversion**: FFmpeg
- **Storage**: `/tmp/downloads` (temporary file storage), `/tmp/cookies` (cookie storage), `/tmp/conversion_status.json` (status tracking)
- **Background Processing**: Python threading

### UI/UX Decisions
The application features ultra-lightweight HTML templates designed for feature phone compatibility. It is built with no JavaScript to ensure functionality on Opera Mini 4.4 and other older browsers, relying on manual page refreshes for status updates and meta refresh tags where necessary. The UI provides clear status updates and time estimates for conversions.

### Feature Specifications
- **Video Conversion**:
    - **Resolution**: 176x144 (with aspect ratio padding)
    - **Format**: 3GP
    - **Video Codec**: MPEG-4 (200kbps bitrate, 12 fps)
    - **Audio Codec**: AAC (12.2kbps bitrate, 8000 Hz sample rate)
    - **Max Duration**: 6 hours (configurable)
    - **Max File Size**: 500MB (configurable)
- **YouTube Authentication**: Supports cookie-based authentication to bypass YouTube's bot detection and rate limiting, allowing access to most public videos without requiring a logged-in YouTube account.
- **Background Processing**: Video download and conversion occur asynchronously using Python threading, with status updates available on a dedicated page.
- **File Management**: Automatic cleanup system deletes converted files after 6 hours and manages orphaned/failed jobs.
- **Network Optimization**: Designed for 2G networks with minimal data usage, intelligent retry logic, and optimized download strategies (e.g., using Android TV client API via yt-dlp, `--force-ipv4`).

### System Design Choices
- **Stateless Design**: Uses temporary file storage and a simple JSON file for status tracking instead of a traditional database, making it suitable for lightweight deployments.
- **Robust Error Handling**: Implements retry mechanisms, specific error messages for various YouTube issues (age-restricted, geo-blocked), and comprehensive timeout settings for downloads and conversions.
- **Deployment**: Optimized for cloud platforms with a focus on Render's free tier, including Gunicorn for production, memory/CPU optimizations, and graceful shutdown handlers. Docker support is provided for containerized deployment.

### Core Routes
- `GET /`: Homepage for URL input.
- `POST /convert`: Initiates video conversion.
- `GET /status/<file_id>`: Displays conversion progress.
- `GET /download/<file_id>`: Serves the converted 3GP file.
- `GET /cookies` & `POST /cookies`: Interface for managing YouTube authentication cookies.
- `GET /health`: Health check endpoint.

## External Dependencies
- **yt-dlp**: Python library for downloading videos from YouTube and other sites.
- **FFmpeg**: Open-source multimedia framework for video and audio conversion. **Note**: Render's native environment includes ffmpeg pre-installed (v4.1.11-0), so no custom binaries needed.
- **Flask**: Python web framework used for the backend.
- **Gunicorn**: WSGI HTTP Server for UNIX (used in production deployments).

## Documentation
- **RENDER_DEPLOYMENT.md**: Comprehensive guide for deploying to Render's free tier
- **DOCKER_DEPLOYMENT.md**: Docker deployment instructions and optimizations
- **COOKIE_SETUP_GUIDE.md**: Instructions for setting up YouTube cookies
- **ADVANCED_TINKERING.md**: Advanced customization guide for developers who want to modify settings, optimize performance, or add new features