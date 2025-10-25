import os
import subprocess
import time
import threading
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import hashlib
# ----------- ROTATING PROXY POOL -----------
PROXIES = [
    "http://144.91.109.105:3128",
    "http://51.38.83.147:3128",
    "http://188.166.83.65:8080",
    "http://51.83.163.41:8080",
    "http://51.158.68.68:8811",
    "http://144.91.75.67:3128",
    "http://165.22.254.150:8080",
    "http://157.245.207.174:3128",
    "http://144.91.74.189:3128",
    "http://165.22.255.102:8080"
]  # Replace or add more free proxies if needed

import random

def get_random_proxy():
    return random.choice(PROXIES)

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
STATUS_FILE = '/tmp/conversion_status.json'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

MAX_VIDEO_DURATION = int(os.environ.get('MAX_VIDEO_DURATION', 6 * 3600))
DOWNLOAD_TIMEOUT = int(os.environ.get('DOWNLOAD_TIMEOUT', 3600))
CONVERSION_TIMEOUT = int(os.environ.get('CONVERSION_TIMEOUT', 21600))
FILE_RETENTION_HOURS = int(os.environ.get('FILE_RETENTION_HOURS', 6))
MAX_FILESIZE = os.environ.get('MAX_FILESIZE', '500M')

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
        # Retry loop with rotating proxies
        for attempt in range(5):
            proxy = get_random_proxy()  # pick a random proxy for each attempt

            download_cmd = [
                'yt-dlp',
                '-f', 'worst/best',
                '--merge-output-format', 'mp4',
                '-o', temp_video,
                '--max-filesize', MAX_FILESIZE,
                '--no-check-certificates',
                '--extractor-args', 'youtube:player_client=android,web',
                '--force-ipv4',
                '--user-agent', 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
                '--retries', '5',
                '--retry-sleep', '3',
                '--sleep-requests', '2',
                '--concurrent-fragments', '1',
                '--proxy', proxy,  # <--- proxy applied here
                '--no-abort-on-error',
                url
            ]

            result = subprocess.run(download_cmd, capture_output=True, text=True, timeout=DOWNLOAD_TIMEOUT)

            if result.returncode == 0 and os.path.exists(temp_video):
                break  # success
            else:
                if attempt < 4:
                    continue  # try next proxy
                else:
                    error_msg = result.stderr
                    raise Exception(f"Download failed after 5 attempts: {error_msg[:200]}")

        # --- Existing duration & size checks ---
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
            '-r', '15',
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
    return render_template('index.html', max_hours=max_hours)

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
