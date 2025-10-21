# 📱 YouTube to 3GP Converter for Feature Phones

Convert YouTube videos to 3GP format optimized for feature phones like Nokia 5310 and old browsers like Opera Mini 4.4.

![Feature Phone Friendly](https://img.shields.io/badge/Nokia%205310-Compatible-green)
![Opera Mini](https://img.shields.io/badge/Opera%20Mini%204.4-Compatible-blue)
![2G Network](https://img.shields.io/badge/2G%20Network-Optimized-orange)

## ✨ Features

- **No JavaScript** - Works on Opera Mini 4.4 and older browsers
- **Ultra-Low Bitrate** - Optimized for 2G networks (176x144 resolution)
- **Long Videos** - Supports up to 6 hours of video
- **Auto Cleanup** - Files deleted after 6 hours
- **Free Forever** - No API keys, no ads, completely free
- **Time Estimates** - Shows processing time from the start (no guessing!)

## 📊 Technical Details

- **Resolution**: 176x144 (perfect for feature phone screens)
- **Format**: 3GP
- **Video Codec**: MPEG-4 (200kbps)
- **Audio Codec**: AAC (12.2kbps, 8000 Hz)
- **Max Duration**: 6 hours
- **Max File Size**: 500 MB
- **File Size**: ~2-3 MB per 5 minutes

## 🚀 Quick Deploy to Render.com

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

1. Push this repo to GitHub
2. Create account on Render.com (free)
3. Click "New Web Service" → Connect GitHub repo
4. Render auto-detects `render.yaml` and deploys!

See [DEPLOY.md](DEPLOY.md) for detailed instructions.

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
├── app.py              # Main Flask application
├── templates/          # HTML templates (feature phone optimized)
│   ├── base.html
│   ├── index.html
│   └── status.html
├── requirements.txt    # Python dependencies
├── render.yaml         # Render deployment config
├── build.sh           # Build script for Render
└── DEPLOY.md          # Deployment guide
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
