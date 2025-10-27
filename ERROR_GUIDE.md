# 🛠️ Complete Error Guide & Troubleshooting

## 📋 Table of Contents
1. [Common Errors & Solutions](#common-errors--solutions)
2. [YouTube Download Errors](#youtube-download-errors)
3. [Conversion Errors](#conversion-errors)
4. [Render Deployment Errors](#render-deployment-errors)
5. [Memory & Timeout Issues](#memory--timeout-issues)
6. [Prevention Tips](#prevention-tips)

---

## Common Errors & Solutions

### ❌ Error: "All download strategies failed"

**What it means**: The app tried 4 different methods to download the video and all failed.

**Common causes**:
1. YouTube is rate-limiting your IP
2. Video is age-restricted and you don't have cookies
3. Video is private or deleted
4. Geo-blocked content

**Solutions**:
```
✅ Wait 10-15 minutes and try again (rate limit cooldown)
✅ Upload YouTube cookies at /cookies page
✅ Try a different video to test
✅ Check if video is public and available
```

**How to fix permanently**:
- Set up cookies (see COOKIE_SETUP_GUIDE.md)
- Videos should work 90% of the time without cookies

---

### ❌ Error: "Video exceeds maximum duration"

**What it means**: Video is longer than 6 hours.

**Why this limit exists**: Render free tier has 512MB RAM - longer videos cause crashes.

**Solutions**:
```
✅ Try shorter videos (under 3 hours recommended)
✅ Increase limit in render.yaml (risky on free tier):
   MAX_VIDEO_DURATION=43200  # 12 hours (may crash!)
```

**Safe limits by tier**:
- Free tier (512MB): 3 hours max
- Standard (2GB): 6-8 hours
- Pro (4GB): 12+ hours

---

### ❌ Error: "File size exceeds maximum limit"

**What it means**: Downloaded video file is larger than 500MB.

**Solutions**:
```
✅ Video will still download - the limit is just a warning
✅ Increase limit if needed:
   MAX_FILESIZE=1G  # 1GB (risky on free tier)
```

**Note**: Large files may cause memory issues during conversion.

---

### ❌ Error: "Download timeout exceeded"

**What it means**: Download took longer than 1 hour.

**Common causes**:
1. Very large video file
2. Slow network connection
3. YouTube throttling

**Solutions**:
```
✅ Increase timeout in render.yaml:
   DOWNLOAD_TIMEOUT=7200  # 2 hours
✅ Try downloading at off-peak hours
✅ Upload cookies to avoid throttling
```

---

### ❌ Error: "Conversion timeout exceeded"

**What it means**: FFmpeg took longer than 6 hours to convert.

**Common causes**:
1. Very long video
2. Render free tier CPU is slow (0.1 CPU)

**Solutions**:
```
✅ Increase timeout:
   CONVERSION_TIMEOUT=43200  # 12 hours
✅ Try shorter videos
✅ Upgrade to paid tier for faster CPU
```

---

### ❌ Error: "Out of memory" or App Crashes

**What it means**: App used more than 512MB RAM and Render killed it.

**Common causes**:
1. Video too large
2. Multiple conversions at once
3. Memory leak

**Solutions**:
```
✅ IMMEDIATE FIX: Restart the service on Render
✅ Try shorter videos (under 30 minutes to test)
✅ Wait for current conversion to finish before starting another
✅ Clear old files: rm /tmp/downloads/*
```

**Permanent fixes**:
1. Reduce MAX_VIDEO_DURATION to 3 hours
2. Reduce MAX_FILESIZE to 200M
3. Upgrade to Standard plan ($25/month)

---

## YouTube Download Errors

### 🔴 "Sign in to confirm you're not a bot"

**What it means**: YouTube's bot detection triggered.

**Solutions**:
```
✅ Upload cookies from logged-in browser
✅ Wait 15-20 minutes before retrying
✅ App will automatically try different download methods
```

**Prevention**: Set up cookies once, works for 6+ months.

---

### 🔴 "Video unavailable" or "Private video"

**What it means**: Video is deleted, private, or unlisted.

**Solutions**:
```
✅ Check video link in regular browser
✅ Make sure video is public
✅ Try a different video
```

**No fix available** - video must be public.

---

### 🔴 "Age-restricted content"

**What it means**: Video requires YouTube login to view.

**Solutions**:
```
✅ Upload cookies from logged-in YouTube account
✅ Make sure cookies are from account that's 18+
✅ Re-export cookies if they're old (>6 months)
```

---

### 🔴 "Geo-blocked content"

**What it means**: Video not available in your region.

**Solutions**:
```
✅ Upload cookies from browser with VPN
✅ Try different download strategy (Android TV works best)
✅ Some geo-blocks can't be bypassed
```

---

### 🔴 "This video requires payment"

**What it means**: Video is YouTube Premium or rental content.

**Solutions**:
```
❌ NO FIX - Premium content cannot be downloaded
✅ Try free alternative videos
```

---

## Conversion Errors

### ⚠️ "FFmpeg command failed"

**What it means**: FFmpeg couldn't convert the video.

**Common causes**:
1. Corrupted download
2. Unsupported video format
3. FFmpeg crashed

**Solutions**:
```
✅ Re-try conversion (delete and start over)
✅ Try different video
✅ Check logs for specific FFmpeg error
```

**How to check logs**:
1. Go to Render Dashboard
2. Click your service
3. Click "Logs" tab
4. Look for "FFmpeg error:"

---

### ⚠️ "Output file not found after conversion"

**What it means**: Conversion appeared successful but file is missing.

**Common causes**:
1. Disk full
2. Permissions error
3. App restarted during conversion

**Solutions**:
```
✅ Check Render logs for disk space errors
✅ Restart service
✅ Try again with shorter video
```

---

## Render Deployment Errors

### 🚨 "Build failed"

**What it means**: Render couldn't build your app.

**Common causes**:
```
1. build.sh syntax error
2. requirements.txt missing packages
3. Python version mismatch
```

**Solutions**:
```
✅ Check Build Logs on Render for exact error
✅ Verify build.sh is executable:
   chmod +x build.sh
   git add build.sh
   git commit -m "Fix build.sh permissions"
   git push

✅ Check requirements.txt has all packages
✅ Verify Python version is 3.11 in render.yaml
```

---

### 🚨 "Service failed to start"

**What it means**: App built but won't run.

**Common causes**:
```
1. PORT environment variable not set
2. Syntax error in app.py
3. Missing dependencies
```

**Solutions**:
```
✅ Check Runtime Logs on Render
✅ Verify render.yaml has correct startCommand
✅ Test locally first:
   gunicorn --bind=0.0.0.0:5000 app:app
```

---

### 🚨 "App keeps crashing" (Crash Loop)

**What it means**: App starts then crashes repeatedly.

**Common causes**:
```
1. Out of memory
2. Uncaught exception in code
3. Missing environment variables
```

**Solutions**:
```
✅ Check Render logs for error message
✅ Reduce memory usage (lower limits)
✅ Restart service
✅ Check all env vars are set in render.yaml
```

**How to read crash logs**:
1. Render Dashboard → Your Service → Logs
2. Look for last message before crash
3. Search for "Error:", "Exception:", "Killed"

---

### 🚨 "Cannot GET /" or "Service Unavailable"

**What it means**: App deployed but not responding.

**Common causes**:
```
1. App is spinning up (wait 30-60 seconds)
2. Port binding issue
3. App crashed
```

**Solutions**:
```
✅ Wait 1 minute and refresh
✅ Check app is running (green dot on Render)
✅ Check logs for errors
✅ Verify PORT is set to $PORT in startCommand
```

---

## Memory & Timeout Issues

### 💾 "Worker timeout" in logs

**What it means**: Gunicorn worker took too long to respond.

**Solutions**:
```
✅ Increase timeout in render.yaml:
   --timeout=1200  # 20 minutes instead of 10
✅ Normal for long conversions
✅ User should wait on status page
```

---

### 💾 "Worker killed by signal 9 (SIGKILL)"

**What it means**: Out of memory - Render killed the process.

**Solutions**:
```
✅ CRITICAL: Reduce video limits immediately
   MAX_VIDEO_DURATION=10800  # 3 hours
   MAX_FILESIZE=200M
✅ Restart service
✅ Only process one video at a time
```

**This is serious** - fix immediately or app will keep crashing!

---

### 💾 "Temporary failure in name resolution"

**What it means**: Network/DNS issue.

**Solutions**:
```
✅ Usually temporary - retry in 5 minutes
✅ Render might be having network issues
✅ Check Render status: https://status.render.com
```

---

## Prevention Tips

### ✅ Before You Deploy

1. **Test locally first**:
   ```bash
   python app.py
   # Visit http://localhost:5000
   # Try converting a 5-minute video
   ```

2. **Verify all files committed**:
   ```bash
   git status
   git add .
   git commit -m "Your message"
   git push
   ```

3. **Check render.yaml is valid**:
   - No syntax errors
   - All env vars defined
   - Correct Python version

---

### ✅ After Deployment

1. **Verify build succeeded**:
   - Green checkmark on Render
   - "Build completed successfully!" in logs

2. **Test with small video**:
   - Use 2-5 minute YouTube video first
   - Verify download works
   - Verify conversion works
   - Verify file downloads

3. **Set up monitoring**:
   - UptimeRobot for /health endpoint
   - Check logs daily for first week
   - Watch for memory errors

---

### ✅ Regular Maintenance

**Weekly**:
- Check Render logs for errors
- Verify app still works (test video)
- Check cookies expiration if used

**Monthly**:
- Update yt-dlp if downloads failing:
  ```bash
  # Add to requirements.txt
  yt-dlp>=2024.01.01
  ```
- Check Render free tier hours remaining
- Review and clear old logs

**Every 6 Months**:
- Re-export and upload YouTube cookies
- Update dependencies in requirements.txt
- Test with variety of videos

---

## Quick Diagnosis Checklist

When something breaks, check in this order:

```
[ ] 1. Is Render service running? (green dot)
[ ] 2. Check Render logs for errors
[ ] 3. Is video public and available?
[ ] 4. Wait 15 minutes and retry (rate limit)
[ ] 5. Try different video (test if app works)
[ ] 6. Restart Render service
[ ] 7. Check Render status page (outage?)
[ ] 8. Re-upload cookies if needed
[ ] 9. Reduce video limits if memory errors
[ ] 10. Ask for help with logs
```

---

## Getting Help

### What to Include When Asking for Help

1. **Error message** (exact text from screen or logs)
2. **Render logs** (last 50 lines)
3. **What you tried** (list steps already attempted)
4. **Video info** (length, is it public?)
5. **When it started** (was it working before?)

### Where to Check First

1. ✅ **This guide** - Most errors covered here
2. ✅ **Render logs** - Real error details
3. ✅ **RENDER_DEPLOYMENT.md** - Deployment issues
4. ✅ **Render status** - https://status.render.com

---

## Error Codes Reference

| Code | Meaning | Solution |
|------|---------|----------|
| 500 | Internal Server Error | Check Render logs |
| 503 | Service Unavailable | Wait or restart |
| 504 | Gateway Timeout | Normal for long videos |
| 403 | YouTube Forbidden | Upload cookies |
| 404 | Not Found | Check URL |
| Signal 9 | Out of Memory | Reduce limits |
| Signal 15 | Graceful Shutdown | Normal restart |

---

## Still Having Issues?

If you've tried everything in this guide:

1. **Restart Everything**:
   ```
   - Render: Manual Deploy → Clear cache → Deploy
   - Wait 5 minutes
   - Test again
   ```

2. **Start Fresh**:
   ```
   - Delete Render service
   - Create new service
   - Redeploy from scratch
   ```

3. **Verify Free Tier Limits**:
   ```
   - Check you haven't exceeded 750 hours/month
   - Check you haven't hit 100GB bandwidth
   - Verify you're on free plan
   ```

---

## Success Indicators

Your app is working correctly if:

✅ Build completes in 3-5 minutes  
✅ Service shows green dot  
✅ Homepage loads  
✅ Small videos (5 min) convert successfully  
✅ Files download correctly  
✅ No errors in logs during conversion  
✅ Health endpoint returns {"status": "ok"}  

---

**Remember**: Most issues are temporary (rate limits) or configuration (memory limits). This guide covers 95% of problems you'll encounter!

🎯 **Pro Tip**: Bookmark this guide and the Render logs page - you'll need them!
