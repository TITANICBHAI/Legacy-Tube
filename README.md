# 📱 YouTube to 3GP Converter for Feature Phones

Convert YouTube videos to 3GP format optimized for feature phones like Nokia 5310 and old browsers like Opera Mini 4.4.

![Feature Phone Friendly](https://img.shields.io/badge/Nokia%205310-Compatible-green)
![Opera Mini](https://img.shields.io/badge/Opera%20Mini%204.4-Compatible-blue)
![2G Network](https://img.shields.io/badge/2G%20Network-Optimized-orange)

## ✨ Features

### Core Features
- **Works Without Cookies** - 4 automatic fallback strategies for YouTube downloads
- **No JavaScript** - Works on Opera Mini 4.4 and older browsers
- **Ultra-Low Bitrate** - Optimized for 2G networks (176x144 resolution)
- **Long Videos** - Supports up to 6 hours of video
- **Auto Cleanup** - Files deleted after 6 hours
- **Free Forever** - No API keys, no ads, completely free
- **Time Estimates** - Shows processing time from the start (no guessing!)

### Advanced Features
- **Multi-Strategy Downloads** - Android TV → iOS → Android Mobile → Web Embedded clients
- **Rate Limit Protection** - Progressive retry with exponential backoff
- **Memory Optimized** - Runs perfectly on Render's 512MB free tier
- **Health Monitoring** - `/health` endpoint for uptime checks
- **Graceful Shutdown** - Automatic cleanup on container restart
- **Cookie Authentication** - Optional cookie support for restricted videos (see `/cookies` page)

## 📊 Technical Details

- **Resolution**: 176x144 (perfect for feature phone screens)
- **Format**: 3GP
- **Video Codec**: MPEG-4 (200kbps)
- **Audio Codec**: AAC (12.2kbps, 8000 Hz)
- **Max Duration**: 6 hours
- **Max File Size**: 500 MB
- **File Size**: ~2-3 MB per 5 minutes

## 🚀 Deployment Options

### Option 1: Render.com (Recommended - Free Tier)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

**Quick Setup (5 minutes):**
1. Push this repo to GitHub
2. Create account on Render.com (free, no credit card)
3. Click "New Web Service" → Connect GitHub repo
4. Render auto-detects `render.yaml` and deploys!

**📖 Deployment Guides:**
- **[RENDER_MANUAL_SETUP.md](RENDER_MANUAL_SETUP.md)** - Complete step-by-step manual for every option (beginners start here!)
- **[RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)** - Free tier optimization guide and troubleshooting
- **[DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)** - Quick overview of all improvements

### Option 2: Docker (Any Platform)

**Using Docker Compose:**
```bash
docker-compose up --build
```

**Manual Docker:**
```bash
docker build -t youtube-3gp .
docker run -p 5000:5000 youtube-3gp
```

**📖 Documentation:**
- **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** - Complete Docker guide with advanced options
- **[Dockerfile](Dockerfile)** - Production-ready, multi-stage build
- **[docker-compose.yml](docker-compose.yml)** - Local testing setup

### Option 3: Native Python (Advanced)

See **[DEPLOY.md](DEPLOY.md)** for traditional deployment instructions.

## 🖥️ Local Development

```bash
# Install Python dependencies (includes yt-dlp)
pip install -r requirements.txt

# Install system dependencies (Ubuntu/Debian)
sudo apt-get install ffmpeg

# Run locally
python app.py
```

Visit `http://localhost:5000`

## 📁 Project Structure

```
.
├── app.py                      # Main Flask application
├── templates/                  # HTML templates (feature phone optimized)
│   ├── base.html              # Base template with minimal CSS
│   ├── index.html             # Homepage with URL input
│   ├── status.html            # Conversion progress page
│   └── cookies.html           # Cookie management page
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Production Docker image
├── docker-compose.yml         # Local Docker testing
├── .dockerignore             # Docker build optimization
├── .env.example              # Environment variables template
├── render.yaml               # Render deployment config
├── build.sh                  # Build script for Render
└── Documentation/
    ├── RENDER_MANUAL_SETUP.md    # Step-by-step Render guide (START HERE!)
    ├── RENDER_DEPLOYMENT.md      # Render optimization guide
    ├── DOCKER_DEPLOYMENT.md      # Docker setup guide
    ├── DEPLOYMENT_SUMMARY.md     # Quick overview
    ├── COOKIE_SETUP_GUIDE.md     # Optional cookie authentication
    └── DEPLOY.md                 # General deployment guide
```

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SESSION_SECRET` | Auto-generated | Flask session secret |
| `MAX_VIDEO_DURATION` | 21600 | Max video duration (seconds) |
| `DOWNLOAD_TIMEOUT` | 3600 | Download timeout (seconds) |
| `CONVERSION_TIMEOUT` | 21600 | Conversion timeout (seconds) |
| `FILE_RETENTION_HOURS` | 6 | File retention time (hours) |
| `MAX_FILESIZE` | 500M | Max download file size |

## 🎯 Use Cases

- Download music videos for Nokia feature phones
- Convert lectures/tutorials for offline viewing on 2G
- Save YouTube content for devices with limited storage
- Perfect for areas with slow internet connections

## 📱 Compatible Devices

Tested and working on:
- Nokia 5310
- Nokia 3310 (newer models)
- Any feature phone with 3GP support
- Opera Mini 4.4 browser

## 🔒 Privacy

- No data collection
- No user tracking
- No analytics
- Files auto-delete after 6 hours
- Open source - see the code yourself!

## 📝 License

MIT License - Free to use, modify, and distribute

## 🙏 Acknowledgments

- Built with Flask (Python)
- Powered by yt-dlp
- Video conversion by FFmpeg
- Optimized for the nostalgia of feature phones 📱

---

Made with ❤️ for feature phone users everywhere
