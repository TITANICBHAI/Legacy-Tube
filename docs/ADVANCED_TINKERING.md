# Advanced Tinkering Guide - YouTube to 3GP Converter

## 🎯 For Developers Who Want to Customize & Optimize

This guide is for advanced users who want to understand the internals and customize the app for their specific needs.

---

## 🔧 Architecture Overview

### Key Components
```
app.py                  → Main Flask application
build.sh               → Installation & verification script
render.yaml            → Render deployment config
Dockerfile             → Docker deployment config
templates/             → HTML templates (Jinja2)
/tmp/downloads/        → Temporary video storage (auto-cleanup)
/tmp/cookies/          → YouTube cookies storage
```

### Process Flow
1. **User submits URL** → `generate_file_id()` creates unique hash
2. **Download strategies** → 4 fallback methods (Android TV → iOS → Android → Web)
3. **Video download** → yt-dlp with timeout & retry logic
4. **Conversion** → FFmpeg converts to 3GP format
5. **Auto-cleanup** → Background thread deletes files after 6 hours

---

## 🎮 Advanced Configuration Options

### 1. Increase Worker/Thread Count (Requires More RAM)

**Current (Free Tier - 512MB RAM):**
```bash
--workers=1 --threads=2
```

**For Render Standard ($25/month - 2GB RAM):**
```yaml
# render.yaml
startCommand: "gunicorn --bind=0.0.0.0:$PORT --workers=2 --threads=4 --timeout=600 ..."
```

**For Render Pro ($85/month - 4GB RAM):**
```yaml
startCommand: "gunicorn --bind=0.0.0.0:$PORT --workers=4 --threads=4 --timeout=600 ..."
```

**Memory formula:** Each worker uses ~250-400MB RAM depending on video size.

---

### 2. Adjust Download Strategy Order

**Edit `app.py` around line 200-250** to change fallback priority:

```python
# Current order (optimized for bypassing restrictions):
DOWNLOAD_STRATEGIES = [
    ('Android TV', 'com.google.android.apps.youtube.unplugged/1.0'),
    ('iOS', 'com.google.ios.youtube/19.29.1'),
    ('Android Mobile', 'com.google.android.youtube/19.29.37'),
    ('Web Embedded', None)
]

# Fastest-first order (best for public videos):
DOWNLOAD_STRATEGIES = [
    ('Web Embedded', None),                                      # Fastest
    ('Android Mobile', 'com.google.android.youtube/19.29.37'),  # Fast
    ('iOS', 'com.google.ios.youtube/19.29.1'),                  # Medium
    ('Android TV', 'com.google.android.apps.youtube.unplugged/1.0')  # Slowest but most reliable
]
```

---

### 3. FFmpeg Quality Settings

**Current settings (optimized for speed on free tier):**
```python
# In app.py, find the ffmpeg conversion command (~line 300-350)
cmd = [
    'ffmpeg', '-i', input_file,
    '-vcodec', 'h263',      # H.263 codec for 3GP
    '-acodec', 'aac',       # AAC audio
    '-strict', 'experimental',
    '-ac', '2',             # Stereo audio
    '-ar', '22050',         # 22.05 kHz sample rate
    '-ab', '64k',           # 64 kbps audio bitrate
    '-vb', '256k',          # 256 kbps video bitrate
    '-s', '176x144',        # QCIF resolution
    '-r', '15',             # 15 fps
    output_file
]
```

**Better quality (slower, uses more CPU):**
```python
cmd = [
    'ffmpeg', '-i', input_file,
    '-vcodec', 'h263',
    '-acodec', 'aac',
    '-strict', 'experimental',
    '-ac', '2',
    '-ar', '44100',         # Better audio quality (44.1 kHz)
    '-ab', '128k',          # Better audio bitrate (128 kbps)
    '-vb', '512k',          # Better video bitrate (512 kbps)
    '-s', '320x240',        # QVGA resolution (better)
    '-r', '24',             # 24 fps (smoother)
    '-preset', 'medium',    # Slower encoding, better quality
    output_file
]
```

**Fastest (lowest quality):**
```python
cmd = [
    'ffmpeg', '-i', input_file,
    '-vcodec', 'h263',
    '-acodec', 'aac',
    '-strict', 'experimental',
    '-ac', '1',             # Mono audio (smaller)
    '-ar', '16000',         # Lower sample rate (16 kHz)
    '-ab', '32k',           # Lower bitrate (32 kbps)
    '-vb', '128k',          # Lower video bitrate (128 kbps)
    '-s', '128x96',         # Tiny resolution
    '-r', '12',             # 12 fps
    '-preset', 'ultrafast', # Fastest encoding
    output_file
]
```

---

### 4. Change File Retention Time

**Current: 6 hours**

Edit `render.yaml`:
```yaml
- key: FILE_RETENTION_HOURS
  value: 12  # Keep files for 12 hours instead
```

Or for Docker (`docker-compose.yml`):
```yaml
environment:
  - FILE_RETENTION_HOURS=12
```

**Warning**: Longer retention = more disk usage!

---

### 5. Increase Video Duration Limits

**Current: 6 hours (21600 seconds)**

```yaml
# render.yaml
- key: MAX_VIDEO_DURATION
  value: 43200  # 12 hours
```

**Caution**: Longer videos = more memory usage and crash risk on free tier!

---

### 6. Enable Debug Mode (Development Only)

**Edit `app.py` at the bottom:**

```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)  # Change to True
```

**⚠️ NEVER enable in production!** It exposes internal errors to users.

---

## 🚀 Performance Optimizations for Render

### 1. Use Redis for Status Tracking (Advanced)

Instead of JSON file, use Redis for better performance:

**Add to `requirements.txt`:**
```
redis
```

**Add to `app.py`:**
```python
import redis
r = redis.from_url(os.environ.get('REDIS_URL'))

def update_status(file_id, updates):
    r.hmset(f"status:{file_id}", updates)
    r.expire(f"status:{file_id}", FILE_RETENTION_HOURS * 3600)
```

**Add Redis service** on Render dashboard ($7/month).

---

### 2. Pre-warm the Service (Prevent Spin-Down)

Free tier spins down after 15 minutes. Use a free cron service to ping it:

**Option A: Use cron-job.org (free)**
1. Go to https://cron-job.org
2. Create job: `https://your-app.onrender.com/health`
3. Schedule: Every 14 minutes

**Option B: Use UptimeRobot (free)**
1. Go to https://uptimerobot.com
2. Add HTTP monitor: `https://your-app.onrender.com/health`
3. Interval: 5 minutes

**⚠️ Note**: This keeps your app "awake" but uses your 750 free hours faster!

---

### 3. Upgrade FFmpeg Version

Render comes with old ffmpeg (4.1.11). To get latest version:

**Edit `build.sh`:**
```bash
#!/usr/bin/env bash
set -o errexit

echo "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "Downloading latest ffmpeg static build..."
mkdir -p /opt/ffmpeg
cd /opt/ffmpeg
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar -xf ffmpeg-release-amd64-static.tar.xz --strip-components=1
export PATH="/opt/ffmpeg:$PATH"

echo "Installing yt-dlp..."
if command -v apt-get &> /dev/null; then
    apt-get update -qq
    apt-get install -y -qq yt-dlp
fi

echo "Verifying installations..."
python --version
/opt/ffmpeg/ffmpeg -version | head -1
yt-dlp --version

echo "Creating required folders..."
mkdir -p /tmp/downloads
mkdir -p /tmp/cookies

echo "Build completed successfully!"
```

Then in `app.py`, change ffmpeg calls:
```python
cmd = ['/opt/ffmpeg/ffmpeg', '-i', input_file, ...]
```

---

### 4. Add Progress WebSocket (Real-time Updates)

**Add to `requirements.txt`:**
```
flask-socketio
```

**In `app.py`:**
```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app)

@socketio.on('check_progress')
def handle_progress(data):
    file_id = data['file_id']
    status = get_status().get(file_id, {})
    emit('progress_update', status)
```

**In template:**
```javascript
<script src="//cdn.socket.io/4.0.0/socket.io.min.js"></script>
<script>
  const socket = io();
  socket.emit('check_progress', {file_id: '{{ file_id }}'});
  socket.on('progress_update', (data) => {
    // Update UI with progress
  });
</script>
```

---

### 5. Parallel Downloads (Multiple Videos)

**⚠️ Requires Standard plan or higher (2GB+ RAM)**

Edit `app.py` to use ThreadPoolExecutor:

```python
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=3)

@app.route('/convert', methods=['POST'])
def convert():
    # Instead of direct call:
    # download_and_convert(url, file_id)
    
    # Use executor:
    executor.submit(download_and_convert, url, file_id)
    return redirect(url_for('status', file_id=file_id))
```

---

### 6. Use Object Storage (S3/Cloudflare R2)

Instead of ephemeral `/tmp`, store files in S3:

**Add to `requirements.txt`:**
```
boto3
```

**Add to `app.py`:**
```python
import boto3

s3 = boto3.client('s3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_KEY')
)

def upload_to_s3(local_file, file_id):
    s3.upload_file(local_file, 'your-bucket', f'{file_id}.3gp')
    return s3.generate_presigned_url('get_object',
        Params={'Bucket': 'your-bucket', 'Key': f'{file_id}.3gp'},
        ExpiresIn=21600)  # 6 hour download link
```

---

## 🧪 Experimental Features

### 1. Support More Output Formats

Add MP4, WEBM, etc:

```python
SUPPORTED_FORMATS = {
    '3gp': {'vcodec': 'h263', 'acodec': 'aac'},
    'mp4': {'vcodec': 'libx264', 'acodec': 'aac'},
    'webm': {'vcodec': 'libvpx', 'acodec': 'libvorbis'}
}

@app.route('/convert', methods=['POST'])
def convert():
    format = request.form.get('format', '3gp')
    codec_settings = SUPPORTED_FORMATS.get(format)
    # Use in ffmpeg command
```

---

### 2. Thumbnail Generation

```python
def generate_thumbnail(video_file, output_thumb):
    cmd = [
        'ffmpeg', '-i', video_file,
        '-ss', '00:00:05',  # 5 seconds in
        '-vframes', '1',     # 1 frame
        '-vf', 'scale=320:-1',
        output_thumb
    ]
    subprocess.run(cmd, timeout=30)
```

---

### 3. Video Trimming

Let users specify start/end time:

```python
@app.route('/convert', methods=['POST'])
def convert():
    start_time = request.form.get('start', '00:00:00')
    end_time = request.form.get('end', None)
    
    cmd = ['ffmpeg', '-i', input_file]
    if start_time:
        cmd.extend(['-ss', start_time])
    if end_time:
        cmd.extend(['-to', end_time])
    cmd.extend(['-vcodec', 'h263', ...])
```

---

## 🐛 Debugging Tips

### 1. Check FFmpeg Version
```bash
# SSH into Render shell (requires paid plan)
ffmpeg -version
```

### 2. Monitor Memory Usage
Add to `app.py`:
```python
import psutil

@app.route('/metrics')
def metrics():
    mem = psutil.virtual_memory()
    return {
        'memory_used_mb': mem.used / 1024 / 1024,
        'memory_percent': mem.percent,
        'cpu_percent': psutil.cpu_percent(interval=1)
    }
```

### 3. Enable Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 4. Test Locally with Docker
```bash
docker-compose up --build
curl http://localhost:5000/health
```

---

## 💡 Ideas to Make It Work Better on Render

### ✅ Already Implemented
1. ✅ Single worker for memory efficiency
2. ✅ Auto-cleanup background thread
3. ✅ 4 download strategies with fallbacks
4. ✅ Health check endpoint
5. ✅ Cache-control headers

### 🚀 Additional Optimizations

#### 1. **Use Render Background Worker for Conversions**
Move heavy conversion to background worker (free tier includes this):

**Add `render.yaml`:**
```yaml
services:
  - type: web
    name: youtube-3gp-web
    # ... existing config

  - type: worker
    name: youtube-3gp-worker
    env: python
    buildCommand: "bash build.sh"
    startCommand: "python worker.py"
```

**Create `worker.py`:**
```python
import redis
r = redis.from_url(os.environ.get('REDIS_URL'))

while True:
    task = r.blpop('conversion_queue', timeout=60)
    if task:
        # Process conversion
        download_and_convert(task['url'], task['file_id'])
```

#### 2. **Add Rate Limiting**
Prevent abuse on free tier:

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/convert', methods=['POST'])
@limiter.limit("10 per hour")  # Max 10 conversions per IP per hour
def convert():
    # ...
```

#### 3. **Compress Download Before Conversion**
```python
# Use yt-dlp's built-in compression
ytdlp_args = [
    'yt-dlp',
    '-f', 'worst[height<=360]',  # Download lower quality to save memory
    # ... rest
]
```

#### 4. **Enable Streaming Download**
Instead of downloading entire video first:

```python
ytdlp_args.append('--concurrent-fragments')
ytdlp_args.append('2')  # Download 2 fragments at once
```

#### 5. **Use Render Cron for Cleanup**
Instead of background thread, use Render's cron job:

**Add to `render.yaml`:**
```yaml
  - type: cron
    name: cleanup-old-files
    env: python
    schedule: "0 * * * *"  # Every hour
    buildCommand: "bash build.sh"
    startCommand: "python cleanup.py"
```

**Create `cleanup.py`:**
```python
import os
import time

for file in os.listdir('/tmp/downloads'):
    file_path = os.path.join('/tmp/downloads', file)
    if time.time() - os.path.getmtime(file_path) > 21600:  # 6 hours
        os.remove(file_path)
```

---

## 📊 Render Free Tier FFmpeg Status

### ✅ **Confirmed: No bin folder needed!**

**What Render Provides:**
- ffmpeg version 4.1.11-0 (pre-installed)
- Path: `/usr/bin/ffmpeg`
- Works out of the box

**Your `build.sh` handles it:**
```bash
apt-get install -y -qq ffmpeg yt-dlp
```

**For Docker deployments**, your `Dockerfile` already installs it:
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg
```

### 🎯 **Myth Busted!**
- ❌ You DON'T need a `/bin` folder
- ❌ You DON'T need static binaries
- ✅ System package manager (apt-get) works perfectly
- ✅ Native environment includes ffmpeg

---

## 🎓 Learning Resources

1. **FFmpeg Documentation**: https://ffmpeg.org/documentation.html
2. **yt-dlp Options**: https://github.com/yt-dlp/yt-dlp#usage-and-options
3. **Gunicorn Tuning**: https://docs.gunicorn.org/en/stable/design.html
4. **Flask Best Practices**: https://flask.palletsprojects.com/en/stable/
5. **Render Docs**: https://render.com/docs

---

## ⚠️ Important Warnings

1. **Never commit secrets** to Git (cookies, API keys)
2. **Test locally first** before deploying changes
3. **Monitor memory** when changing worker count
4. **Backup important data** before major changes
5. **Free tier has limits** - don't expect production performance

---

## 🤝 Contributing Ideas

Want to improve this app? Here are some ideas:

1. Add playlist support (download multiple videos)
2. Implement user accounts with rate limits
3. Add video preview/thumbnail generation
4. Support audio-only extraction (MP3)
5. Add batch conversion queue
6. Implement progress bar with WebSockets
7. Add video metadata editing
8. Support subtitle extraction

---

## 📝 Final Notes

This app is optimized for **Render's free tier constraints**. Most advanced features require:
- **Standard plan ($25/month)**: 2GB RAM, can handle 2-4 workers
- **Pro plan ($85/month)**: 4GB RAM, can handle 4-8 workers

For personal use, **free tier is perfectly fine** with current settings!

Happy tinkering! 🚀
