# YouTube to 3GP Converter for Feature Phones

## Overview
This project is a web application that converts YouTube videos to the 3GP format (176x144 resolution) and MP3 audio, optimized for feature phones like the Nokia 5310 and older web browsers such as Opera Mini 4.4. Its main purpose is to enable access to YouTube content on 2G networks by providing ultra-low file sizes and minimal bandwidth usage. It aims to be a free and accessible tool for users with older devices. The application prioritizes cookie-less operation for cloud hosting (Render free tier), using 7 different download strategies to bypass YouTube's anti-bot measures without requiring users to upload cookies from feature phones.

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
- **YouTube Authentication**: OPTIONAL cookie support for enhanced reliability. App works without cookies using 7 optimized download strategies.
- **Background Processing**: Asynchronous download and conversion with status updates.
- **File Management**: Automatic cleanup of converted files and failed jobs after 6 hours.
- **Network Optimization**: Designed for 2G networks with minimal data usage, intelligent retry logic, and reliable download strategies mimicking Android clients.
- **Cookie-Less Cloud Hosting**: Optimized for Render free tier with 7 download methods (Android Client, Android Embedded, Android Music, iOS, TV Embedded, Web Embedded, Media Connect).
- **YouTube IP Block Bypass**: Supports IPv6, proxy configuration, rate limiting, enhanced user agents, custom browser headers, smarter exponential backoff (2s→4s→8s→12s→15s→20s), realistic browser headers (DNT, Sec-Fetch-*), randomized sleep intervals, and smart error detection.
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

## Project Structure
- **Root**: Core application files (app.py, Dockerfile, render.yaml, requirements.txt)
- **templates/**: HTML templates for all pages
- **docs/**: All documentation files (deployment guides, testing reports, etc.)
- **Temporary storage**: `/tmp` directory for downloads, conversions, cookies, and status tracking

## Recent Changes

### November 12, 2025 - Render Free Tier Optimization (0.1 vCPU)
- **Conversion Queue System**: Implemented serialized processing to prevent concurrent FFmpeg processes from overloading 0.1 vCPU
  - Thread-safe Queue() processes one conversion at a time
  - Users see queue position and estimated wait times
  - Prevents CPU throttling/crashes on Render free tier
- **FFmpeg Settings**: Restored all high-quality encoding options (compression_level 9, trellis 2, mbd rd, cmp/subcmp 2, me_method hex)
  - Queue prevents overload, so CPU-intensive settings are safe
  - Conversions may be slower on 0.1 vCPU, but quality is maximized
- **No Timeouts**: Removed all conversion timeouts to allow processing to complete regardless of duration
- **Documentation**: Organized all .md files into `docs/` folder for cleaner project structure

### November 2025 - Feature Phone Splitting Fix
- **Critical Fix**: Replaced broken binary splitting with proper FFmpeg re-encoding for feature phone compatibility
- **Audio Codec Fix**: Changed 3GP split audio from MP3 to AMR-NB (Adaptive Multi-Rate Narrowband) - the standard codec for feature phones
- **Split Implementation**: 
  - Removed `split_file_by_parts` and `split_file_by_size` binary splitting (created corrupt files)
  - Implemented `split_media_file()` with proper re-encoding for each part
  - 3GP parts: H.263 video (176x144, 64kbps, 15fps) + AMR-NB audio (12.2kbps, 8kHz, mono)
  - MP3 parts: libmp3lame (128kbps, 44.1kHz, stereo)
  - Each part is a complete, standalone playable file with proper headers and keyframes
- **UI Improvements**:
  - Simplified splitting interface (removed confusing "by size" and "by duration" options)
  - Added clear messaging about re-encoding time expectations
  - Limited parts to 2-50 (was 2-100) for better reliability
- **New Feature**: Dedicated `/split_tool` page for splitting already-downloaded files
  - Shows all available MP3 and 3GP files
  - File info display (size, duration, format)
  - Added [Split] link in navigation
  - Robust error handling and input validation
  - Path traversal protection and security hardening

### November 2025 - Cookie-Less Cloud Hosting Improvements
- **Purpose**: Make app work reliably WITHOUT cookies on Render free tier, since feature phone users can't easily upload cookies
- **Download Strategies**: Expanded from 4 to 7 methods, adding Android Embedded, TV Embedded, Web Embedded, and Media Connect clients
- **Retry Logic**: Multi-level approach - yt-dlp retries each strategy 10 times internally (3-10s random sleep), then code switches strategies with exponential backoff (2s→4s→8s→12s→15s→20s). Total: up to 70 attempts (10 retries × 7 strategies)
- **Anti-Bot Headers**: Added DNT, Sec-Fetch-Dest, Sec-Fetch-Mode, Sec-Fetch-Site, Upgrade-Insecure-Requests headers to all requests
- **yt-dlp Settings**: 10 retries per strategy (total 70 with 7 strategies), longer sleep intervals (2-10s randomized), increased timeouts (45s socket timeout)
- **Error Messages**: Improved to emphasize waiting 10-15 minutes instead of requiring cookies, cookies marked as optional
- **UI Updates**: De-emphasized cookie warnings on all pages, changed from red error boxes to subtle info boxes
- **Documentation**: Updated README.md and templates to clarify cookies are optional, not required

## External Dependencies
- **yt-dlp**: Python library for downloading videos.
- **FFmpeg**: Multimedia framework for video/audio conversion.
- **Flask**: Python web framework.
- **Gunicorn**: WSGI HTTP Server (for production).