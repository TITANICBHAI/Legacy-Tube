# 🚀 Render Advanced Guide - YouTube to 3GP Converter

Complete advanced guide for deploying and optimizing on Render with YouTube IP block bypass solutions.

---

## 🎯 Quick Summary

**Known Issues & Solutions**:
- ✅ **YouTube IP blocking** → IPv6, Proxies, Cookies
- ✅ **429 Rate limiting** → Rate limits, delays, cookies
- ✅ **/tmp disk space (2GB limit)** → Auto-cleanup, monitoring
- ✅ **Memory limits (512MB)** → Optimized workers, cleanup
- ✅ **Cold starts (15 min)** → UptimeRobot ping

---

## 🔥 Known Issues & Advanced Solutions

### Issue 1: YouTube IP Blocking (403 Forbidden)

**Problem**: YouTube blocks cloud provider IPs (AWS, GCP, Azure) that Render uses.

**Symptoms**:
```
HTTP Error 403: Forbidden
Sign in to confirm you're not a bot
unable to download video data
```

**Solutions** (in order of effectiveness):

#### Solution A: Upload YouTube Cookies ⭐ **BEST**
```
1. Go to: https://your-app.onrender.com/cookies
2. Export cookies from your browser (see COOKIE_SETUP_GUIDE.md)
3. Upload the cookies.txt file
4. Try downloading again
```

**Why this works**: Authenticated requests are less likely to be blocked.

#### Solution B: Enable IPv6
```
Render Environment Variables:
USE_IPV6=true
```

**Why this works**: YouTube's IPv6 blocking is less aggressive than IPv4.

#### Solution C: Use a Proxy Server
```
Render Environment Variables:
PROXY_URL=http://username:password@proxy-server:port
```

**Proxy options**:
- Residential proxies (best, but paid): Bright Data, Smartproxy
- Free proxies (unreliable): Not recommended for production
- Self-hosted proxy: Run on home connection with WireGuard

#### Solution D: Combination Approach ⭐ **RECOMMENDED**
```
# Render Environment Variables
USE_IPV6=true
RATE_LIMIT_BYTES=500000  # 500KB/s limit
```
PLUS upload cookies from /cookies page.

---

### Issue 2: Rate Limiting (429 Too Many Requests)

**Problem**: YouTube detects too many requests and throttles your IP.

**Symptoms**:
```
HTTP Error 429: Too Many Requests
ERROR: unable to extract
Throttled at ~1MB/s
```

**Solutions**:

#### Solution A: Enable Rate Limiting ⭐ **PREVENTS 429**
```bash
# Render Environment Variables
RATE_LIMIT_BYTES=500000  # 500KB/s (prevents rate limits)
```

**Recommended values**:
- `500000` (500KB/s) - Safe, prevents most 429 errors
- `1000000` (1MB/s) - Faster, slight risk
- `0` (unlimited) - Fastest, high risk of 429

#### Solution B: Upload Cookies
Same as IP blocking solution - cookies help avoid rate limits.

#### Solution C: Wait and Retry
If you get 429 errors:
1. Wait 10-15 minutes
2. Try again
3. Your IP will be unthrottled

---

### Issue 3: Disk Space Limit (2GB /tmp Ephemeral Storage)

**Problem**: Render has a **HARD 2GB limit** on `/tmp` storage. Large videos can fill it up.

**Symptoms**:
```
Server storage full
Insufficient disk space for conversion
Pod evicted
SIGKILL errors
```

**Automatic Solutions** (Already Built-In):

✅ **Automatic disk space monitoring**  
✅ **Emergency cleanup when space low**  
✅ **Pre-download space checks**  
✅ **Auto-delete files after 6 hours**  

**Manual Solutions**:

#### Solution A: Reduce File Retention Time
```bash
# Render Environment Variables
FILE_RETENTION_HOURS=3  # Delete files after 3 hours instead of 6
```

#### Solution B: Limit Video Length
```bash
# Render Environment Variables
MAX_VIDEO_DURATION=1800  # 30 minutes max (in seconds)
MAX_FILESIZE=500M  # 500MB max download size
```

#### Solution C: Monitor Disk Space
```bash
# Enable/disable monitoring (enabled by default)
ENABLE_DISK_SPACE_MONITORING=true
DISK_SPACE_THRESHOLD_MB=1500  # Alert when <1.5GB free
```

#### Solution D: Manual Cleanup via API
```bash
# SSH into Render (paid plans only)
ssh YOUR_SERVICE@ssh.YOUR_REGION.render.com

# Check disk usage
df -h /tmp

# Find large files
du -sh /tmp/downloads/*

# Manual cleanup
rm -rf /tmp/downloads/*
```

---

### Issue 4: Memory Limits (512MB on Free Tier)

**Problem**: Free tier only has 512MB RAM. Large videos can cause OOM errors.

**Symptoms**:
```
SIGKILL
Worker timeout
Memory exceeded
Deployment failed
```

**Solutions**:

#### Solution A: Already Optimized! ✅
```
- Single worker (prevents memory doubling)
- 2 threads (optimal for 512MB)
- FFmpeg single-threaded
- Aggressive cleanup
- Streaming downloads (no full buffering)
```

#### Solution B: Limit Video Size
```bash
# Render Environment Variables
MAX_FILESIZE=500M  # Limit downloads to 500MB
MAX_VIDEO_DURATION=3600  # 1 hour max
```

#### Solution C: Upgrade Render Plan
```
Free: 512MB RAM → $0/month
Starter: 512MB RAM → $7/month (no improvement)
Standard: 2GB RAM → $25/month (4x memory) ⭐ BETTER
```

---

### Issue 5: Cold Starts (15 Minute Sleep)

**Problem**: Free tier apps sleep after 15 minutes of inactivity. Wake-up takes 30 seconds.

**Symptoms**:
- First request after sleep: 30-second delay
- User sees loading message

**Solutions**:

#### Solution A: Use UptimeRobot (Free) ⭐ **RECOMMENDED**
```
1. Sign up: https://uptimerobot.com (free)
2. Add monitor:
   - URL: https://your-app.onrender.com/health
   - Interval: Every 5 minutes
3. Done! App stays awake 24/7
```

#### Solution B: Accept Cold Starts
- For feature phone users, 30s wait is acceptable
- First user wakes it up for everyone else
- No cost, no setup needed

#### Solution C: Upgrade to Paid Plan
```
Free: Sleeps after 15 min
Paid ($7+/month): No sleep, always on
```

---

## 🔧 Complete Environment Variables Reference

### Required (Auto-set by render.yaml)
```bash
PORT=5000  # Render auto-sets this
SESSION_SECRET=<auto-generated>  # Flask session key
```

### YouTube IP Block Bypass
```bash
USE_IPV6=false  # Set to 'true' to use IPv6 (less blocked)
PROXY_URL=  # Example: http://user:pass@proxy.com:8080
```

### Performance & Rate Limiting
```bash
RATE_LIMIT_BYTES=0  # 0=unlimited, 500000=500KB/s (prevents 429)
MAX_CONCURRENT_DOWNLOADS=1  # Don't change (memory limit)
```

### Storage Management
```bash
FILE_RETENTION_HOURS=6  # Auto-delete files after 6 hours
ENABLE_DISK_SPACE_MONITORING=true  # Monitor /tmp space
DISK_SPACE_THRESHOLD_MB=1500  # Alert when <1.5GB free
```

### Video Limits
```bash
MAX_VIDEO_DURATION=36000  # 10 hours (in seconds)
DOWNLOAD_TIMEOUT=3600  # 1 hour download timeout
CONVERSION_TIMEOUT=21600  # 6 hour conversion timeout
MAX_FILESIZE=2G  # Max download size
```

### Advanced Debugging
```bash
PYTHONUNBUFFERED=1  # See logs in real-time
LOG_LEVEL=INFO  # DEBUG for more verbose logs
```

---

## 📊 Performance Optimization Checklist

### ✅ Already Optimized
- [x] Single worker (512MB RAM limit)
- [x] 2 threads (optimal)
- [x] FFmpeg single-threaded
- [x] Auto-cleanup every 30 min
- [x] Aggressive error handling
- [x] 4 download strategies
- [x] IPv6 support
- [x] Proxy support
- [x] Cookie authentication
- [x] Disk space monitoring
- [x] Emergency cleanup
- [x] Rate limiting support

### 🎯 Optional Optimizations

#### For Heavy Use:
```bash
# More aggressive cleanup
FILE_RETENTION_HOURS=2  # Delete after 2 hours

# Stricter limits
MAX_VIDEO_DURATION=1800  # 30 min max
MAX_FILESIZE=500M  # 500MB max

# Rate limiting (prevent 429)
RATE_LIMIT_BYTES=500000  # 500KB/s
```

#### For Better Reliability:
```bash
# Enable all safeguards
USE_IPV6=true
RATE_LIMIT_BYTES=500000
ENABLE_DISK_SPACE_MONITORING=true

# Upload cookies from /cookies page
```

---

## 🐛 Troubleshooting Decision Tree

```
Download fails?
├─ 403 Forbidden?
│  ├─ Upload cookies (/cookies page) ⭐
│  ├─ Set USE_IPV6=true
│  └─ Configure PROXY_URL
│
├─ 429 Too Many Requests?
│  ├─ Set RATE_LIMIT_BYTES=500000 ⭐
│  ├─ Upload cookies
│  └─ Wait 10-15 minutes
│
├─ Disk space full?
│  ├─ Reduce FILE_RETENTION_HOURS=3
│  ├─ Lower MAX_FILESIZE=500M
│  └─ Check /tmp usage in logs
│
├─ Memory/timeout errors?
│  ├─ Lower MAX_VIDEO_DURATION=3600
│  ├─ Lower MAX_FILESIZE=500M
│  └─ Upgrade to Standard plan ($25/mo)
│
└─ Still failing?
   └─ Check ERROR_GUIDE.md
```

---

## 🔍 Monitoring Your App

### Check Logs
```
1. Go to Render Dashboard
2. Click your service
3. Click "Logs" tab
4. Look for:
   ⚠️ "IP block detected"
   ⚠️ "Low disk space"
   ⚠️ "Rate limit"
   ✅ "Download successful"
```

### Key Log Messages
```
✅ GOOD:
"Download successful with Android TV"
"Conversion complete"
"Disk space: 1800MB free"

⚠️ WARNINGS:
"Possible IP block detected"
"Low disk space: 1200MB free"
"Emergency cleanup: deleted 5 files"

❌ ERRORS:
"YouTube IP BLOCK detected!"
"YouTube bot detection triggered!"
"Server storage full"
```

### Health Check
```bash
# Check if app is running
curl https://your-app.onrender.com/health

# Should return:
{"status": "healthy"}
```

---

## 💡 Best Practices

### For Optimal Performance:
1. ✅ **Upload cookies** (prevents most IP blocks)
2. ✅ **Set RATE_LIMIT_BYTES=500000** (prevents 429)
3. ✅ **Use UptimeRobot** (prevents cold starts)
4. ✅ **Monitor logs regularly**
5. ✅ **Keep FILE_RETENTION_HOURS low** (saves disk space)

### For Maximum Reliability:
```bash
# Set these environment variables:
USE_IPV6=true
RATE_LIMIT_BYTES=500000
FILE_RETENTION_HOURS=3
MAX_FILESIZE=500M
ENABLE_DISK_SPACE_MONITORING=true
```

PLUS upload cookies from /cookies page.

---

## 🚀 Advanced Proxy Setup

### Using Residential Proxies (Best for Production)

**Recommended providers**:
- Bright Data (expensive, reliable)
- Smartproxy (mid-range)
- Oxylabs (enterprise)

**Setup**:
```bash
# Render Environment Variables
PROXY_URL=http://username:password@proxy.provider.com:port
```

### Self-Hosted Proxy (Advanced)

**Requirements**:
- Home server or VPS with unrestricted IP
- WireGuard or SOCKS5 proxy
- Port forwarding

**Setup**:
1. Install WireGuard on home server
2. Configure Render to route through it
3. Set PROXY_URL to your server

**Tutorial**: https://www.wireguard.com/quickstart/

---

## 📈 Scaling Beyond Free Tier

### When to Upgrade:

**Upgrade if you experience**:
- Frequent memory errors (512MB not enough)
- Disk space issues (>10 videos/hour)
- Cold start problems (need always-on)

### Render Plan Comparison:

| Plan | RAM | Price | Best For |
|------|-----|-------|----------|
| **Free** | 512MB | $0 | Light use, testing |
| **Starter** | 512MB | $7/mo | Always-on needed |
| **Standard** | 2GB | $25/mo | Heavy use, long videos |
| **Pro** | 4GB+ | $85+/mo | Production, high traffic |

**Recommendation**: Free tier works great for most users! Upgrade to Standard ($25/mo) only if you process many long videos (>30 min) or get frequent memory errors.

---

## 🎓 Advanced Topics

### Custom yt-dlp Options

Edit `app.py` to add custom yt-dlp options:

```python
# In download_and_convert() function
base_opts = {
    'format': 'worst/best',
    # Add your custom options:
    'geo_bypass': True,
    'age_limit': 18,
    'subtitleslangs': ['en'],
    # etc.
}
```

### Custom FFmpeg Settings

Edit `app.py` conversion command:

```python
convert_cmd = [
    'ffmpeg',
    '-i', temp_video,
    '-vcodec', 'h264',  # Change codec
    '-b:v', '500k',  # Higher bitrate
    # etc.
]
```

See [ADVANCED_TINKERING.md](ADVANCED_TINKERING.md) for detailed examples.

---

## 🔗 Quick Links

- **Render Dashboard**: https://dashboard.render.com
- **Render Docs**: https://render.com/docs
- **yt-dlp GitHub**: https://github.com/yt-dlp/yt-dlp
- **UptimeRobot**: https://uptimerobot.com

---

## ✅ Deployment Checklist

### Initial Deployment:
- [ ] Push code to GitHub
- [ ] Deploy to Render (auto-detects from render.yaml)
- [ ] Wait for build to complete
- [ ] Test with a short video
- [ ] Check logs for errors

### Post-Deployment:
- [ ] Upload cookies (/cookies page)
- [ ] Set up UptimeRobot monitoring
- [ ] Set environment variables (if needed):
  - [ ] USE_IPV6=true
  - [ ] RATE_LIMIT_BYTES=500000
- [ ] Bookmark your app URL
- [ ] Monitor logs for first few days

### If Issues Occur:
- [ ] Check [ERROR_GUIDE.md](ERROR_GUIDE.md)
- [ ] Review Render logs
- [ ] Try solutions in this guide
- [ ] Adjust environment variables

---

**You now have a production-ready YouTube to 3GP converter with enterprise-grade error handling!** 🎉

---

Last Updated: October 27, 2025
