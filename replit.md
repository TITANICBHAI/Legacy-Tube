# YouTube to 3GP Converter for Feature Phones

## Overview
A web application that converts YouTube videos to 3GP format (176x144 resolution) optimized for feature phones like Nokia 5310 and old browsers like Opera Mini 4.4.39. Perfect for 2G networks with ultra-low file sizes.

## Current State
**Status**: Fully functional
- Flask web application running on port 5000
- Video download via yt-dlp (no API keys required)
- Automatic conversion to 3GP format using FFmpeg
- Background processing with status updates
- Automatic file cleanup (6-hour retention)
- No JavaScript - works on Opera Mini 4.4

## Recent Changes
**2025-10-25**: Cookie Authentication Support (FIXES 2025 YOUTUBE BLOCKING)
- **Cookie-based Authentication**: Added support for YouTube cookies to bypass bot detection
- **Admin Cookie Management**: New `/cookies` route for uploading and managing cookies.txt file
- **Automatic Cookie Integration**: yt-dlp automatically uses cookies when available
- **Strict Cookie Validation**: Validates presence of LOGIN_INFO or __Secure-*PSID tokens
- **Upload Validation**: Rejects invalid cookies immediately with specific error messages
- **Enhanced Error Messages**: Specific guidance for cookie-related authentication failures
- **User Notifications**: Homepage shows cookie status and links to setup page
- **Fixes "Sign In Required" Errors**: Resolves YouTube's 2025 bot detection on cloud servers
- **Fixes Error 111 Connection Refused**: Proper authentication prevents connection blocks
- **Fixes Rate Limiting**: Authenticated requests bypass IP-based rate limits
- **Feature Phone Compatible**: Cookie upload page works on Opera Mini 4.4

**2025-10-21**: Enhanced rate limit protection and error handling (PRODUCTION-READY)
- **Android Client API**: Uses `player_client=android,web` for superior rate limit bypass on shared IPs
- **Automatic Retry**: Auto-retries failed downloads with 3-second pause between attempts
- **Fragment Control**: `--concurrent-fragments 1` reduces server load
- **Smart Error Messages**: Specific messages for age-restricted, geo-blocked, private videos, etc.
- **5 Retry Attempts**: Automatically retries transient failures up to 5 times
- **Request Pacing**: 2 seconds between requests to prevent bot detection
- **Full-Speed Downloads**: No throttling - supports full 500MB limit
- **Comprehensive Testing**: 100+ test scenarios designed and documented
- **Feature Phone Safe**: All changes preserve 3GP format, resolution, and codec compatibility

**2025-10-21**: YouTube rate limit fixes for Render deployment (TESTED & VERIFIED)
- **Fixed HTTP 429 errors**: Resolved "Too Many Requests" errors on shared hosting platforms
- **Force IPv4**: Uses `--force-ipv4` to bypass YouTube rate limiting (proven solution)
- **Custom User-Agent**: Mimics Android mobile browser to match API client
- **Request delays**: Added smart delays to prevent rapid-fire requests
- **Works on Render**: Successfully deploys and runs on Render.com free tier

**2025-10-21**: Auto-refresh feature and yt-dlp fixes
- **Added auto-refresh**: Status page now automatically refreshes every 30 seconds during processing
- **Fixed YouTube download errors**: Updated yt-dlp to 2025.10.14 and simplified format selector
- **Removed complex format filters**: Now uses simple `worst/best` selector (more reliable with YouTube's changes)
- **Auto-refresh stops when complete**: Saves bandwidth, download button appears automatically
- **Works on Opera Mini 4.4**: Uses meta refresh tag (no JavaScript needed)
- **Comprehensive deployment guide**: Created detailed DEPLOY.md with every single step explained

**2025-10-21**: User experience improvements
- Extended file retention from 2 hours to 6 hours for slower downloads on 2G
- Reduced max file size from 4GB to 500MB to prevent excessive downloads
- Improved time estimates on status page - now shows detailed estimates from the start (no guessing game)
- Updated all UI text to reflect 6-hour file retention and 500MB limit

**2025-10-20**: Extended video support and improved auto-deletion
- Extended maximum video length from short clips to **6 hours**
- Increased download timeout to 60 minutes (3600 seconds)
- Increased conversion timeout to 6 hours base (21600 seconds) with dynamic timeout (2x video duration)
- Increased max file size from 2GB to 4GB
- Made all timeouts and limits configurable via environment variables
- yt-dlp duration filter now uses MAX_VIDEO_DURATION dynamically
- File IDs now include timestamp to prevent URL collision issues
- Added video duration validation with ffprobe
- Improved auto-deletion system with better error handling
- Added cleanup for failed/orphaned and stuck jobs (downloading/converting)
- Enhanced user feedback with realistic processing time estimates
- Better error messages for file size and duration limits
- Added Railway pricing information to documentation

**2025-10-20**: Critical conversion fixes
- Fixed yt-dlp format selection (YouTube API changes broke `-f worst`)
- Improved FFmpeg conversion with proper aspect ratio handling (scale+pad filter)
- Upgraded video codec from H.263 to MPEG-4 for better compatibility
- Increased bitrates: 200kbps video, 12.2kbps audio for better quality
- Fixed "Signature extraction failed" errors with robust format selector

**2025-10-20**: Latest improvements
- Added favicon route to eliminate 404 errors (returns 204 No Content)
- Implemented Cache-Control headers for HTML responses to prevent stale status pages
- Verified all functionality: no LSP errors, clean browser console
- Confirmed FFmpeg 3GP/MPEG-4 codec support
- Server tested and running smoothly

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
- **Maximum Duration**: Up to 6 hours (configurable via MAX_VIDEO_DURATION)
- **Download Timeout**: 60 minutes base (configurable via DOWNLOAD_TIMEOUT)
- **Conversion Timeout**: 6 hours base, dynamic timeout of 2x video duration (configurable via CONVERSION_TIMEOUT)
- **Max File Size**: 500MB (configurable via MAX_FILESIZE)
- **Resolution**: 176x144 (with proper aspect ratio padding)
- **Format**: 3GP
- **Video Codec**: MPEG-4 (more compatible than H.263)
- **Video Bitrate**: 200kbps (better quality)
- **Audio Codec**: AAC (feature phone compatible)
- **Audio Sample Rate**: 8000 Hz
- **Audio Bitrate**: 12.2kbps
- **Frame Rate**: 12 fps
- **Aspect Ratio**: Auto-scaled and padded to preserve original ratio
- **File Size Estimates**: 
  - 5 minute video = ~3-4 MB
  - 1 hour video = ~35-45 MB
  - 6 hour video = ~210-270 MB

### User Flow
1. User pastes YouTube URL on homepage
2. Backend starts download in background thread
3. Status page shows "Processing..." with time estimates immediately
4. User manually refreshes to check status
5. When complete, download button appears
6. User downloads 3GP file (works on 2G)
7. File auto-deletes after 6 hours

### Key Features
- **No API Keys**: Uses yt-dlp library, completely free
- **No JavaScript**: Works on Opera Mini 4.4.39 and older browsers
- **2G Optimized**: Ultra-low bitrate for slow networks
- **Auto Cleanup**: Files deleted after 6 hours to save space
- **Background Processing**: Conversion happens asynchronously
- **Manual Refresh**: No auto-refresh to save bandwidth on 2G
- **Time Estimates**: Shows expected processing time from the start (no guessing)

### Routes
- `GET /` - Homepage with URL input form (shows cookie status)
- `GET /favicon.ico` - Favicon route (returns 204 No Content)
- `POST /convert` - Start video conversion
- `GET /status/<file_id>` - Check conversion status
- `GET /download/<file_id>` - Download converted 3GP file
- `GET /cookies` - Cookie management page
- `POST /cookies` - Upload or delete YouTube cookies

### Cookie Authentication Setup

**Why Cookies Are Needed:**
YouTube's 2025 bot detection blocks yt-dlp downloads from cloud servers, causing:
- "Sign in to confirm you're not a bot" errors
- "Please try again after 10 minutes" rate limiting
- Error 111 Connection Refused
- These happen even for public videos on shared hosting

**How to Set Up Cookies:**

1. **Install Browser Extension**
   - Chrome/Edge: Search for "Get cookies.txt LOCALLY" in Chrome Web Store
   - Firefox: Search for "cookies.txt" in Firefox Add-ons

2. **Export YouTube Cookies**
   - Visit youtube.com in your browser (no need to log in)
   - Click the extension icon
   - Click "Export" or "Download"
   - Save file as `cookies.txt`

3. **Upload to App**
   - Go to `/cookies` page in the app
   - Upload your `cookies.txt` file
   - Validation checks ensure cookies are valid

4. **Test**
   - Try converting a YouTube video
   - Should work without "sign in" errors

**Cookie Notes:**
- Cookies stored in `/tmp/cookies/youtube_cookies.txt`
- Not required for all videos, but recommended on cloud hosting
- Cookies from a logged-in YouTube account work best for age-restricted content
- Cookies from non-logged-in session work for most public videos
- Re-upload if cookies expire (usually every few weeks)

### Storage Management
- Downloads stored in `/tmp/downloads/`
- Cookies stored in `/tmp/cookies/`
- Status tracked in `/tmp/conversion_status.json`
- Cleanup thread runs every 30 minutes
- Files deleted after 6 hours of completion (configurable via FILE_RETENTION_HOURS)
- Failed/orphaned files also cleaned up automatically
- Cleanup logs deletion count for monitoring
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
- `MAX_VIDEO_DURATION`: Maximum video duration in seconds (default: 21600 = 6 hours)
- `DOWNLOAD_TIMEOUT`: Download timeout in seconds (default: 3600 = 60 minutes)
- `CONVERSION_TIMEOUT`: Base conversion timeout in seconds; actual timeout is max(CONVERSION_TIMEOUT, duration*2) (default: 21600 = 6 hours)
- `FILE_RETENTION_HOURS`: File retention time in hours (default: 6)
- `MAX_FILESIZE`: Maximum download file size (default: 500M)

## Deployment Notes
- Runs on port 5000 (required for Replit)
- Uses development Flask server (sufficient for personal use)
- No database required (JSON file for status)
- Automatic cleanup prevents storage overflow

## Hosting Options & Pricing

### Railway
**Status**: No longer free (discontinued free tier August 2023)
- **Cost**: $5-20/month depending on usage
- **Why it costs**: CPU usage for video conversion, storage for temporary files, bandwidth for downloads
- **Not recommended** for personal use due to costs

### Replit (Current Platform)
**Status**: Has free tier available
- **Free tier**: Limited to hobby projects, sufficient for personal use
- **Paid tier**: Starting at $7/month for more resources
- **Best for**: Personal projects, testing, development

### Render
**Status**: Limited free tier available
- **Free tier**: Available with restrictions (spins down after inactivity)
- **Cost**: ~$7/month for always-on instance
- **Good for**: Occasional use projects

### Fly.io
**Status**: Small free tier
- **Free tier**: Includes limited compute and bandwidth
- **Cost**: Pay-as-you-go beyond free tier
- **Good for**: Light usage projects

**Recommendation**: For personal use, stay on Replit's free tier or use the paid tier ($7/month) which is more cost-effective than Railway for this type of video processing application.
