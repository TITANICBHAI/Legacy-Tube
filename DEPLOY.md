# 🚀 Deploy to Render.com - Quick Guide

## What You Need
- GitHub account
- Render.com account (free, no credit card needed)

## Steps (5 minutes)

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "YouTube to 3GP converter"
git remote add origin https://github.com/YOUR_USERNAME/youtube-3gp-converter.git
git push -u origin main
```

### 2. Deploy on Render
1. Go to https://render.com
2. Sign up/login (use your GitHub account)
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repository
5. Render will auto-detect the `render.yaml` file
6. Click **"Apply"** → **"Create Web Service"**

**That's it!** Render will:
- Install Python 3.11
- Install Python packages (Flask, gunicorn, yt-dlp)
- Install system package (ffmpeg)
- Deploy your Flask app with single worker (prevents race conditions)
- Give you a free URL: `https://youtube-3gp-converter.onrender.com`

### 3. Keep It Awake (Optional)

Render free apps sleep after 15 minutes. To keep it awake:

1. Go to https://cron-job.org (free, no signup needed)
2. Create a new cron job:
   - Name: "Keep YouTube Converter Awake"
   - URL: `https://YOUR_APP_NAME.onrender.com/`
   - Interval: Every 10 minutes
3. Save and enable

Now your app stays awake 24/7!

## Environment Variables (Already Set)

These are automatically configured in `render.yaml`:
- `SESSION_SECRET` - Auto-generated secure key
- `MAX_VIDEO_DURATION` - 6 hours (21600 seconds)
- `DOWNLOAD_TIMEOUT` - 60 minutes (3600 seconds)
- `CONVERSION_TIMEOUT` - 6 hours (21600 seconds)
- `FILE_RETENTION_HOURS` - 6 hours
- `MAX_FILESIZE` - 500MB

## Your App URL

After deployment, your app will be live at:
```
https://YOUR_APP_NAME.onrender.com
```

Works perfectly on:
- Nokia 5310 ✓
- Opera Mini 4.4 ✓
- Any feature phone with internet ✓

## Troubleshooting

**App won't start?**
- Check Render logs in the dashboard
- Make sure `build.sh` has execute permissions

**Conversion fails?**
- Free tier has CPU limits
- Very long videos (4-6 hours) might timeout
- Try shorter videos first

**App is slow?**
- First request after sleep takes 30-60 seconds
- Use cron-job.org to keep it awake

## Costs

**FREE FOREVER** on Render's free tier:
- 750 hours/month (enough for 24/7 uptime)
- Unlimited conversions
- No credit card required
- No time limit

Perfect for personal use! 🎉
