import os
import subprocess
import time
import threading
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from werkzeug.utils import secure_filename
import hashlib

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')

DOWNLOAD_FOLDER = '/tmp/downloads'
STATUS_FILE = '/tmp/conversion_status.json'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def get_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_status(status_data):
    with open(STATUS_FILE, 'w') as f:
        json.dump(status_data, f)

def generate_file_id(url):
    return hashlib.md5(url.encode()).hexdigest()[:12]

def download_and_convert(url, file_id):
    status = get_status()
    status[file_id] = {
        'status': 'downloading',
        'progress': 'Downloading video from YouTube...',
        'url': url,
        'timestamp': datetime.now().isoformat()
    }
    save_status(status)
    
    output_path = os.path.join(DOWNLOAD_FOLDER, f'{file_id}.3gp')
    temp_video = os.path.join(DOWNLOAD_FOLDER, f'{file_id}_temp.mp4')
    
    try:
        
        status[file_id]['status'] = 'downloading'
        status[file_id]['progress'] = 'Downloading video...'
        save_status(status)
        
        download_cmd = [
            'yt-dlp',
            '-f', 'worst',
            '-o', temp_video,
            url
        ]
        
        result = subprocess.run(download_cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            raise Exception(f"Download failed: {result.stderr}")
        
        status[file_id]['status'] = 'converting'
        status[file_id]['progress'] = 'Converting to 3GP format (176x144)...'
        save_status(status)
        
        convert_cmd = [
            'ffmpeg',
            '-i', temp_video,
            '-s', '176x144',
            '-r', '12',
            '-vcodec', 'h263',
            '-b:v', '64k',
            '-acodec', 'amr_nb',
            '-ar', '8000',
            '-ac', '1',
            '-b:a', '12.2k',
            '-y',
            output_path
        ]
        
        result = subprocess.run(convert_cmd, capture_output=True, text=True, timeout=300)
        
        if os.path.exists(temp_video):
            os.remove(temp_video)
        
        if result.returncode != 0:
            raise Exception(f"Conversion failed: {result.stderr}")
        
        file_size = os.path.getsize(output_path)
        file_size_mb = file_size / (1024 * 1024)
        
        status[file_id]['status'] = 'completed'
        status[file_id]['progress'] = f'Conversion complete! File size: {file_size_mb:.2f} MB'
        status[file_id]['filename'] = f'{file_id}.3gp'
        status[file_id]['file_size'] = file_size
        status[file_id]['completed_at'] = datetime.now().isoformat()
        save_status(status)
        
    except Exception as e:
        status[file_id]['status'] = 'failed'
        status[file_id]['progress'] = f'Error: {str(e)}'
        save_status(status)
        if os.path.exists(temp_video):
            os.remove(temp_video)

def cleanup_old_files():
    while True:
        try:
            time.sleep(1800)
            
            cutoff_time = datetime.now() - timedelta(hours=2)
            status = get_status()
            
            for file_id, data in list(status.items()):
                if 'completed_at' in data:
                    completed_time = datetime.fromisoformat(data['completed_at'])
                    if completed_time < cutoff_time:
                        file_path = os.path.join(DOWNLOAD_FOLDER, f'{file_id}.3gp')
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        del status[file_id]
            
            save_status(status)
            
            for filename in os.listdir(DOWNLOAD_FOLDER):
                file_path = os.path.join(DOWNLOAD_FOLDER, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        
        except Exception as e:
            print(f"Cleanup error: {e}")

cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

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
    app.run(host='0.0.0.0', port=5000, debug=False)
