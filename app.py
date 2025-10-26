import os
import subprocess
import time
import threading
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import hashlib

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

MAX_VIDEO_DURATION = int(os.environ.get('MAX_VIDEO_DURATION', 10 * 3600))
DOWNLOAD_TIMEOUT = int(os.environ.get('DOWNLOAD_TIMEOUT', 3600))
CONVERSION_TIMEOUT = int(os.environ.get('CONVERSION_TIMEOUT', 21600))
FILE_RETENTION_HOURS = int(os.environ.get('FILE_RETENTION_HOURS', 6))
MAX_FILESIZE = os.environ.get('MAX_FILESIZE', '2G')

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

def get_video_duration(file_path):
    try:
        cmd = [
            'ffprobe',
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

def download_and_convert(url, file_id):
    update_status(file_id, {
        'status': 'downloading',
        'progress': 'Downloading video from YouTube... (this may take several minutes for long videos)',
        'url': url,
        'timestamp': datetime.now().isoformat()
    })
    
    output_path = os.path.join(DOWNLOAD_FOLDER, f'{file_id}.3gp')
    temp_video = os.path.join(DOWNLOAD_FOLDER, f'{file_id}_temp.mp4')
    
    try:
        base_cmd = [
            'yt-dlp',
            '-f', 'worst/best',
            '--merge-output-format', 'mp4',
            '-o', temp_video,
            '--max-filesize', MAX_FILESIZE,
            '--no-check-certificates',
            '--force-ipv4',
            '--retries', '15',
            '--retry-sleep', '3',
            '--fragment-retries', '15',
            '--sleep-requests', '1',
            '--concurrent-fragments', '1',
            '--no-abort-on-error',
            '--extractor-retries', '10',
            '--socket-timeout', '30',
            '--http-chunk-size', '10M'
        ]
        
        strategies = [
            {
                'name': 'Android TV',
                'args': [
                    '--extractor-args', 'youtube:player_client=android_embedded,android,ios;player_skip=webpage,configs',
                    '--user-agent', 'com.google.android.youtube/19.02.39 (Linux; U; Android 13; Pixel 7) gzip'
                ]
            },
            {
                'name': 'iOS',
                'args': [
                    '--extractor-args', 'youtube:player_client=ios,android;player_skip=webpage',
                    '--user-agent', 'com.google.ios.youtube/19.02.3 (iPhone14,3; U; CPU iOS 16_0 like Mac OS X)'
                ]
            },
            {
                'name': 'Android Mobile',
                'args': [
                    '--extractor-args', 'youtube:player_client=android,web;player_skip=configs',
                    '--user-agent', 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
                ]
            },
            {
                'name': 'Web Embedded',
                'args': [
                    '--extractor-args', 'youtube:player_client=web_embedded,web;player_skip=webpage',
                    '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            }
        ]
        
        if has_cookies():
            base_cmd.extend(['--cookies', COOKIES_FILE])
        
        result = None
        last_error = None
        
        for i, strategy in enumerate(strategies):
            try:
                download_cmd = base_cmd + strategy['args'] + [url]
                
                if i > 0:
                    update_status(file_id, {
                        'status': 'downloading',
                        'progress': f'Retrying with {strategy["name"]} client... (attempt {i+1}/{len(strategies)})'
                    })
                    time.sleep(3 * i)
                
                result = subprocess.run(download_cmd, capture_output=True, text=True, timeout=DOWNLOAD_TIMEOUT)
                
                if result.returncode == 0 and os.path.exists(temp_video):
                    break
                else:
                    last_error = result.stderr
                    
            except subprocess.TimeoutExpired:
                last_error = "Download timeout"
                continue
            except Exception as e:
                last_error = str(e)
                continue
        
        if not result or result.returncode != 0:
            error_msg = last_error if last_error else "All download strategies failed"
            
            if 'duration' in error_msg.lower():
                raise Exception(f"Video exceeds {MAX_VIDEO_DURATION/3600:.0f}-hour limit")
            if 'filesize' in error_msg.lower() or 'too large' in error_msg.lower():
                raise Exception(f"Video file too large (limit: {MAX_FILESIZE})")
            if '429' in error_msg or 'too many requests' in error_msg.lower():
                raise Exception("YouTube rate limit reached. Please wait 5-10 minutes and try again.")
            if 'age' in error_msg.lower() and 'restricted' in error_msg.lower():
                raise Exception("Video is age-restricted. Cannot download without YouTube account.")
            if 'private' in error_msg.lower() or 'members-only' in error_msg.lower():
                raise Exception("Video is private or members-only. Cannot download.")
            if 'geo' in error_msg.lower() or 'not available in your country' in error_msg.lower() or 'not made this video available in your country' in error_msg.lower():
                raise Exception("Video is geo-restricted by the uploader and not available in your region. Try a different video or use a VPN to access region-locked content.")
            if 'copyright' in error_msg.lower() or 'removed' in error_msg.lower():
                raise Exception("Video removed due to copyright claim or deletion.")
            if 'live' in error_msg.lower() and 'stream' in error_msg.lower():
                raise Exception("Cannot download live streams. Try again after the stream ends.")
            if 'sign in' in error_msg.lower() or 'login' in error_msg.lower() or 'bot' in error_msg.lower():
                if has_cookies():
                    raise Exception("YouTube authentication failed even with cookies. Try: 1) Upload fresh cookies from /cookies page, or 2) Wait 10 minutes and retry.")
                else:
                    raise Exception("YouTube is asking for sign-in verification. This video may work with cookies - see /cookies page for optional setup. Or try a different video.")
            
            raise Exception(f"Download failed: {error_msg[:200]}")
        
        if not os.path.exists(temp_video):
            raise Exception("Download failed: Video file not created")
        
        duration = get_video_duration(temp_video)
        if duration > MAX_VIDEO_DURATION:
            os.remove(temp_video)
            raise Exception(f"Video is {duration/3600:.1f} hours long. Maximum allowed is {MAX_VIDEO_DURATION/3600:.0f} hours.")
        
        file_size = os.path.getsize(temp_video)
        file_size_mb = file_size / (1024 * 1024)
        
        est_time = max(1, int(duration / 60))
        update_status(file_id, {
            'status': 'converting',
            'progress': f'Converting to 3GP format... Video: {duration/60:.1f} minutes, Size: {file_size_mb:.1f} MB. Estimated time: {est_time}-{est_time*2} minutes.'
        })
        
        convert_cmd = [
            'ffmpeg',
            '-i', temp_video,
            '-vf', 'scale=176:144:force_original_aspect_ratio=decrease,pad=176:144:(ow-iw)/2:(oh-ih)/2,setsar=1',
            '-vcodec', 'mpeg4',
            '-r', '12',
            '-b:v', '300k',
            '-acodec', 'aac',
            '-ar', '22050',
            '-b:a', '48000',
            '-ac', '1',
            '-y',
            output_path
        ]
        
        dynamic_timeout = max(CONVERSION_TIMEOUT, int(duration * 2))
        result = subprocess.run(convert_cmd, capture_output=True, text=True, timeout=dynamic_timeout)
        
        if os.path.exists(temp_video):
            try:
                os.remove(temp_video)
            except:
                pass
        
        if result.returncode != 0:
            raise Exception(f"Conversion failed: {result.stderr[:200]}")
        
        if not os.path.exists(output_path):
            raise Exception("Conversion failed: Output file not created")
        
        final_size = os.path.getsize(output_path)
        final_size_mb = final_size / (1024 * 1024)
        
        update_status(file_id, {
            'status': 'completed',
            'progress': f'Conversion complete! Duration: {duration/60:.1f} min, File size: {final_size_mb:.2f} MB',
            'filename': f'{file_id}.3gp',
            'file_size': final_size,
            'duration': duration,
            'completed_at': datetime.now().isoformat()
        })
        
    except subprocess.TimeoutExpired:
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
        update_status(file_id, {
            'status': 'failed',
            'progress': f'Error: {str(e)}'
        })
        if os.path.exists(temp_video):
            try:
                os.remove(temp_video)
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
                            file_path = os.path.join(DOWNLOAD_FOLDER, f'{file_id}.3gp')
                            if os.path.exists(file_path):
                                os.remove(file_path)
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

@app.route('/')
def index():
    max_hours = MAX_VIDEO_DURATION / 3600
    cookies_status = has_cookies()
    return render_template('index.html', max_hours=max_hours, has_cookies=cookies_status)

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/convert', methods=['POST'])
def convert():
    url = request.form.get('url', '').strip()
    
    if not url:
        flash('Please enter a YouTube URL')
        return redirect(url_for('index'))
    
    if 'youtube.com' not in url and 'youtu.be' not in url:
        flash('Please enter a valid YouTube URL')
        return redirect(url_for('index'))
    
    file_id = generate_file_id(url)
    
    thread = threading.Thread(target=download_and_convert, args=(url, file_id))
    thread.daemon = True
    thread.start()
    
    return redirect(url_for('status', file_id=file_id))

@app.route('/status/<file_id>')
def status(file_id):
    status_data = get_status()
    file_status = status_data.get(file_id, {'status': 'unknown', 'progress': 'File not found'})
    return render_template('status.html', file_id=file_id, file_status=file_status)

@app.route('/download/<file_id>')
def download(file_id):
    file_path = os.path.join(DOWNLOAD_FOLDER, f'{file_id}.3gp')
    
    if not os.path.exists(file_path):
        flash('File not found or has been deleted')
        return redirect(url_for('index'))
    
    return send_file(file_path, as_attachment=True, download_name=f'video_{file_id}.3gp')

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
