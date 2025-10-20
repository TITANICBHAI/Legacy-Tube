# YouTube to 3GP Converter for Feature Phones

## Overview
A web application that converts YouTube videos to 3GP format (176x144 resolution) optimized for feature phones like Nokia 5310 and old browsers like Opera Mini 4.4.39. Perfect for 2G networks with ultra-low file sizes.

## Current State
**Status**: Fully functional
- Flask web application running on port 5000
- Video download via yt-dlp (no API keys required)
- Automatic conversion to 3GP format using FFmpeg
- Background processing with status updates
- Automatic file cleanup (2-hour retention)
- No JavaScript - works on Opera Mini 4.4

## Recent Changes
**2025-10-20**: Initial implementation
- Created Flask app with route handlers
- Implemented yt-dlp + FFmpeg conversion pipeline
- Built ultra-lightweight HTML templates for feature phones
- Added background threading for async video processing
- Implemented automatic cleanup system (2-hour file retention)
- Configured workflow to run on port 5000
- Fixed thread-safety with atomic update_status() function
- Changed audio codec from AMR-NB to AAC for broader compatibility

## Project Architecture

### Technology Stack
- **Backend**: Flask (Python 3.11)
- **Video Download**: yt-dlp (no API required)
- **Video Conversion**: FFmpeg
- **Storage**: /tmp/downloads (temporary storage)
- **Background Processing**: Python threading

### File Structure
```
.
├── app.py                 # Main Flask application
├── templates/
│   ├── base.html         # Base template with minimal CSS
│   ├── index.html        # Home page with URL input form
│   └── status.html       # Conversion status and download page
├── pyproject.toml        # Python dependencies
└── replit.md            # Project documentation
```

### Video Conversion Settings
- **Resolution**: 176x144 (perfect for Nokia feature phones)
- **Format**: 3GP
- **Video Codec**: H.263
- **Video Bitrate**: 64kbps
- **Audio Codec**: AAC (feature phone compatible)
- **Audio Sample Rate**: 8000 Hz
- **Audio Bitrate**: 16kbps
- **Frame Rate**: 12 fps
- **Result**: 3-5 minute video = ~2-3 MB

### User Flow
1. User pastes YouTube URL on homepage
2. Backend starts download in background thread
3. Status page shows "Converting..." message
4. User manually refreshes to check status
5. When complete, download button appears
6. User downloads 3GP file (works on 2G)
7. File auto-deletes after 2 hours

### Key Features
- **No API Keys**: Uses yt-dlp library, completely free
- **No JavaScript**: Works on Opera Mini 4.4.39 and older browsers
- **2G Optimized**: Ultra-low bitrate for slow networks
- **Auto Cleanup**: Files deleted after 2 hours to save space
- **Background Processing**: Conversion happens asynchronously
- **Manual Refresh**: No auto-refresh to save bandwidth on 2G

### Routes
- `GET /` - Homepage with URL input form
- `POST /convert` - Start video conversion
- `GET /status/<file_id>` - Check conversion status
- `GET /download/<file_id>` - Download converted 3GP file

### Storage Management
- Downloads stored in `/tmp/downloads/`
- Status tracked in `/tmp/conversion_status.json`
- Cleanup thread runs every 30 minutes
- Files deleted after 2 hours of completion
- Maximum 2-3 concurrent conversions expected (personal use)

## User Preferences
- Target device: Nokia 5310 feature phone
- Browser: Opera Mini 4.4.39
- Network: 2G speeds
- No ads, 100% free for both developer and users
- Minimal bandwidth usage (no auto-refresh, no JavaScript)

## Dependencies
- Python 3.11
- Flask (web framework)
- yt-dlp (system package - YouTube downloader)
- FFmpeg (system package - video converter)

## Environment Variables
- `SESSION_SECRET`: Flask session secret (set via Replit Secrets)

## Deployment Notes
- Runs on port 5000 (required for Replit)
- Uses development Flask server (sufficient for personal use)
- No database required (JSON file for status)
- Automatic cleanup prevents storage overflow
