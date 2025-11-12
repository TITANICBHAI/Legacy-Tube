# Deployment Guide - YouTube to 3GP Converter

## Deploy to Render.com (Recommended - Free Tier Available)

### Quick Deploy (5 minutes)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "YouTube to 3GP converter with cookie auth"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up (free)

3. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select your repository
   - Render auto-detects `render.yaml` configuration

4. **Wait for Deployment**
   - Build takes 3-5 minutes
   - Render installs Python, ffmpeg, and dependencies automatically
   - You'll get a URL like: `https://youtube-3gp-converter.onrender.com`

5. **Upload Cookies** (Important!)
   - Visit `https://YOUR-APP.onrender.com/cookies`
   - Upload YouTube cookies (see COOKIE_SETUP_GUIDE.md)
   - This fixes "sign in required" errors on cloud hosting

### Configuration

All settings are in `render.yaml`:
- **Free tier**: Enough for personal use
- **Timeout**: 7200 seconds (2 hours) for long videos
- **Workers**: 2 (handles multiple conversions)
- **Auto-cleanup**: Files deleted after 6 hours

### Environment Variables (Auto-configured)

Already set in `render.yaml`:
- `MAX_VIDEO_DURATION`: 21600 seconds (6 hours)
- `DOWNLOAD_TIMEOUT`: 3600 seconds (1 hour)
- `CONVERSION_TIMEOUT`: 21600 seconds (6 hours)
- `FILE_RETENTION_HOURS`: 6 hours
- `MAX_FILESIZE`: 500 MB
- `SESSION_SECRET`: Auto-generated

### Free Tier Limitations

- **Spin down**: App sleeps after 15 min of inactivity
- **First request**: Takes 30-60 seconds to wake up
- **Build minutes**: 500 hours/month (more than enough)
- **Perfect for**: Personal use, occasional conversions

### Upgrade to Paid ($7/month)

If you need:
- Always-on (no spin down)
- Faster response times
- More concurrent conversions

### Troubleshooting

**"Sign in required" errors after deploy:**
→ Upload cookies at `/cookies` page (cloud IPs are blocked by YouTube)

**Build fails at ffmpeg:**
→ Should auto-install, check build logs on Render dashboard

**Conversion timeout:**
→ Render free tier has 2-hour timeout (enough for 6-hour videos)

**App spins down:**
→ Normal on free tier, upgrade to paid for always-on

### Custom Domain (Optional)

On Render dashboard:
1. Go to your service
2. Click "Settings" → "Custom Domains"
3. Add your domain
4. Update DNS records as shown

---

## Alternative: Deploy to Replit (Current Platform)

Already configured! Just:
1. Upload cookies at `/cookies`
2. Share the Replit URL
3. Keep the Repl running

**Note**: Replit free tier may have limitations for public use.

---

## Alternative: Deploy to Fly.io

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Login: `fly auth login`
3. Create app: `fly launch`
4. Deploy: `fly deploy`

---

## After Deployment Checklist

- [ ] App is accessible at public URL
- [ ] Visit `/cookies` page works
- [ ] Upload YouTube cookies
- [ ] Test converting a short video
- [ ] Verify 3GP download works on feature phone
- [ ] Check logs for any errors

---

## Support

For issues:
1. Check Render build logs
2. Verify cookies are uploaded
3. Test with a short public video first
4. See COOKIE_SETUP_GUIDE.md for cookie troubleshooting
