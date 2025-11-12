# Render Deployment Guide - Free Tier Optimized

## Overview
This guide helps you deploy the YouTube to 3GP converter on Render's **free tier** with optimizations for memory and CPU constraints.

## Free Tier Specifications
- **Memory**: 512 MB RAM
- **CPU**: Shared CPU (0.1 CPU)
- **Disk**: Ephemeral storage (resets on restart)
- **Bandwidth**: 100 GB/month
- **Spin down**: After 15 minutes of inactivity
- **Monthly hours**: 750 hours free

## Optimizations Applied

### 1. Memory Management
- **Single worker**: `--workers=1` instead of multiple workers
- **Worker temp directory**: Uses `/dev/shm` (RAM) for better performance
- **Max requests**: Restarts worker after 50 requests to prevent memory leaks
- **HTTP chunk size**: 10MB chunks to reduce memory usage
- **No cache pip install**: Saves disk space during build

### 2. Process Management
- **Threads**: 2 threads per worker for concurrent requests
- **Timeout**: 600 seconds (10 minutes) to prevent hanging processes
- **Auto-restart**: Workers restart after processing requests
- **Fragment control**: Downloads 1 fragment at a time (less memory)

### 3. Download Strategies
The app tries **4 different strategies** automatically:
1. **Android TV** - Best for bypassing restrictions
2. **iOS** - Good for geo-blocked content
3. **Android Mobile** - General purpose
4. **Web Embedded** - Fallback option

If one fails, it automatically tries the next with progressive delays.

## Deployment Steps

### Step 1: Prepare Your Repository
1. Make sure all files are committed to your Git repository
2. Push to GitHub, GitLab, or Bitbucket

### Step 2: Create Render Account
1. Go to https://render.com
2. Sign up for free account (no credit card required)
3. Connect your Git provider

### Step 3: Create New Web Service
1. Click "New +" → "Web Service"
2. Connect your repository
3. Render will auto-detect the `render.yaml` configuration

### Step 4: Configure (Auto-detected from render.yaml)
- **Name**: youtube-3gp-converter
- **Environment**: Python
- **Region**: Oregon (or closest to you)
- **Branch**: main (or your branch)
- **Build Command**: bash build.sh
- **Start Command**: (auto-configured with gunicorn)

### Step 5: Environment Variables (Optional)
All variables are pre-configured in `render.yaml`, but you can override:
- `MAX_VIDEO_DURATION`: 21600 (6 hours in seconds)
- `DOWNLOAD_TIMEOUT`: 3600 (1 hour in seconds)
- `FILE_RETENTION_HOURS`: 6
- `MAX_FILESIZE`: 500M
- `SESSION_SECRET`: (auto-generated)

### Step 6: Deploy
1. Click "Create Web Service"
2. Wait 5-10 minutes for initial build
3. Watch the deployment logs
4. Your app will be live at `https://youtube-3gp-converter.onrender.com`

## Post-Deployment

### Testing Without Cookies
1. Visit your app URL
2. Try converting a public YouTube video
3. The app will try 4 different strategies automatically
4. Most public videos should work without cookies!

### If Videos Still Fail
1. Go to `/cookies` page on your app
2. Upload YouTube cookies (see COOKIE_SETUP_GUIDE.md)
3. This helps with age-restricted or geo-blocked content

## Free Tier Limitations & Workarounds

### ⚠️ Spin Down After Inactivity
**Issue**: App sleeps after 15 minutes of no requests
**Impact**: First request after sleep takes 30-60 seconds to wake up
**Workaround**: 
- Accept the delay (free tier limitation)
- Upgrade to paid plan ($7/month for always-on)

### ⚠️ Memory Constraints
**Issue**: Only 512 MB RAM available
**Impact**: Can't process very long videos simultaneously
**Workaround**: 
- App configured for 1 worker (prevents out-of-memory)
- Videos processed one at a time
- Files auto-delete after 6 hours

### ⚠️ Storage is Ephemeral
**Issue**: `/tmp` storage resets on restart
**Impact**: Downloaded files lost on restart
**Workaround**: 
- App designed for this (temporary storage only)
- Files auto-delete anyway (6 hour retention)
- Download videos immediately after conversion

### ⚠️ Monthly Bandwidth Limit
**Issue**: 100 GB/month bandwidth on free tier
**Impact**: Can serve ~200-300 converted videos/month
**Workaround**: 
- For personal use, this is plenty
- Upgrade to paid plan if needed

## Monitoring Your App

### Check Logs
1. Go to Render Dashboard → Your Service
2. Click "Logs" tab
3. Monitor for errors or issues

### Check Status
- Green dot = Running
- Yellow dot = Deploying
- Red dot = Failed

### Common Log Messages
- `Build completed successfully!` = Good build
- `Retrying with [Strategy] client...` = Normal (trying fallbacks)
- `Conversion complete!` = Successful conversion

## Troubleshooting

### Build Fails
**Check**: Build logs for specific errors
**Common causes**:
- Missing dependencies (check build.sh)
- Python version mismatch
- Network timeout during pip install

**Fix**: 
```bash
# Ensure build.sh is executable
chmod +x build.sh
```

### App Crashes
**Check**: Runtime logs for errors
**Common causes**:
- Out of memory (video too large)
- Timeout (video too long)
- YouTube blocking

**Fix**: 
- Try shorter videos
- Upload cookies for authentication
- Wait a few minutes and retry

### Downloads Fail Even With Strategies
**Error**: "All download strategies failed"
**Causes**:
- YouTube rate limiting your IP
- Age-restricted content
- Geo-blocked content

**Fix**:
1. Upload cookies from `/cookies` page
2. Wait 10-15 minutes (rate limit cooldown)
3. Try different video

### Slow First Request
**Normal**: Free tier spins down after inactivity
**Wait time**: 30-60 seconds for wake up
**Not a bug**: This is how free tier works

## Performance Tips

1. **Convert shorter videos first** - Test with 5-10 minute videos
2. **One at a time** - Don't start multiple conversions simultaneously
3. **Download immediately** - Files auto-delete after 6 hours
4. **Use during low-traffic hours** - Better performance when fewer users
5. **Be patient** - Free tier is slower than paid

## Upgrade Options

If you need better performance:

### Render Starter ($7/month)
- Always-on (no spin down)
- 512 MB RAM (same as free)
- Better CPU allocation
- No monthly hour limit

### Render Standard ($25/month)
- 2 GB RAM (4x more)
- Dedicated CPU
- Can handle multiple conversions
- Faster processing

**Recommendation**: Free tier is fine for personal use. Only upgrade if you use it frequently and can't tolerate spin-down delays.

## Cost Comparison

| Platform | Free Tier | Always-On Cost | Notes |
|----------|-----------|----------------|-------|
| **Render** | ✅ Yes (with spin-down) | $7/month | Best free option |
| Railway | ❌ No | $5-20/month | No free tier anymore |
| Fly.io | ✅ Limited | Pay-as-you-go | Complex pricing |
| Replit | ✅ Yes | $7/month | Great for development |

## Success Checklist

- [ ] Repository pushed to Git
- [ ] Render account created
- [ ] Web service deployed
- [ ] Build logs show "Build completed successfully!"
- [ ] App accessible at render.com URL
- [ ] Tested with a public YouTube video
- [ ] Conversion works without cookies
- [ ] Files download correctly

## Support

If you encounter issues:
1. Check Render deployment logs
2. Review error messages in browser
3. Try uploading cookies if downloads fail
4. Verify YouTube video is public and not restricted
5. Wait 10-15 minutes if rate limited

**Note**: This app is optimized for Render's free tier constraints and should work reliably for personal use without requiring cookies for most public YouTube videos.
