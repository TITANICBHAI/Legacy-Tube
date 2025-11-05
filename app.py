import os
import subprocess
import time
import threading
import json
import signal
import sys
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import hashlib
import yt_dlp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')

@app.after_request
def add_cache_control_headers(response):
    if response.content_type and 'text/html' in response.content_type:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

DOWNLOAD_FOLDER = '/tmp/downloads'
COOKIES_FOLDER = '/tmp/cookies'
STATUS_FILE = '/tmp/conversion_status.json'
COOKIES_FILE = os.path.join(COOKIES_FOLDER, 'youtube_cookies.txt')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(COOKIES_FOLDER, exist_ok=True)

def parse_filesize(size_str):
    """Parse filesize string like '500M', '2G' to bytes"""
    if isinstance(size_str, int):
        return size_str
    size_str = str(size_str).strip().upper()
    multipliers = {'K': 1024, 'M': 1024**2, 'G': 1024**3}
    for suffix, multiplier in multipliers.items():
        if size_str.endswith(suffix):
            return int(float(size_str[:-1]) * multiplier)
    return int(size_str)

MAX_VIDEO_DURATION = int(os.environ.get('MAX_VIDEO_DURATION', 2 * 3600))  # 2 hours for Render free tier
DOWNLOAD_TIMEOUT = int(os.environ.get('DOWNLOAD_TIMEOUT', 1800))  # 30 min max download
CONVERSION_TIMEOUT = int(os.environ.get('CONVERSION_TIMEOUT', 3600))  # 1 hour max conversion
FILE_RETENTION_HOURS = int(os.environ.get('FILE_RETENTION_HOURS', 6))
MAX_FILESIZE = parse_filesize(os.environ.get('MAX_FILESIZE', '500M'))  # 500MB for Render free tier (2GB /tmp total)

# YouTube IP block bypass settings
USE_IPV6 = os.environ.get('USE_IPV6', 'false').lower() == 'true'
PROXY_URL = os.environ.get('PROXY_URL', '')  # Optional: http://user:pass@proxy:port
USE_OAUTH = os.environ.get('USE_OAUTH', 'false').lower() == 'true'

# Advanced performance settings
RATE_LIMIT_BYTES = int(os.environ.get('RATE_LIMIT_BYTES', 0))  # 0 = unlimited, set to 500000 for 500KB/s
MAX_CONCURRENT_DOWNLOADS = int(os.environ.get('MAX_CONCURRENT_DOWNLOADS', 1))
ENABLE_DISK_SPACE_MONITORING = os.environ.get('ENABLE_DISK_SPACE_MONITORING', 'true').lower() == 'true'
DISK_SPACE_THRESHOLD_MB = int(os.environ.get('DISK_SPACE_THRESHOLD_MB', 1500))  # Alert when < 1.5GB free

# Quality presets for MP3 audio conversion
# Note: Minimum 128kbps to avoid YouTube download errors with low bitrate
MP3_QUALITY_PRESETS = {
    'medium': {
        'name': '128 kbps (Good Quality - Recommended)',
        'bitrate': '128k',
        'sample_rate': '44100',
        'vbr_quality': '4',
        'description': '~5 MB per 5 min'
    },
    'high': {
        'name': '192 kbps (High Quality)',
        'bitrate': '192k',
        'sample_rate': '44100',
        'vbr_quality': '2',
        'description': '~7 MB per 5 min'
    },
    'veryhigh': {
        'name': '256 kbps (Very High Quality)',
        'bitrate': '256k',
        'sample_rate': '48000',
        'vbr_quality': '0',
        'description': '~9 MB per 5 min'
    },
    'extreme': {
        'name': '320 kbps (Maximum Quality)',
        'bitrate': '320k',
        'sample_rate': '48000',
        'vbr_quality': '0',
        'description': '~12 MB per 5 min'
    }
}

# Quality presets for 3GP video conversion
VIDEO_QUALITY_PRESETS = {
    'ultralow': {
        'name': 'Ultra Low (2G Networks)',
        'video_bitrate': '150k',
        'audio_bitrate': '128k',
        'audio_sample_rate': '44100',
        'fps': '10',
        'description': '~2.3 MB per 5 min'
    },
    'low': {
        'name': 'Low (Recommended for Feature Phones)',
        'video_bitrate': '200k',
        'audio_bitrate': '192k',
        'audio_sample_rate': '44100',
        'fps': '12',
        'description': '~3.2 MB per 5 min'
    },
    'medium': {
        'name': 'Medium (Better Quality)',
        'video_bitrate': '300k',
        'audio_bitrate': '256k',
        'audio_sample_rate': '44100',
        'fps': '15',
        'description': '~4.6 MB per 5 min'
    },
    'high': {
        'name': 'High (Best Quality)',
        'video_bitrate': '400k',
        'audio_bitrate': '320k',
        'audio_sample_rate': '48000',
        'fps': '18',
        'description': '~6 MB per 5 min'
    }
}

# Detect FFmpeg path (for Render free tier compatibility)
def download_ffmpeg_binary():
    """Auto-download FFmpeg if not found - helps discover Render's actual paths"""
    try:
        logger.info("FFmpeg not found in expected locations. Attempting auto-download...")

        # Try downloading to /tmp first (always writable)
        download_dir = '/tmp/bin'
        os.makedirs(download_dir, exist_ok=True)

        ffmpeg_url = 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz'
        download_path = os.path.join(download_dir, 'ffmpeg-static.tar.xz')

        logger.info(f"Downloading FFmpeg from {ffmpeg_url}...")
        result = subprocess.run(['wget', '-O', download_path, ffmpeg_url], 
                              capture_output=True, timeout=120)

        if result.returncode == 0 and os.path.exists(download_path):
            logger.info(f"Download successful! Extracting to {download_dir}...")
            subprocess.run(['tar', '-xJf', download_path, '-C', download_dir, '--strip-components=1'],
                         timeout=60)
            os.remove(download_path)

            ffmpeg_binary = os.path.join(download_dir, 'ffmpeg')
            if os.path.exists(ffmpeg_binary):
                os.chmod(ffmpeg_binary, 0o755)
                logger.info(f"✓ FFmpeg auto-downloaded successfully to: {ffmpeg_binary}")
                logger.info(f"✓ DISCOVERED PATH: {ffmpeg_binary} (use this in your config!)")
                return ffmpeg_binary

        logger.warning("Auto-download failed, trying system package manager...")
        # Try apt-get as last resort (works on some systems)
        subprocess.run(['apt-get', 'update'], capture_output=True, timeout=30)
        subprocess.run(['apt-get', 'install', '-y', 'ffmpeg'], capture_output=True, timeout=120)

        return 'ffmpeg'  # Hope it's now in PATH

    except Exception as e:
        logger.error(f"Auto-download failed: {e}")
        return 'ffmpeg'  # Fallback to system PATH

def get_ffmpeg_path():
    """Find FFmpeg binary - checks multiple locations, auto-downloads if needed"""
    possible_paths = [
        'bin/ffmpeg',  # Pre-placed binary in repository
        '/opt/bin/ffmpeg',  # Static binary location (from build.sh)
        '/tmp/bin/ffmpeg',  # Auto-downloaded location
        'ffmpeg',  # System PATH
        '/usr/bin/ffmpeg',  # Standard location
        '/usr/local/bin/ffmpeg',  # Alternative location
    ]

    # First pass: try all known locations
    for path in possible_paths:
        try:
            result = subprocess.run([path, '-version'], capture_output=True, timeout=5)
            if result.returncode == 0:
                logger.info(f"✓ FFmpeg found at: {path}")
                return path
        except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
            continue

    # Not found - try auto-download
    logger.warning("FFmpeg not found in any expected location - attempting auto-download...")
    downloaded_path = download_ffmpeg_binary()

    # Verify the downloaded binary works
    try:
        result = subprocess.run([downloaded_path, '-version'], capture_output=True, timeout=5)
        if result.returncode == 0:
            logger.info(f"✓ Auto-downloaded FFmpeg working at: {downloaded_path}")
            return downloaded_path
    except:
        pass

    logger.error("⚠️ FFmpeg not available - conversions may fail!")
    return 'ffmpeg'  # Last resort fallback

def get_ffprobe_path():
    """Find FFprobe binary - checks multiple locations, uses ffmpeg if needed"""
    possible_paths = [
        'bin/ffprobe',  # Pre-placed binary in repository
        '/opt/bin/ffprobe',  # Static binary location (from build.sh)
        '/tmp/bin/ffprobe',  # Auto-downloaded location
        'ffprobe',  # System PATH
        '/usr/bin/ffprobe',  # Standard location
        '/usr/local/bin/ffprobe',  # Alternative location
    ]

    for path in possible_paths:
        try:
            result = subprocess.run([path, '-version'], capture_output=True, timeout=5)
            if result.returncode == 0:
                logger.info(f"✓ FFprobe found at: {path}")
                return path
        except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
            continue

    logger.info("FFprobe not found (not critical - FFmpeg can handle duration detection)")
    return 'ffprobe'  # Fallback to system PATH

FFMPEG_PATH = get_ffmpeg_path()
FFPROBE_PATH = get_ffprobe_path()
logger.info(f"Using FFmpeg: {FFMPEG_PATH}")
logger.info(f"Using FFprobe: {FFPROBE_PATH}")

status_lock = threading.Lock()

def get_status():
    with status_lock:
        if os.path.exists(STATUS_FILE):
            try:
                with open(STATUS_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

def save_status(status_data):
    with status_lock:
        temp_file = STATUS_FILE + '.tmp'
        with open(temp_file, 'w') as f:
            json.dump(status_data, f)
        os.replace(temp_file, STATUS_FILE)

def update_status(file_id, updates):
    with status_lock:
        if os.path.exists(STATUS_FILE):
            try:
                with open(STATUS_FILE, 'r') as f:
                    status = json.load(f)
            except json.JSONDecodeError:
                status = {}
        else:
            status = {}

        if file_id not in status:
            status[file_id] = {}
        status[file_id].update(updates)

        temp_file = STATUS_FILE + '.tmp'
        with open(temp_file, 'w') as f:
            json.dump(status, f)
        os.replace(temp_file, STATUS_FILE)

def generate_file_id(url):
    timestamp = str(int(time.time() * 1000))
    combined = f"{url}_{timestamp}"
    return hashlib.md5(combined.encode()).hexdigest()[:16]

def check_disk_space():
    """Check available disk space on /tmp (Render has 2GB ephemeral storage limit)"""
    try:
        import shutil
        total, used, free = shutil.disk_usage('/tmp')
        free_mb = free / (1024 * 1024)
        used_mb = used / (1024 * 1024)
        total_mb = total / (1024 * 1024)

        logger.info(f"Disk space: {free_mb:.0f}MB free / {total_mb:.0f}MB total ({used_mb:.0f}MB used)")

        if free_mb < DISK_SPACE_THRESHOLD_MB:
            logger.warning(f"⚠️ Low disk space: {free_mb:.0f}MB free (threshold: {DISK_SPACE_THRESHOLD_MB}MB)")
            return False, free_mb
        return True, free_mb
    except Exception as e:
        logger.error(f"Error checking disk space: {e}")
        return True, 0  # Continue anyway

def clean_tmp_immediately():
    """Emergency cleanup of /tmp when space is low"""
    try:
        import glob

        # Clean downloads folder
        files = glob.glob(os.path.join(DOWNLOAD_FOLDER, '*'))
        deleted = 0
        freed_mb = 0

        for filepath in files:
            try:
                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                os.remove(filepath)
                deleted += 1
                freed_mb += size_mb
            except:
                pass

        logger.info(f"Emergency cleanup: deleted {deleted} files, freed {freed_mb:.1f}MB")
        return freed_mb
    except Exception as e:
        logger.error(f"Emergency cleanup failed: {e}")
        return 0

def get_video_duration(file_path):
    try:
        cmd = [
            FFPROBE_PATH,
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return float(result.stdout.strip())
        return 0
    except:
        return 0

def has_cookies():
    return os.path.exists(COOKIES_FILE) and os.path.getsize(COOKIES_FILE) > 0

def validate_cookies():
    if not has_cookies():
        return False, "No cookies file found"

    try:
        with open(COOKIES_FILE, 'r') as f:
            content = f.read()

            if 'youtube.com' not in content.lower():
                return False, "Cookie file does not contain YouTube cookies"

            if len(content.strip()) < 50:
                return False, "Cookie file appears to be empty or invalid"

            lines = content.strip().split('\n')
            has_youtube_cookies = False

            for line in lines:
                if line.startswith('#') or not line.strip():
                    continue

                parts = line.split('\t')
                if len(parts) >= 7:
                    domain = parts[0]
                    cookie_name = parts[5]

                    if 'youtube.com' in domain.lower():
                        has_youtube_cookies = True

                        if cookie_name in ['LOGIN_INFO', '__Secure-1PSID', '__Secure-3PSID']:
                            return True, "Valid YouTube cookies with authentication token found"

            if has_youtube_cookies:
                return False, "YouTube cookies found but missing LOGIN_INFO or session tokens. Please export cookies while logged into YouTube, or from a fresh youtube.com visit."
            else:
                return False, "No YouTube cookies detected in file"

    except Exception as e:
        return False, f"Error reading cookies: {str(e)}"

def download_and_convert(url, file_id, output_format='3gp', quality='auto'):
    # Check disk space BEFORE starting download
    if ENABLE_DISK_SPACE_MONITORING:
        has_space, free_mb = check_disk_space()
        if not has_space:
            logger.warning(f"Low disk space ({free_mb:.0f}MB), attempting cleanup...")
            freed_mb = clean_tmp_immediately()
            has_space, free_mb = check_disk_space()
            if not has_space:
                update_status(file_id, {
                    'status': 'failed',
                    'progress': f'Server storage full ({free_mb:.0f}MB free). Please try again in a few minutes after cleanup.'
                })
                return

    file_extension = 'mp3' if output_format == 'mp3' else '3gp'
    format_name = 'MP3 audio' if output_format == 'mp3' else '3GP video'

    # Auto-select quality if not specified
    if quality == 'auto':
        if output_format == 'mp3':
            quality = 'medium'  # 128kbps default for MP3
        else:
            quality = 'low'  # Low quality default for 3GP (feature phone optimized)

    # Validate quality preset
    if output_format == 'mp3':
        if quality not in MP3_QUALITY_PRESETS:
            quality = 'medium'
        quality_preset = MP3_QUALITY_PRESETS[quality]
    else:
        if quality not in VIDEO_QUALITY_PRESETS:
            quality = 'low'
        quality_preset = VIDEO_QUALITY_PRESETS[quality]

    update_status(file_id, {
        'status': 'downloading',
        'progress': f'Downloading from YouTube for {format_name} conversion ({quality_preset["name"]})... (this may take several minutes for long videos)',
        'url': url,
        'timestamp': datetime.now().isoformat()
    })

    output_path = os.path.join(DOWNLOAD_FOLDER, f'{file_id}.{file_extension}')
    temp_video = os.path.join(DOWNLOAD_FOLDER, f'{file_id}_temp.mp4')

    try:
        # Base yt-dlp options (using Python API instead of subprocess)
        # Use flexible format selection to avoid "Requested format not available" errors
        # Priority: smaller files for feature phones, but fallback to any available format
        if output_format == 'mp3':
            # For audio: get best audio, any format
            format_str = 'bestaudio/best'
        else:
            # For video: prefer smaller files but accept anything available
            # Try: low quality video+audio, then medium, then any available
            format_str = 'worst[height<=480]+worstaudio/bestvideo[height<=480]+bestaudio/best[height<=480]/worst+worstaudio/best'

        base_opts = {
            'format': format_str,
            'merge_output_format': 'mp4',
            'outtmpl': temp_video,
            'max_filesize': MAX_FILESIZE,
            'nocheckcertificate': True,
            'retries': 15,
            'retry_sleep': 3,
            'fragment_retries': 15,
            'sleep_requests': 1,
            'concurrent_fragment_downloads': 1,
            'ignoreerrors': False,
            'extractor_retries': 10,
            'socket_timeout': 30,
            'http_chunk_size': 10485760,  # 10MB
            'quiet': False,
            'no_warnings': False,
            'logger': logger,
        }

        # YouTube IP block bypass: Use IPv6 if enabled (less blocked by YouTube)
        if USE_IPV6:
            base_opts['force_ipv6'] = True
            logger.info(f"Using IPv6 for download (IP block bypass)")
        else:
            base_opts['force_ipv4'] = True

        # Add proxy if configured (bypass cloud IP blocks)
        if PROXY_URL:
            base_opts['proxy'] = PROXY_URL
            logger.info(f"Using proxy for download (IP block bypass)")

        # Add rate limiting if configured (avoid 429 errors)
        if RATE_LIMIT_BYTES > 0:
            base_opts['ratelimit'] = RATE_LIMIT_BYTES
            logger.info(f"Rate limiting enabled: {RATE_LIMIT_BYTES} bytes/sec ({RATE_LIMIT_BYTES/1024:.0f} KB/s)")

        # Download strategies - Updated for YouTube's new restrictions (Nov 2025)
        # Multiple clients to bypass bot detection - ordered by reliability
        strategies = [
            {
                'name': 'iOS Client (Most Reliable)',
                'opts': {
                    'extractor_args': {'youtube': {
                        'player_client': ['ios'],
                        'player_skip': ['configs', 'webpage']
                    }},
                    'http_headers': {
                        'User-Agent': 'com.google.ios.youtube/19.45.4 (iPhone16,2; U; CPU iOS 18_1_1 like Mac OS X;)',
                        'X-YouTube-Client-Name': '5',
                        'X-YouTube-Client-Version': '19.45.4'
                    }
                }
            },
            {
                'name': 'Android TV (Highly Reliable)',
                'opts': {
                    'extractor_args': {'youtube': {
                        'player_client': ['android_tv'],
                        'player_skip': ['configs', 'webpage']
                    }},
                    'http_headers': {
                        'User-Agent': 'com.google.android.youtube.tv/2.41.04 (Linux; U; Android 13; en_US)',
                        'X-YouTube-Client-Name': '85',
                        'X-YouTube-Client-Version': '2.41.04'
                    }
                }
            },
            {
                'name': 'Android Client (Best Compatibility)',
                'opts': {
                    'extractor_args': {'youtube': {
                        'player_client': ['android'],
                        'player_skip': ['configs', 'webpage']
                    }},
                    'http_headers': {
                        'User-Agent': 'com.google.android.youtube/19.45.38 (Linux; U; Android 14; en_US)',
                        'X-YouTube-Client-Name': '3',
                        'X-YouTube-Client-Version': '19.45.38'
                    }
                }
            },
            {
                'name': 'Android Music (Less Restricted)',
                'opts': {
                    'extractor_args': {'youtube': {
                        'player_client': ['android_music'],
                        'player_skip': ['configs']
                    }},
                    'http_headers': {
                        'User-Agent': 'com.google.android.apps.youtube.music/7.31.51 (Linux; U; Android 14) gzip',
                        'X-YouTube-Client-Name': '21',
                        'X-YouTube-Client-Version': '7.31.51'
                    }
                }
            },
            {
                'name': 'Android Creator (Alternative)',
                'opts': {
                    'extractor_args': {'youtube': {
                        'player_client': ['android_creator'],
                        'player_skip': ['configs']
                    }},
                    'http_headers': {
                        'User-Agent': 'com.google.android.apps.youtube.creator/24.43.101 (Linux; U; Android 14)',
                        'X-YouTube-Client-Name': '14',
                        'X-YouTube-Client-Version': '24.43.101'
                    }
                }
            },
            {
                'name': 'Mobile Web (Fallback)',
                'opts': {
                    'extractor_args': {'youtube': {
                        'player_client': ['mweb'],
                        'player_skip': ['configs']
                    }},
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9'
                    }
                }
            },
            {
                'name': 'TV Embedded (Last Resort)',
                'opts': {
                    'extractor_args': {'youtube': {
                        'player_client': ['tv_embedded'],
                        'player_skip': ['webpage']
                    }},
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (PlayStation; PlayStation 5/9.00) AppleWebKit/605.1.15 Chrome/130.0.0.0 Safari/605.1.15'
                    }
                }
            }
        ]

        # Add cookies if available
        if has_cookies():
            base_opts['cookiefile'] = COOKIES_FILE

        last_error = None
        download_success = False

        for i, strategy in enumerate(strategies):
            try:
                if i > 0:
                    update_status(file_id, {
                        'status': 'downloading',
                        'progress': f'Retrying with {strategy["name"]} client... (attempt {i+1}/{len(strategies)})'
                    })
                    time.sleep(3 * i)

                # Merge strategy options with base options
                ydl_opts = {**base_opts, **strategy['opts']}

                logger.info(f"Attempting download with {strategy['name']} strategy for {file_id}")

                # Use yt-dlp Python API instead of subprocess
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(url, download=True)

                if os.path.exists(temp_video) and os.path.getsize(temp_video) > 0:
                    logger.info(f"Download successful with {strategy['name']} for {file_id}")
                    download_success = True
                    break
                else:
                    logger.warning(f"{strategy['name']} strategy failed - file not created or empty")

            except yt_dlp.utils.DownloadError as e:
                last_error = str(e)
                error_lower = last_error.lower()

                # Detect IP blocking specifically
                if '403' in last_error or 'forbidden' in error_lower or 'bot' in error_lower:
                    logger.warning(f"⚠️ Possible IP block detected with {strategy['name']}: {last_error[:200]}")
                    # Add extra delay when IP blocked
                    time.sleep(5)
                else:
                    logger.error(f"{strategy['name']} download error for {file_id}: {last_error}")
                continue
            except Exception as e:
                last_error = str(e)
                logger.error(f"{strategy['name']} unexpected error for {file_id}: {last_error}")
                continue

        if not download_success:
            error_msg = last_error if last_error else "All download strategies failed"
            error_lower = error_msg.lower()

            # Check if cookies would help
            cookies_help = " → Try uploading YouTube cookies from /cookies page to fix this." if not has_cookies() else ""

            # Enhanced error detection with cookie suggestions
            if '403' in error_msg or 'forbidden' in error_lower:
                raise Exception(f"⚠️ YouTube IP BLOCK detected! YouTube is blocking downloads from this server.{cookies_help if cookies_help else ' Try using fresh cookies from /cookies page.'}")

            if 'po token' in error_lower or 'po_token' in error_lower:
                raise Exception(f"⚠️ YouTube now requires PO tokens for some videos. Upload YouTube cookies from /cookies page to bypass this restriction.")

            if 'failed to extract' in error_lower or 'failed to parse' in error_lower:
                raise Exception(f"⚠️ YouTube blocked the video extraction. This is a bot detection measure.{cookies_help}")

            if 'video player configuration error' in error_lower or 'error 153' in error_lower:
                raise Exception(f"⚠️ YouTube player error (Error 153). This video has restricted playback.{cookies_help}")

            if 'bot' in error_lower and ('sign in' in error_lower or 'confirm' in error_lower):
                raise Exception(f"⚠️ YouTube bot detection triggered!{cookies_help if cookies_help else ' Try fresh cookies from /cookies page.'}")

            if 'duration' in error_lower:
                raise Exception(f"Video exceeds {MAX_VIDEO_DURATION/3600:.0f}-hour limit")
            if 'filesize' in error_msg.lower() or 'too large' in error_msg.lower():
                raise Exception(f"Video file too large (limit: 2GB)")
            if '429' in error_msg or 'too many requests' in error_msg.lower():
                raise Exception(f"YouTube rate limit reached. Wait 5-10 minutes and try again.{cookies_help}")
            if 'age' in error_msg.lower() and 'restricted' in error_msg.lower():
                raise Exception(f"Video is age-restricted. Upload cookies from /cookies page to access it.")
            if 'private' in error_msg.lower() or 'members-only' in error_msg.lower():
                raise Exception("Video is private or members-only. Cannot download.")
            if 'geo' in error_msg.lower() or 'not available in your country' in error_msg.lower():
                raise Exception("Video is geo-restricted and not available in your region.")
            if 'copyright' in error_msg.lower() or 'removed' in error_msg.lower():
                raise Exception("Video removed due to copyright claim or deletion.")
            if 'live' in error_msg.lower() and 'stream' in error_msg.lower():
                raise Exception("Cannot download live streams. Try again after the stream ends.")
            if 'sign in' in error_msg.lower() or 'login' in error_msg.lower():
                if has_cookies():
                    raise Exception("YouTube authentication failed. Upload fresh cookies from /cookies page.")
                else:
                    raise Exception(f"YouTube requires sign-in verification.{cookies_help}")

            raise Exception(f"Download failed: {error_msg[:200]}{cookies_help}")

        if not os.path.exists(temp_video):
            raise Exception("Download failed: Video file not created")

        duration = get_video_duration(temp_video)
        if duration > MAX_VIDEO_DURATION:
            os.remove(temp_video)
            raise Exception(f"Video is {duration/3600:.1f} hours long. Maximum allowed is {MAX_VIDEO_DURATION/3600:.0f} hours.")

        file_size = os.path.getsize(temp_video)
        file_size_mb = file_size / (1024 * 1024)

        # Check disk space AGAIN before conversion (video might be large)
        if ENABLE_DISK_SPACE_MONITORING:
            has_space, free_mb = check_disk_space()
            if free_mb < (file_size_mb * 1.5):  # Need ~1.5x video size for conversion
                logger.warning(f"Insufficient space for conversion: {free_mb:.0f}MB free, need ~{file_size_mb*1.5:.0f}MB")
                os.remove(temp_video)
                raise Exception(f"Insufficient disk space for conversion. Downloaded video is {file_size_mb:.1f}MB but only {free_mb:.0f}MB free. Try a shorter video.")

        est_time = max(1, int(duration / 60))

        if output_format == 'mp3':
            update_status(file_id, {
                'status': 'converting',
                'progress': f'Converting to MP3 audio ({quality_preset["name"]})... Duration: {duration/60:.1f} minutes, Size: {file_size_mb:.1f} MB. Estimated time: {est_time} minute(s).'
            })

            # MP3 conversion with quality preset
            convert_cmd = [
                FFMPEG_PATH,
                '-i', temp_video,
                '-vn',  # No video
                '-acodec', 'libmp3lame',
                '-ar', quality_preset['sample_rate'],  # Sample rate from preset
                '-b:a', quality_preset['bitrate'],  # Bitrate from preset
                '-ac', '2' if quality in ['veryhigh', 'extreme'] else '1',  # Stereo for high quality, mono otherwise
                '-q:a', quality_preset['vbr_quality'],  # VBR quality from preset
                '-compression_level', '2',  # Faster encoding for web server
                '-threads', '1',
                '-y',
                output_path
            ]
        else:
            update_status(file_id, {
                'status': 'converting',
                'progress': f'Converting to 3GP video ({quality_preset["name"]})... Duration: {duration/60:.1f} minutes, Size: {file_size_mb:.1f} MB. Estimated time: {est_time}-{est_time*2} minutes.'
            })

            # 3GP video conversion with quality preset and compression
            video_bitrate_num = int(quality_preset['video_bitrate'].replace('k', ''))
            maxrate = f"{int(video_bitrate_num * 1.25)}k"  # 25% higher maxrate for better quality
            bufsize = f"{int(video_bitrate_num * 2)}k"  # Buffer size for smooth streaming

            convert_cmd = [
                FFMPEG_PATH,
                '-i', temp_video,
                '-vf', 'scale=176:144:force_original_aspect_ratio=decrease,pad=176:144:(ow-iw)/2:(oh-ih)/2,setsar=1',
                '-vcodec', 'mpeg4',
                '-r', quality_preset['fps'],  # FPS from preset
                '-b:v', quality_preset['video_bitrate'],  # Video bitrate from preset
                '-maxrate', maxrate,  # Dynamic maxrate based on bitrate
                '-bufsize', bufsize,  # Dynamic buffer size
                '-qmin', '2',  # Minimum quantizer for better quality
                '-qmax', '31',  # Maximum quantizer
                '-mbd', 'rd',  # Rate distortion optimization for better compression
                '-acodec', 'aac',
                '-ar', quality_preset['audio_sample_rate'],  # Audio sample rate from preset
                '-b:a', quality_preset['audio_bitrate'],  # Audio bitrate from preset
                '-ac', '1',
                '-threads', '1',
                '-y',
                output_path
            ]

        dynamic_timeout = max(CONVERSION_TIMEOUT, int(duration * 2))
        result = subprocess.run(convert_cmd, capture_output=True, text=True, timeout=dynamic_timeout)

        if result.returncode != 0:
            error_msg = result.stderr[:300] if result.stderr else "Unknown FFmpeg error"
            logger.error(f"FFmpeg conversion failed for {file_id}: {error_msg}")

            # Retry once with simpler encoding if first attempt fails
            logger.info(f"Retrying conversion with simpler settings for {file_id}")

            if output_format == 'mp3':
                simple_cmd = [
                    FFMPEG_PATH,
                    '-i', temp_video,
                    '-vn',
                    '-acodec', 'libmp3lame',
                    '-ar', '16000',
                    '-b:a', '32k',
                    '-ac', '1',
                    '-threads', '1',
                    '-y',
                    output_path
                ]
            else:
                simple_cmd = [
                    FFMPEG_PATH,
                    '-i', temp_video,
                    '-s', '176x144',
                    '-vcodec', 'mpeg4',
                    '-r', '12',
                    '-b:v', '150k',
                    '-acodec', 'aac',
                    '-ar', '16000',
                    '-b:a', '24k',
                    '-ac', '1',
                    '-threads', '1',
                    '-y',
                    output_path
                ]

            retry_result = subprocess.run(simple_cmd, capture_output=True, text=True, timeout=dynamic_timeout)

            if retry_result.returncode != 0:
                # Clean up temp file before raising exception
                if os.path.exists(temp_video):
                    try:
                        os.remove(temp_video)
                    except:
                        pass
                raise Exception(f"Conversion failed after retry: {error_msg}")

        # Clean up temp video after successful conversion
        if os.path.exists(temp_video):
            try:
                os.remove(temp_video)
            except:
                pass

        if not os.path.exists(output_path):
            raise Exception("Conversion failed: Output file not created")

        final_size = os.path.getsize(output_path)
        final_size_mb = final_size / (1024 * 1024)

        # Use correct filename extension based on format
        filename_with_ext = f'{file_id}.{file_extension}'

        update_status(file_id, {
            'status': 'completed',
            'progress': f'Conversion complete! Duration: {duration/60:.1f} min, File size: {final_size_mb:.2f} MB',
            'filename': filename_with_ext,
            'file_size': final_size,
            'duration': duration,
            'completed_at': datetime.now().isoformat()
        })

    except subprocess.TimeoutExpired:
        logger.error(f"Timeout processing {file_id}")
        update_status(file_id, {
            'status': 'failed',
            'progress': 'Error: Processing timeout. Video may be too long or server is busy. Try a shorter video.'
        })
        if os.path.exists(temp_video):
            try:
                os.remove(temp_video)
            except:
                pass
    except Exception as e:
        logger.error(f"Error processing {file_id}: {str(e)}")
        update_status(file_id, {
            'status': 'failed',
            'progress': f'Error: {str(e)}'
        })
        if os.path.exists(temp_video):
            try:
                os.remove(temp_video)
            except:
                pass

        # Cleanup output if partially created
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except:
                pass

def cleanup_old_files():
    while True:
        try:
            time.sleep(1800)

            cutoff_time = datetime.now() - timedelta(hours=FILE_RETENTION_HOURS)
            deleted_count = 0

            with status_lock:
                if os.path.exists(STATUS_FILE):
                    try:
                        with open(STATUS_FILE, 'r') as f:
                            status = json.load(f)
                    except json.JSONDecodeError:
                        status = {}
                else:
                    status = {}

                for file_id, data in list(status.items()):
                    try:
                        should_delete = False

                        if 'completed_at' in data:
                            completed_time = datetime.fromisoformat(data['completed_at'])
                            if completed_time < cutoff_time:
                                should_delete = True
                        elif 'timestamp' in data:
                            start_time = datetime.fromisoformat(data['timestamp'])
                            if start_time < cutoff_time:
                                if data.get('status') in ['failed', 'unknown', 'downloading', 'converting']:
                                    should_delete = True

                        if should_delete:
                            # Delete both 3gp and mp3 files if they exist
                            file_path_3gp = os.path.join(DOWNLOAD_FOLDER, f'{file_id}.3gp')
                            file_path_mp3 = os.path.join(DOWNLOAD_FOLDER, f'{file_id}.mp3')
                            if os.path.exists(file_path_3gp):
                                os.remove(file_path_3gp)
                                deleted_count += 1
                            if os.path.exists(file_path_mp3):
                                os.remove(file_path_mp3)
                                deleted_count += 1
                            del status[file_id]
                    except Exception as e:
                        print(f"Error cleaning file {file_id}: {e}")
                        continue

                temp_file = STATUS_FILE + '.tmp'
                with open(temp_file, 'w') as f:
                    json.dump(status, f)
                os.replace(temp_file, STATUS_FILE)

            for filename in os.listdir(DOWNLOAD_FOLDER):
                try:
                    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
                    if os.path.isfile(file_path):
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if file_time < cutoff_time:
                            os.remove(file_path)
                            deleted_count += 1
                except Exception as e:
                    print(f"Error removing orphan file {filename}: {e}")
                    continue

            if deleted_count > 0:
                print(f"Cleanup completed: Deleted {deleted_count} old files")

        except Exception as e:
            print(f"Cleanup error: {e}")

cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

def signal_handler(sig, frame):
    print(f'\nReceived signal {sig}. Gracefully shutting down...')
    print('Cleaning up temporary files...')
    try:
        for filename in os.listdir(DOWNLOAD_FOLDER):
            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
            if os.path.isfile(file_path) and filename.endswith('_temp.mp4'):
                try:
                    os.remove(file_path)
                    print(f'Cleaned up temp file: {filename}')
                except:
                    pass
    except:
        pass
    print('Shutdown complete.')
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

@app.route('/')
def index():
    max_hours = MAX_VIDEO_DURATION / 3600
    cookies_status = has_cookies()
    return render_template('index.html', 
                         max_hours=max_hours, 
                         has_cookies=cookies_status,
                         mp3_presets=MP3_QUALITY_PRESETS,
                         video_presets=VIDEO_QUALITY_PRESETS)

@app.route('/mp3')
def mp3_converter():
    max_hours = MAX_VIDEO_DURATION / 3600
    cookies_status = has_cookies()
    return render_template('mp3.html', 
                         max_hours=max_hours, 
                         has_cookies=cookies_status,
                         mp3_presets=MP3_QUALITY_PRESETS)

@app.route('/3gp')
def gp3_converter():
    max_hours = MAX_VIDEO_DURATION / 3600
    cookies_status = has_cookies()
    return render_template('3gp.html', 
                         max_hours=max_hours, 
                         has_cookies=cookies_status,
                         video_presets=VIDEO_QUALITY_PRESETS)

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/health')
def health():
    return {'status': 'ok', 'service': 'youtube-3gp-converter'}, 200

@app.route('/convert', methods=['POST'])
def convert():
    url = request.form.get('url', '').strip()
    output_format = request.form.get('format', '3gp').strip()
    
    # Get quality based on selected format
    if output_format == 'mp3':
        quality = request.form.get('mp3_quality', 'auto').strip()
    else:
        quality = request.form.get('video_quality', 'auto').strip()

    if not url:
        flash('Please enter a YouTube URL')
        return redirect(url_for('index'))

    if 'youtube.com' not in url and 'youtu.be' not in url:
        flash('Please enter a valid YouTube URL')
        return redirect(url_for('index'))

    if output_format not in ['3gp', 'mp3']:
        output_format = '3gp'

    file_id = generate_file_id(url)

    thread = threading.Thread(target=download_and_convert, args=(url, file_id, output_format, quality))
    thread.daemon = True
    thread.start()

    return redirect(url_for('status', file_id=file_id))

@app.route('/status/<file_id>')
def status(file_id):
    status_data = get_status()
    file_status = status_data.get(file_id, {'status': 'unknown', 'progress': 'File not found'})
    
    # Get file info if file exists
    file_info = None
    if file_status.get('status') == 'completed':
        file_path_3gp = os.path.join(DOWNLOAD_FOLDER, f'{file_id}.3gp')
        file_path_mp3 = os.path.join(DOWNLOAD_FOLDER, f'{file_id}.mp3')
        
        if os.path.exists(file_path_3gp):
            file_info = get_file_info(file_path_3gp)
        elif os.path.exists(file_path_mp3):
            file_info = get_file_info(file_path_mp3)
    
    return render_template('status.html', file_id=file_id, file_status=file_status, file_info=file_info)

@app.route('/download/<file_id>')
def download(file_id):
    # Check for both 3gp and mp3 files
    file_path_3gp = os.path.join(DOWNLOAD_FOLDER, f'{file_id}.3gp')
    file_path_mp3 = os.path.join(DOWNLOAD_FOLDER, f'{file_id}.mp3')

    if os.path.exists(file_path_3gp):
        return send_file(file_path_3gp, as_attachment=True, download_name=f'video_{file_id}.3gp')
    elif os.path.exists(file_path_mp3):
        return send_file(file_path_mp3, as_attachment=True, download_name=f'audio_{file_id}.mp3')
    else:
        flash('File not found or has been deleted')
        return redirect(url_for('index'))

def get_file_info(file_path):
    """Get file information: size, duration (for video/audio), format"""
    info = {
        'size_bytes': 0,
        'size_mb': 0,
        'size_human': '0 MB',
        'duration_seconds': 0,
        'duration_human': 'Unknown',
        'format': os.path.splitext(file_path)[1].replace('.', '').upper()
    }
    
    if not os.path.exists(file_path):
        return info
    
    # Get file size
    size_bytes = os.path.getsize(file_path)
    info['size_bytes'] = size_bytes
    info['size_mb'] = size_bytes / (1024 * 1024)
    
    # Human readable size
    if size_bytes >= 1024 * 1024:
        info['size_human'] = f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        info['size_human'] = f"{size_bytes / 1024:.2f} KB"
    
    # Get duration using ffprobe (for video/audio files)
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.3gp', '.mp3', '.mp4', '.avi', '.mkv', '.flv']:
        try:
            ffprobe_cmd = [
                get_ffprobe_path(),
                '-v', 'quiet',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                file_path
            ]
            result = subprocess.run(ffprobe_cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                duration_seconds = float(result.stdout.strip())
                info['duration_seconds'] = int(duration_seconds)
                
                # Human readable duration
                hours = int(duration_seconds // 3600)
                minutes = int((duration_seconds % 3600) // 60)
                seconds = int(duration_seconds % 60)
                
                if hours > 0:
                    info['duration_human'] = f"{hours}h {minutes}m {seconds}s"
                elif minutes > 0:
                    info['duration_human'] = f"{minutes}m {seconds}s"
                else:
                    info['duration_human'] = f"{seconds}s"
        except Exception as e:
            logger.warning(f"Could not get duration for {file_path}: {str(e)}")
    
    return info

def split_file_by_parts(file_path, num_parts, file_id):
    """Split file into specified number of parts"""
    if not os.path.exists(file_path):
        return None
    
    file_size = os.path.getsize(file_path)
    
    # Validate: prevent zero-byte parts
    if num_parts > file_size:
        logger.warning(f"num_parts ({num_parts}) exceeds file size ({file_size} bytes), capping to file size")
        num_parts = max(2, file_size)  # At least 2 parts, at most 1 byte per part
    
    part_size = file_size // num_parts
    
    # Additional safety: ensure part_size is at least 1 byte
    if part_size < 1:
        part_size = 1
        num_parts = file_size
    
    ext = os.path.splitext(file_path)[1]
    parts = []
    
    with open(file_path, 'rb') as f:
        for i in range(num_parts):
            part_filename = f"{file_id}_part{i+1}{ext}"
            part_path = os.path.join(DOWNLOAD_FOLDER, part_filename)
            
            # Read the chunk for this part
            if i == num_parts - 1:
                # Last part gets all remaining bytes
                chunk = f.read()
            else:
                chunk = f.read(part_size)
            
            # Skip empty chunks
            if not chunk:
                break
            
            with open(part_path, 'wb') as part_file:
                part_file.write(chunk)
            
            parts.append({
                'filename': part_filename,
                'path': part_path,
                'size': len(chunk),
                'part_num': i + 1
            })
    
    # Verify all parts are non-zero
    valid_parts = []
    for part in parts:
        if part['size'] > 0:
            valid_parts.append(part)
        else:
            # Clean up zero-byte file
            if os.path.exists(part['path']):
                os.remove(part['path'])
            logger.warning(f"Removed zero-byte part: {part['filename']}")
    
    return valid_parts if len(valid_parts) > 0 else None

def split_file_by_size(file_path, size_mb, file_id):
    """Split file into parts of specified size (in MB)"""
    if not os.path.exists(file_path):
        return None
    
    file_size = os.path.getsize(file_path)
    part_size = int(size_mb * 1024 * 1024)  # Convert MB to bytes
    
    ext = os.path.splitext(file_path)[1]
    parts = []
    part_num = 1
    
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(part_size)
            if not chunk:
                break
            
            part_filename = f"{file_id}_part{part_num}{ext}"
            part_path = os.path.join(DOWNLOAD_FOLDER, part_filename)
            
            with open(part_path, 'wb') as part_file:
                part_file.write(chunk)
            
            parts.append({
                'filename': part_filename,
                'path': part_path,
                'size': len(chunk),
                'part_num': part_num
            })
            
            part_num += 1
    
    return parts

def split_video_by_duration(file_path, duration_seconds, file_id):
    """Split video into parts of specified duration (in seconds) using ffmpeg"""
    if not os.path.exists(file_path):
        return None
    
    ext = os.path.splitext(file_path)[1]
    parts = []
    part_num = 1
    start_time = 0
    
    # Get total duration
    info = get_file_info(file_path)
    total_duration = info['duration_seconds']
    
    if total_duration == 0:
        return None
    
    ffmpeg_path = get_ffmpeg_path()
    
    while start_time < total_duration:
        part_filename = f"{file_id}_part{part_num}{ext}"
        part_path = os.path.join(DOWNLOAD_FOLDER, part_filename)
        
        # Use ffmpeg to extract segment
        ffmpeg_cmd = [
            ffmpeg_path,
            '-i', file_path,
            '-ss', str(start_time),
            '-t', str(duration_seconds),
            '-c', 'copy',  # Copy without re-encoding for speed
            '-y',  # Overwrite output file
            part_path
        ]
        
        try:
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0 and os.path.exists(part_path):
                parts.append({
                    'filename': part_filename,
                    'path': part_path,
                    'size': os.path.getsize(part_path),
                    'part_num': part_num
                })
            else:
                logger.error(f"Failed to create part {part_num}: {result.stderr}")
                break
        except Exception as e:
            logger.error(f"Error splitting video part {part_num}: {str(e)}")
            break
        
        start_time += duration_seconds
        part_num += 1
    
    return parts if len(parts) > 0 else None

@app.route('/split/<file_id>', methods=['POST'])
def split_file(file_id):
    """Handle file splitting requests"""
    # Find the file
    file_path_3gp = os.path.join(DOWNLOAD_FOLDER, f'{file_id}.3gp')
    file_path_mp3 = os.path.join(DOWNLOAD_FOLDER, f'{file_id}.mp3')
    
    file_path = None
    if os.path.exists(file_path_3gp):
        file_path = file_path_3gp
    elif os.path.exists(file_path_mp3):
        file_path = file_path_mp3
    else:
        flash('File not found or has been deleted')
        return redirect(url_for('status', file_id=file_id))
    
    # Get split parameters
    split_mode = request.form.get('split_mode')  # 'parts', 'size', or 'duration'
    
    parts = None
    
    try:
        if split_mode == 'parts':
            num_parts = int(request.form.get('num_parts', 2))
            file_size = os.path.getsize(file_path)
            
            # Validate range
            if num_parts < 2 or num_parts > 100:
                flash('Number of parts must be between 2 and 100')
                return redirect(url_for('status', file_id=file_id))
            
            # Validate against file size
            if num_parts > file_size:
                max_parts = max(2, file_size)
                flash(f'File is too small to split into {num_parts} parts. Maximum {max_parts} parts for this file. Try splitting by size instead.')
                return redirect(url_for('status', file_id=file_id))
            
            parts = split_file_by_parts(file_path, num_parts, file_id)
            
        elif split_mode == 'size':
            size_mb = float(request.form.get('size_mb', 5))
            if size_mb < 0.1 or size_mb > 1000:
                flash('Part size must be between 0.1 MB and 1000 MB')
                return redirect(url_for('status', file_id=file_id))
            parts = split_file_by_size(file_path, size_mb, file_id)
            
        elif split_mode == 'duration':
            duration_minutes = float(request.form.get('duration_minutes', 2))
            duration_seconds = int(duration_minutes * 60)
            if duration_seconds < 10 or duration_seconds > 36000:
                flash('Part duration must be between 10 seconds and 10 hours')
                return redirect(url_for('status', file_id=file_id))
            parts = split_video_by_duration(file_path, duration_seconds, file_id)
        
        if parts:
            flash(f'File split into {len(parts)} parts successfully!')
            return redirect(url_for('split_downloads', file_id=file_id))
        else:
            flash('Failed to split file. Please try again.')
            return redirect(url_for('status', file_id=file_id))
            
    except ValueError as e:
        flash('Invalid input values. Please check your numbers.')
        return redirect(url_for('status', file_id=file_id))
    except Exception as e:
        logger.error(f"Error splitting file: {str(e)}")
        flash('An error occurred while splitting the file.')
        return redirect(url_for('status', file_id=file_id))

@app.route('/split_downloads/<file_id>')
def split_downloads(file_id):
    """Show download links for all split parts"""
    # Find all parts for this file_id
    parts = []
    for filename in os.listdir(DOWNLOAD_FOLDER):
        if filename.startswith(f'{file_id}_part'):
            part_path = os.path.join(DOWNLOAD_FOLDER, filename)
            # Extract part number
            import re
            match = re.search(r'part(\d+)', filename)
            part_num = int(match.group(1)) if match else 0
            
            parts.append({
                'filename': filename,
                'path': part_path,
                'size': os.path.getsize(part_path),
                'size_human': f"{os.path.getsize(part_path) / (1024 * 1024):.2f} MB",
                'part_num': part_num
            })
    
    # Sort by part number
    parts.sort(key=lambda x: x['part_num'])
    
    if not parts:
        flash('No split parts found. File may have expired.')
        return redirect(url_for('index'))
    
    return render_template('split_downloads.html', file_id=file_id, parts=parts)

@app.route('/download_part/<filename>')
def download_part(filename):
    """Download a specific split part"""
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename)
    else:
        flash('File part not found or has been deleted')
        return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    # Check if showing thumbnails (default: no, to save data on 2G)
    show_thumbnails = request.args.get('show_thumbnails', '0') == '1'
    
    # Get query from POST (new search) or GET (thumbnail toggle)
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
    else:
        query = request.args.get('query', '').strip()
    
    # If no query, show the search form
    if not query:
        if request.method == 'POST':
            flash('Please enter a search term')
        return render_template('search.html', results=None, query='', show_thumbnails=show_thumbnails)
    
    # Execute the search (query is guaranteed to exist here)
    try:
        # Use yt-dlp to search YouTube (no API key required)
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'force_generic_extractor': False,
            'socket_timeout': 30,  # Timeout for 2G networks
        }

        # Add cookies if available (helps with rate limiting and bot detection)
        if has_cookies():
            ydl_opts['cookiefile'] = COOKIES_FILE

        results = []
        search_results = None

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Search for up to 10 results with timeout protection
                search_results = ydl.extract_info(f"ytsearch10:{query}", download=False)
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            logger.error(f"Search DownloadError: {error_msg}")
            if 'timeout' in error_msg.lower():
                flash('Search timed out. Please check your connection and try again.')
            elif '429' in error_msg or 'too many requests' in error_msg.lower():
                flash('Too many search requests. Please wait a few minutes and try again.')
            elif '403' in error_msg or 'forbidden' in error_msg.lower():
                flash('YouTube blocked the search. Try uploading cookies from /cookies page.')
            else:
                flash('YouTube search error. Please try again.')
            return render_template('search.html', results=None, query=query, show_thumbnails=show_thumbnails)
        except Exception as e:
            logger.error(f"Search extraction error: {str(e)}")
            flash('Search failed. Please try again later.')
            return render_template('search.html', results=None, query=query, show_thumbnails=show_thumbnails)

        # Process search results
        if search_results and 'entries' in search_results:
            for entry in search_results['entries']:
                if entry and entry.get('id'):  # Ensure entry has an ID
                    duration = entry.get('duration', 0)
                    duration_str = f"{int(duration // 60)}:{int(duration % 60):02d}" if duration else "Unknown"

                    # Format upload date
                    upload_date = entry.get('upload_date', '')
                    upload_date_str = "Unknown"
                    if upload_date and len(upload_date) == 8:  # Format: YYYYMMDD
                        try:
                            upload_date_str = f"{upload_date[6:8]}/{upload_date[4:6]}/{upload_date[0:4]}"
                        except:
                            upload_date_str = "Unknown"

                    # Format view count
                    view_count = entry.get('view_count', 0)
                    if view_count:
                        if view_count >= 1000000:
                            view_str = f"{view_count/1000000:.1f}M views"
                        elif view_count >= 1000:
                            view_str = f"{view_count/1000:.1f}K views"
                        else:
                            view_str = f"{view_count} views"
                    else:
                        view_str = "Unknown views"

                    # FIXED: Proper URL construction for YouTube videos
                    # yt-dlp flat extraction may return partial URLs or video IDs
                    video_id = entry.get('id', '')
                    video_url = entry.get('url', '')

                    # Construct proper YouTube URL
                    if video_url and video_url.startswith('http'):
                        # Already a full URL
                        final_url = video_url
                    elif video_id:
                        # Construct from video ID
                        final_url = f"https://www.youtube.com/watch?v={video_id}"
                    else:
                        # Fallback: try to extract from URL field
                        logger.warning(f"Could not determine URL for search result: {entry.get('title', 'Unknown')}")
                        continue  # Skip this result

                    # Get thumbnail URL (small thumbnail for 2G networks)
                    thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/default.jpg"
                    
                    results.append({
                        'title': entry.get('title', 'Unknown'),
                        'url': final_url,
                        'duration': duration_str,
                        'duration_seconds': duration,
                        'upload_date': upload_date_str,
                        'channel': entry.get('channel', entry.get('uploader', 'Unknown')),
                        'views': view_str,
                        'thumbnail': thumbnail_url,
                    })

        # Validate we got results
        if not results:
            flash('No results found. Try different search terms.')
            return render_template('search.html', results=[], query=query, show_thumbnails=show_thumbnails)

        return render_template('search.html', results=results, query=query, show_thumbnails=show_thumbnails)

    except Exception as e:
        # Catch any unexpected errors not handled by inner try-except
        logger.error(f"Unexpected search error: {str(e)}")
        flash('An unexpected error occurred. Please try again.')
        return render_template('search.html', results=None, query=query, show_thumbnails=show_thumbnails)

@app.route('/cookies', methods=['GET', 'POST'])
def cookies_page():
    if request.method == 'POST':
        if 'cookies_file' in request.files:
            file = request.files['cookies_file']
            if file.filename == '':
                flash('No file selected')
                return redirect(url_for('cookies_page'))

            if file and file.filename and file.filename.endswith('.txt'):
                try:
                    content = file.read().decode('utf-8')

                    if 'youtube.com' not in content.lower():
                        flash('Invalid cookie file: must contain YouTube cookies')
                        return redirect(url_for('cookies_page'))

                    with open(COOKIES_FILE, 'w') as f:
                        f.write(content)

                    is_valid, validation_msg = validate_cookies()
                    if not is_valid:
                        os.remove(COOKIES_FILE)
                        flash(f'Cookie validation failed: {validation_msg}')
                        return redirect(url_for('cookies_page'))

                    flash('Cookies uploaded and validated successfully!')
                    return redirect(url_for('cookies_page'))
                except Exception as e:
                    flash(f'Error uploading cookies: {str(e)}')
                    return redirect(url_for('cookies_page'))
            else:
                flash('Please upload a .txt file')
                return redirect(url_for('cookies_page'))

        elif 'delete_cookies' in request.form:
            try:
                if os.path.exists(COOKIES_FILE):
                    os.remove(COOKIES_FILE)
                flash('Cookies deleted successfully')
            except Exception as e:
                flash(f'Error deleting cookies: {str(e)}')
            return redirect(url_for('cookies_page'))

    cookies_exist = has_cookies()
    is_valid, message = validate_cookies() if cookies_exist else (False, "No cookies uploaded")

    return render_template('cookies.html', 
                         cookies_exist=cookies_exist, 
                         is_valid=is_valid, 
                         validation_message=message)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
