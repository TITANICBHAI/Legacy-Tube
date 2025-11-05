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

**Recent UI Improvements (Nov 2025):**
- Enhanced status pages with emoji indicators for better visual clarity on feature phones
- Clearer step-by-step instructions on error pages with numbered actions
- Prominent download button with green styling on completion page
- Better error recovery guidance with direct links to cookie upload page
- Improved processing status display with estimated times and auto-refresh reminders

### Feature Specifications
- **Video Conversion** (3GP Format):
    - **Resolution**: 176x144 (with aspect ratio padding)
    - **Format**: 3GP with MPEG-4 video and AAC audio
    - **Quality Presets**: Ultra Low (150k video, 10fps), Low (200k video, 12fps), Medium (300k video, 15fps), High (400k video, 18fps)
    - **Video Settings**: Variable bitrate with rate distortion optimization for better compression
    - **Audio Settings**: Fixed at 24kbps AAC, 16kHz, mono (constant across all presets for feature phone compatibility)
    - **Max Duration**: 6 hours (configurable)
    - **Max File Size**: 500MB (configurable)
- **Audio Conversion** (MP3 Format):
    - **Quality Presets**: 128kbps (default), 192kbps, 256kbps, 320kbps
    - **Compression**: VBR mode with optimized quality settings
    - **Sample Rate**: 44.1-48kHz based on quality
    - **Channels**: Mono for 128k/192k, stereo for 256k/320k
    - **Note**: Minimum 128kbps to avoid YouTube download errors
- **YouTube Authentication**: Supports cookie-based authentication to bypass YouTube's bot detection and rate limiting, allowing access to most public videos without requiring a logged-in YouTube account.
- **Background Processing**: Video download and conversion occur asynchronously using Python threading, with status updates available on a dedicated page.
- **File Management**: Automatic cleanup system deletes converted files after 6 hours and manages orphaned/failed jobs.
- **Network Optimization**: Designed for 2G networks with minimal data usage, intelligent retry logic, and optimized download strategies (e.g., using Android TV client API via yt-dlp).
- **YouTube IP Block Bypass**: Multiple strategies to bypass YouTube's cloud IP blocking:
    - **IPv6 Support**: Optional IPv6 usage (less blocked by YouTube)
    - **Proxy Support**: Configure HTTP/SOCKS5 proxy via environment variable
    - **Rate Limiting**: Configurable download speed limits to avoid 429 errors
    - **Enhanced User Agents**: Mimics real Android/iOS devices
    - **Cookie Authentication**: Upload browser cookies for authenticated access
- **Disk Space Management**: Advanced monitoring for Render's 2GB /tmp limit:
    - **Real-time Monitoring**: Checks disk space before downloads and conversions
    - **Emergency Cleanup**: Automatic cleanup when space drops below threshold
    - **Pre-download Checks**: Validates sufficient space before starting
    - **Configurable Thresholds**: Alert when free space < 1.5GB (configurable)
- **File Splitting** (NEW - Nov 2025): Advanced file splitting for easier downloads on 2G networks:
    - **Split by Number of Parts**: Divide files into equal-sized parts (2-100 parts)
    - **Split by Size**: Split files by specifying size per part (0.1MB - 1000MB)
    - **Split by Duration**: Split videos by time duration (for 3GP videos only)
    - **Sequential Numbering**: Parts numbered as file_id_part1.ext, file_id_part2.ext, etc.
    - **Auto-generated Join Commands**: Dynamic Windows/Mac/Linux commands with actual filenames
    - **Smart Validation**: Prevents zero-byte parts, validates against file size
    - **File Info Display**: Shows file size, duration, and format before splitting
    - **Feature Phone Friendly**: Large buttons, clear instructions, no JavaScript required

### System Design Choices
- **Stateless Design**: Uses temporary file storage and a simple JSON file for status tracking instead of a traditional database, making it suitable for lightweight deployments.
- **Robust Error Handling**: Implements retry mechanisms, specific error messages for various YouTube issues (age-restricted, geo-blocked), and comprehensive timeout settings for downloads and conversions.
- **Deployment**: Optimized for cloud platforms with a focus on Render's free tier, including Gunicorn for production, memory/CPU optimizations, and graceful shutdown handlers. Docker support is provided for containerized deployment.

### Core Routes
- `GET /`: Homepage for URL input.
- `POST /convert`: Initiates video conversion.
- `GET /status/<file_id>`: Displays conversion progress and file splitting options.
- `GET /download/<file_id>`: Serves the converted 3GP/MP3 file.
- `POST /split/<file_id>`: Splits file into parts (by number, size, or duration).
- `GET /split_downloads/<file_id>`: Shows download links for all split parts.
- `GET /download_part/<filename>`: Downloads a specific split part.
- `GET /search` & `POST /search`: YouTube search interface (no API key required).
- `GET /cookies` & `POST /cookies`: Interface for managing YouTube authentication cookies.
- `GET /health`: Health check endpoint.

## External Dependencies
- **yt-dlp**: Python library for downloading videos from YouTube and other sites.
- **FFmpeg**: Open-source multimedia framework for video and audio conversion. **Note**: Render's native environment includes ffmpeg pre-installed (v4.1.11-0), so no custom binaries needed.
- **Flask**: Python web framework used for the backend.
- **Gunicorn**: WSGI HTTP Server for UNIX (used in production deployments).

## Documentation
- **RENDER_ADVANCED.md**: Complete advanced guide for Render deployment with YouTube IP block bypass solutions, rate limiting, disk space management, and troubleshooting
- **NO_CARD_FREE_HOSTING.md**: Guide to 100% free hosting platforms without credit card requirements (Render, Replit, Railway comparison)
- **ERROR_GUIDE.md**: Comprehensive error troubleshooting with solutions for IP blocking (403), rate limiting (429), disk space issues, and more
- **COOKIE_SETUP_GUIDE.md**: Instructions for setting up YouTube cookies to bypass IP blocks and bot detection
- **ADVANCED_TINKERING.md**: Advanced customization guide for developers who want to modify settings, optimize performance, or add new features
- **DOCKER_DEPLOYMENT.md**: Docker deployment instructions and optimizations

## Recent Updates

### November 5, 2025 (Latest Update)
- ✅ **NEW**: File splitting feature for easier 2G downloads - split files by parts, size, or duration
- ✅ **NEW**: File info display on completion page (size, duration, format)
- ✅ **NEW**: Auto-generated join commands with actual filenames for Windows/Mac/Linux
- ✅ **NEW**: Sequential part numbering (part1, part2, part3...) for easy tracking
- ✅ **NEW**: Smart validation prevents zero-byte parts and impossible split requests
- ✅ **NEW**: Duration-based splitting for 3GP videos (split by minutes)
- ✅ **NEW**: Feature phone friendly split UI with large buttons and clear instructions
- ✅ **NEW**: Split downloads page showing all parts with individual download links

### November 2, 2025
- ✅ **NEW**: Updated High 3GP quality to 18 fps (was 15 fps) for smoother playback
- ✅ **NEW**: Upgraded YouTube blocking prevention with 2025 user agents (iOS 18.1, Android 14)
- ✅ **NEW**: Added Android TV download strategy for better reliability
- ✅ **NEW**: Feature phone UI improvements - clearer status messages, better error recovery
- ✅ **NEW**: Enhanced download/error pages with emoji indicators and step-by-step guidance
- ✅ **CRITICAL FIX**: Fixed search function URL construction bug that could return invalid YouTube URLs
- ✅ **CRITICAL FIX**: Fixed cleanup function to properly delete both .3gp and .mp3 files (was only deleting .3gp)
- ✅ Auto-download FFmpeg if not found - no more deployment failures!
- ✅ FFmpeg detection now logs actual paths to help discover Render's locations
- ✅ Enhanced search function with comprehensive error handling (timeout, 429, 403, bot detection)
- ✅ Added cookie support to search requests for better rate-limit handling and bot detection bypass
- ✅ Added 30-second socket timeout to search for 2G network compatibility
- ✅ Improved search result validation and empty result handling
- ✅ Fixed quality preset options in search page to properly match backend presets
- ✅ Added quality presets: 4 options for MP3 (128-320kbps), 4 options for 3GP video
- ✅ Improved MP3 compression with VBR mode and better quality settings
- ✅ Enhanced 3GP compression with rate distortion optimization for smaller files
- ✅ Added bin/ folder support for pre-placed FFmpeg binaries (Render deployment)
- ✅ Updated build.sh to check bin/ folder first before downloading binaries
- ✅ User can now choose quality or use auto-select (128kbps MP3, Low 3GP)

### October 27, 2025
- ✅ Added YouTube IP block bypass with IPv6, proxy, and rate limiting support
- ✅ Implemented advanced disk space monitoring for Render's 2GB /tmp limit
- ✅ Enhanced error detection for IP blocks (403) and rate limiting (429)
- ✅ Added emergency cleanup system when disk space is low
- ✅ Updated download strategies with better device mimicking (Android TV, iOS)
- ✅ Created comprehensive documentation for known issues and solutions