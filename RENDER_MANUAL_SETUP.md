# Complete Manual Setup Guide for Render

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Method 1: Automatic Deployment (render.yaml)](#method-1-automatic-deployment-renderyaml)
3. [Method 2: Manual Docker Deployment](#method-2-manual-docker-deployment)
4. [Method 3: Manual Native Python Deployment](#method-3-manual-native-python-deployment)
5. [Environment Variables Setup](#environment-variables-setup)
6. [Health Check Configuration](#health-check-configuration)
7. [Testing Your Deployment](#testing-your-deployment)
8. [Troubleshooting](#troubleshooting)
9. [Manual Tinkering & Advanced Options](#manual-tinkering--advanced-options)

---

## Prerequisites

### Step 1: Create GitHub Account (if you don't have one)
1. Go to https://github.com
2. Click "Sign up"
3. Enter your email, password, and username
4. Verify your email address
5. Complete the setup wizard

### Step 2: Push Your Code to GitHub

**Option A: Using Git Command Line**
```bash
# Navigate to your project directory
cd /path/to/your/project

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit your changes
git commit -m "Initial commit - YouTube to 3GP converter"

# Create repository on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git push -u origin main
```

**Option B: Using GitHub Desktop**
1. Download GitHub Desktop: https://desktop.github.com
2. Install and sign in
3. Click "File" → "Add Local Repository"
4. Select your project folder
5. Click "Publish repository"
6. Choose public or private
7. Click "Publish"

**Option C: Using Replit's Git Integration**
1. Open your Replit project
2. Click on "Version Control" icon (left sidebar)
3. Click "Initialize Git repository"
4. Commit your changes with a message
5. Click "Create a GitHub repository"
6. Follow the prompts to connect and push

### Step 3: Create Render Account
1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with:
   - **Option A**: GitHub account (recommended - easiest integration)
   - **Option B**: GitLab account
   - **Option C**: Email and password
4. Verify your email if using email signup
5. Complete profile setup

---

## Method 1: Automatic Deployment (render.yaml)

This is the **easiest and recommended** method. Your project already has `render.yaml` configured.

### Step 1: Connect GitHub to Render

1. **Log into Render Dashboard**
   - Go to https://dashboard.render.com
   - You should see your dashboard

2. **Authorize GitHub Access**
   - If this is your first time, Render will ask to connect to GitHub
   - Click "Connect GitHub"
   - A popup will open asking for permissions
   - Click "Authorize Render"
   - You may need to enter your GitHub password

3. **Select Repository Access**
   - Choose "All repositories" OR
   - Choose "Only select repositories" and pick your project
   - Click "Install & Authorize"

### Step 2: Create Web Service from Dashboard

1. **Click "New +"** (top right of dashboard)
2. **Select "Web Service"**
3. **Choose Your Repository**
   - You'll see a list of your GitHub repositories
   - Find and click on your YouTube to 3GP converter repo
   - Click "Connect"

### Step 3: Configure Service (Auto-detected)

Render will auto-detect your `render.yaml` file and fill in these settings:

**Review these settings** (should be auto-filled):

| Setting | Value | Notes |
|---------|-------|-------|
| **Name** | `youtube-3gp-converter` | Auto-detected from render.yaml |
| **Region** | `Oregon (US West)` | Auto-detected (change if needed) |
| **Branch** | `main` | Change if your branch is named differently |
| **Environment** | `Python` | Auto-detected |
| **Build Command** | `bash build.sh` | Auto-detected from render.yaml |
| **Start Command** | `gunicorn --bind=0.0.0.0:$PORT --workers=1 --threads=2 --timeout=600 --max-requests=50 --max-requests-jitter=10 --worker-class=sync --worker-tmp-dir=/dev/shm app:app` | Auto-detected |
| **Plan** | `Free` | ✅ Select this! |

### Step 4: Environment Variables (Auto-configured)

Scroll down to **Environment Variables** section. These should be auto-filled from render.yaml:

| Variable | Value | Auto-Set |
|----------|-------|----------|
| `PYTHON_VERSION` | `3.11.0` | ✅ Yes |
| `MAX_VIDEO_DURATION` | `21600` | ✅ Yes |
| `DOWNLOAD_TIMEOUT` | `3600` | ✅ Yes |
| `CONVERSION_TIMEOUT` | `21600` | ✅ Yes |
| `FILE_RETENTION_HOURS` | `6` | ✅ Yes |
| `MAX_FILESIZE` | `500M` | ✅ Yes |
| `SESSION_SECRET` | (auto-generated) | ✅ Yes |

**No manual input needed** - everything is configured!

### Step 5: Deploy!

1. **Scroll to bottom**
2. **Click "Create Web Service"** (big blue button)
3. **Wait for deployment** (5-10 minutes)

**What happens during deployment:**
```
[Build Process - ~5-7 minutes]
1. Cloning repository from GitHub...
2. Detecting environment: Python
3. Running build.sh...
4. Installing Python dependencies...
5. Installing ffmpeg and yt-dlp...
6. Creating required folders...
7. Build completed ✓

[Deploy Process - ~1-2 minutes]
8. Starting gunicorn server...
9. Health check: Waiting for /health endpoint...
10. Health check: Success ✓
11. Your service is live! 🚀
```

### Step 6: Verify Deployment

Once deployment completes, you'll see:
- **Green "Live" badge** at the top
- **Your app URL**: `https://youtube-3gp-converter.onrender.com`

**Test it:**
1. Click on the URL
2. You should see the YouTube to 3GP converter homepage
3. Try converting a short video (1-2 minutes)

---

## Method 2: Manual Docker Deployment

If you want to use Docker instead of native Python deployment.

### Step 1: Connect Repository (same as Method 1)
Follow "Method 1: Step 1" to connect GitHub to Render.

### Step 2: Create Web Service with Docker

1. **Click "New +"** → **"Web Service"**
2. **Select your repository** → **Click "Connect"**

### Step 3: Manual Docker Configuration

**Fill in manually:**

| Setting | Value to Enter |
|---------|----------------|
| **Name** | `youtube-3gp-converter` (or your choice) |
| **Region** | `Oregon (US West)` (or closest to you) |
| **Branch** | `main` (or your default branch) |
| **Runtime** | **Select "Docker"** ⚠️ Important! |
| **Dockerfile Path** | `Dockerfile` (default, leave as is) |
| **Docker Build Context Directory** | `.` (root directory) |
| **Plan** | **Free** |

### Step 4: Docker-Specific Settings

**Advanced Settings** (click to expand):

| Setting | Value | Why |
|---------|-------|-----|
| **Docker Command** | (leave empty) | Uses CMD from Dockerfile |
| **Health Check Path** | `/health` | Monitors app status |
| **Port** | `5000` | App listens on 5000 |

### Step 5: Environment Variables for Docker

**Click "Add Environment Variable"** for each:

| Key | Value |
|-----|-------|
| `PORT` | `5000` |
| `SESSION_SECRET` | Click "Generate" button |
| `MAX_VIDEO_DURATION` | `21600` |
| `DOWNLOAD_TIMEOUT` | `3600` |
| `CONVERSION_TIMEOUT` | `21600` |
| `FILE_RETENTION_HOURS` | `6` |
| `MAX_FILESIZE` | `500M` |

### Step 6: Deploy Docker Container

1. **Review all settings**
2. **Click "Create Web Service"**
3. **Wait 5-10 minutes** for Docker build

**Docker build process:**
```
1. Building Docker image...
   - Stage 1: Installing build dependencies
   - Stage 2: Creating runtime image
   - Installing ffmpeg and yt-dlp
2. Pushing image to Render registry...
3. Starting container...
4. Health check in progress...
5. Container is live! ✓
```

---

## Method 3: Manual Native Python Deployment

For those who want full manual control without render.yaml.

### Step 1: Connect Repository
Same as Method 1: Step 1.

### Step 2: Create Web Service Manually

1. **Click "New +"** → **"Web Service"**
2. **Connect your repository**
3. **Select "I want to configure my service manually"** (if prompted)

### Step 3: Basic Configuration

**Fill in each field manually:**

#### General Settings
```
Name: youtube-3gp-converter
Region: Oregon (US West)
Branch: main
Root Directory: (leave empty for root)
```

#### Runtime Settings
```
Runtime: Python 3
Python Version: 3.11.0
```

### Step 4: Build & Start Commands

**Build Command:**
```bash
bash build.sh
```

**Start Command:**
```bash
gunicorn --bind=0.0.0.0:$PORT --workers=1 --threads=2 --timeout=600 --max-requests=50 --max-requests-jitter=10 --worker-class=sync --worker-tmp-dir=/dev/shm app:app
```

**Breakdown of start command:**
- `--bind=0.0.0.0:$PORT` - Listen on all interfaces, port from Render
- `--workers=1` - Single worker (512MB RAM constraint)
- `--threads=2` - 2 threads per worker for concurrency
- `--timeout=600` - 10 minute timeout for long conversions
- `--max-requests=50` - Restart worker after 50 requests (prevent memory leaks)
- `--max-requests-jitter=10` - Random jitter to prevent all workers restarting at once
- `--worker-class=sync` - Synchronous worker class
- `--worker-tmp-dir=/dev/shm` - Use RAM for temp files (faster)
- `app:app` - Run the Flask app

### Step 5: Plan Selection

**Select Plan:**
```
Plan: Free
Instance Type: Free
```

**Free Tier Specs:**
- RAM: 512 MB
- CPU: Shared
- Bandwidth: 100 GB/month
- Hours: 750 hours/month
- Spin down: After 15 minutes of inactivity

### Step 6: Environment Variables

**Click "Add Environment Variable"** button for each:

1. **PYTHON_VERSION**
   - Key: `PYTHON_VERSION`
   - Value: `3.11.0`

2. **SESSION_SECRET** (Important!)
   - Key: `SESSION_SECRET`
   - Click "Generate" button (creates secure random string)
   - Or enter your own: at least 32 random characters

3. **MAX_VIDEO_DURATION**
   - Key: `MAX_VIDEO_DURATION`
   - Value: `21600`
   - Meaning: 6 hours in seconds

4. **DOWNLOAD_TIMEOUT**
   - Key: `DOWNLOAD_TIMEOUT`
   - Value: `3600`
   - Meaning: 1 hour timeout for downloads

5. **CONVERSION_TIMEOUT**
   - Key: `CONVERSION_TIMEOUT`
   - Value: `21600`
   - Meaning: 6 hours base timeout for conversions

6. **FILE_RETENTION_HOURS**
   - Key: `FILE_RETENTION_HOURS`
   - Value: `6`
   - Meaning: Auto-delete files after 6 hours

7. **MAX_FILESIZE**
   - Key: `MAX_FILESIZE`
   - Value: `500M`
   - Meaning: Maximum 500MB video download

### Step 7: Advanced Settings

**Click "Advanced"** to expand:

#### Health Check
```
Health Check Path: /health
```

#### Auto-Deploy
```
Auto-Deploy: Yes (recommended)
```
This auto-deploys when you push to GitHub.

#### Pull Request Previews
```
Pull Request Previews: No (optional, uses resources)
```

### Step 8: Create & Deploy

1. **Review all settings carefully**
2. **Click "Create Web Service"**
3. **Monitor deployment logs** (appears automatically)

---

## Environment Variables Setup

### Required Variables

| Variable | Required? | Default | Description |
|----------|-----------|---------|-------------|
| `SESSION_SECRET` | ✅ **YES** | None | Flask session encryption key |
| `PYTHON_VERSION` | No | 3.11.0 | Python version |
| `MAX_VIDEO_DURATION` | No | 21600 | Max video length (seconds) |
| `DOWNLOAD_TIMEOUT` | No | 3600 | Download timeout (seconds) |
| `CONVERSION_TIMEOUT` | No | 21600 | Conversion timeout (seconds) |
| `FILE_RETENTION_HOURS` | No | 6 | Auto-delete after X hours |
| `MAX_FILESIZE` | No | 500M | Max download size |

### How to Add/Edit Environment Variables

#### During Initial Setup
1. Scroll to "Environment Variables" section
2. Click "Add Environment Variable"
3. Enter Key and Value
4. Click "Add" or press Enter
5. Repeat for each variable

#### After Deployment
1. Go to your service dashboard
2. Click "Environment" tab (left sidebar)
3. Click "Add Environment Variable"
4. Enter Key and Value
5. Click "Save Changes"
6. **Service will auto-redeploy** with new variables

### Generating Secure SESSION_SECRET

**Option 1: Use Render's Generator (Easiest)**
1. When adding `SESSION_SECRET` variable
2. Click "Generate" button
3. Render creates a secure random string
4. Click "Save"

**Option 2: Generate Your Own (Python)**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Copy the output and use as SESSION_SECRET value.

**Option 3: Generate Your Own (OpenSSL)**
```bash
openssl rand -hex 32
```

**Option 4: Online Generator**
- Visit: https://randomkeygen.com/
- Use a "Fort Knox Password" (256-bit)
- Copy and paste

---

## Health Check Configuration

### What is a Health Check?

Render periodically pings your app to ensure it's running. If health check fails, Render restarts your service.

### Setting Up Health Check

#### Method A: During Service Creation
1. In "Advanced Settings" section
2. Find "Health Check Path"
3. Enter: `/health`
4. Leave other defaults:
   - Protocol: HTTP
   - Port: (blank - uses service port)

#### Method B: After Deployment
1. Go to service dashboard
2. Click "Settings" tab
3. Scroll to "Health & Alerts"
4. Click "Edit"
5. Enter Health Check Path: `/health`
6. Click "Save Changes"

### Health Check Settings Explained

| Setting | Recommended Value | What It Means |
|---------|-------------------|---------------|
| **Health Check Path** | `/health` | URL endpoint to check |
| **Protocol** | `HTTP` | Use HTTP (not HTTPS internally) |
| **Port** | (blank) | Uses default service port |
| **Initial Delay** | `30` seconds | Wait 30s before first check |
| **Interval** | `30` seconds | Check every 30 seconds |
| **Timeout** | `10` seconds | Fail if no response in 10s |
| **Unhealthy Threshold** | `3` | Restart after 3 failed checks |

### Testing Your Health Check

**From Your Browser:**
```
https://your-app-name.onrender.com/health
```

**Expected Response:**
```json
{
  "service": "youtube-3gp-converter",
  "status": "ok"
}
```

**From Command Line:**
```bash
curl https://your-app-name.onrender.com/health
```

**If Health Check Fails:**
1. Check deployment logs for errors
2. Verify `/health` route exists in app.py
3. Ensure service is actually running
4. Check if port is correct (should be 5000)

---

## Testing Your Deployment

### Step 1: Access Your App

1. **Find Your URL:**
   - On service dashboard, top right
   - Format: `https://your-service-name.onrender.com`
   - Click to open in new tab

2. **First Load:**
   - If service is asleep (free tier), first load takes 30-60 seconds
   - You'll see "This service is waking up..."
   - Wait patiently - this is normal!

### Step 2: Test Homepage

**What to check:**
- [ ] Page loads without errors
- [ ] You see "YouTube to 3GP" header
- [ ] URL input box is present
- [ ] "Convert to 3GP" button works
- [ ] Cookie status shows at bottom

### Step 3: Test Video Conversion

**Use a short test video first!**

**Good test videos:**
1. Find a 1-2 minute public YouTube video
2. Copy the URL (e.g., `https://www.youtube.com/watch?v=dQw4w9WgXcQ`)
3. Paste into your app
4. Click "Convert to 3GP"

**What happens:**
```
1. Redirects to status page
2. Shows "Downloading video from YouTube..."
3. May show "Retrying with [Strategy] client..." (normal!)
4. Shows "Converting to 3GP format..."
5. Shows "Conversion complete!"
6. Download button appears
```

**Expected times (Render free tier):**
- 1-2 min video: ~3-5 minutes total
- 5 min video: ~5-8 minutes total
- 10 min video: ~10-15 minutes total

### Step 4: Test Download

1. Click "Download 3GP File" button
2. File should download to your computer
3. Check file:
   - Extension: `.3gp`
   - Size: Should be much smaller than original
   - Plays in VLC or media player

### Step 5: Test Cookie Upload (Optional)

1. Go to `/cookies` page
2. Try uploading a cookie file
3. Should show validation status
4. Can delete cookies from same page

### Step 6: Monitor Logs

**View Real-Time Logs:**
1. Go to service dashboard
2. Click "Logs" tab (left sidebar)
3. Watch for errors or warnings

**Good log messages:**
```
Conversion complete! Duration: 2.3 min, File size: 3.45 MB
Cleanup completed: Deleted 1 old files
Health check succeeded
```

**Bad log messages to watch for:**
```
Error: Download failed
Out of memory
Connection timeout
Health check failed
```

---

## Troubleshooting

### Problem 1: Build Fails

**Error: "Could not find ffmpeg"**

**Solution:**
1. Check `build.sh` is in repository
2. Ensure build command is: `bash build.sh`
3. Check build logs for apt-get errors
4. Try manual redeploy: Dashboard → "Manual Deploy" → "Deploy latest commit"

**Error: "No module named 'flask'"**

**Solution:**
1. Check `requirements.txt` exists
2. Verify `pip install -r requirements.txt` runs in build.sh
3. Check Python version is correct (3.11.0)

### Problem 2: Service Won't Start

**Error: "Application failed to respond to health check"**

**Solution:**
1. Check start command has correct port binding: `--bind=0.0.0.0:$PORT`
2. Verify app.py runs: `if __name__ == '__main__': app.run(host='0.0.0.0', port=port)`
3. Test health endpoint locally first
4. Check logs for Python errors

**Error: "Worker timeout"**

**Solution:**
1. Increase gunicorn timeout: `--timeout=900` (15 minutes)
2. Check if video conversion is hanging
3. Try shorter test video first

### Problem 3: Conversions Fail

**Error: "Download failed: All strategies failed"**

**Solution:**
1. Upload cookies from `/cookies` page
2. Try different YouTube video
3. Check if video is public and not geo-restricted
4. Wait 10 minutes if rate-limited

**Error: "Video exceeds 6-hour limit"**

**Solution:**
1. Try shorter video
2. Or increase `MAX_VIDEO_DURATION` env var
3. Redeploy after changing env var

### Problem 4: Out of Memory

**Error: "Worker killed (signal 9)" or "Out of memory"**

**Solution:**
1. This is 512MB limit hit
2. Try shorter videos
3. Don't convert multiple videos simultaneously
4. Ensure `--workers=1` (not higher)
5. Check `--worker-tmp-dir=/dev/shm` is set

### Problem 5: Service Keeps Spinning Down

**Issue:** Service sleeps after 15 minutes

**This is normal on free tier!**

**Workarounds:**
1. None - this is how free tier works
2. Upgrade to paid plan ($7/month) for always-on
3. Accept 30-60 second wake-up time
4. Use external monitoring (pings every 14 min, but check Render TOS)

### Problem 6: Can't Access Logs

**Solution:**
1. Dashboard → Your Service → "Logs" tab
2. If empty, try:
   - Trigger an action (convert video)
   - Refresh page
   - Check "Events" tab for deployment info

---

## Manual Tinkering & Advanced Options

### Customizing Worker Settings

**Location:** Dashboard → Settings → Start Command

**Single worker, more threads:**
```bash
gunicorn --workers=1 --threads=4 ...
```
Use: More concurrent requests, same memory

**Multiple workers (risky on 512MB):**
```bash
gunicorn --workers=2 --threads=2 ...
```
Use: More processing power, but might OOM

### Adjusting Timeouts

**Short timeout (faster failures):**
```bash
gunicorn --timeout=300 ...
```
Use: If conversions should fail fast

**Long timeout (for very long videos):**
```bash
gunicorn --timeout=1800 ...
```
Use: For 1+ hour videos

### Changing Video Limits

**Allow longer videos:**
```
MAX_VIDEO_DURATION=36000  # 10 hours
```

**Larger file sizes:**
```
MAX_FILESIZE=1G  # 1 gigabyte
```

**Shorter retention:**
```
FILE_RETENTION_HOURS=2  # Delete after 2 hours
```

### Custom Build Commands

**Add extra dependencies:**

Edit `build.sh`:
```bash
#!/usr/bin/env bash
set -o errexit

pip install --no-cache-dir -r requirements.txt
apt-get update -qq
apt-get install -y -qq ffmpeg yt-dlp curl htop

# Custom setup
mkdir -p /tmp/custom_folder
echo "Custom build completed!"
```

### Using Different Regions

**Available Regions:**
- `Oregon (US West)` - Default, good for US/Canada
- `Ohio (US East)` - Good for US East Coast/Europe
- `Frankfurt (EU Central)` - Good for Europe
- `Singapore (Southeast Asia)` - Good for Asia

**To Change:**
1. Settings → General → Region
2. Select new region
3. Click "Save Changes"
4. Service redeploys to new region

### Enabling Auto-Deploy

**What it does:** Automatically deploys when you push to GitHub

**Enable:**
1. Settings → General
2. Find "Auto-Deploy"
3. Toggle **ON**
4. Select branch (usually `main`)
5. Click "Save"

Now every `git push` triggers deployment!

### Manual Deployments

**Deploy specific commit:**
1. Dashboard → "Manual Deploy"
2. Select branch
3. Enter commit SHA (optional, leave blank for latest)
4. Click "Deploy"

**Clear cache and rebuild:**
1. Manual Deploy
2. Check "Clear build cache"
3. Click "Deploy"

### Setting Up Notifications

**Get notified on deployment events:**

1. Settings → Notifications
2. Choose notification type:
   - Email
   - Slack
   - Discord webhook
3. Select events:
   - Deploy started
   - Deploy succeeded
   - Deploy failed
   - Service suspended
4. Click "Add Notification"

### Viewing Metrics

**Free tier metrics:**
1. Dashboard → Metrics tab
2. View:
   - Request count
   - Response times
   - Error rates
   - Bandwidth usage
   - Memory usage

**Note:** Detailed metrics only on paid plans

### Connecting Custom Domain

**Free tier: Only *.onrender.com subdomain**

**Paid plans can use custom domain:**
1. Buy domain (e.g., GoDaddy, Namecheap)
2. Dashboard → Settings → Custom Domain
3. Click "Add Custom Domain"
4. Enter domain: `converter.yourdomain.com`
5. Add CNAME record to your DNS:
   ```
   CNAME converter yourdomain.onrender.com
   ```
6. Wait for SSL certificate (automatic)

### Upgrading to Paid Plan

**If you need:**
- Always-on (no spin-down)
- More memory (up to 16GB)
- Faster CPU
- Custom domain
- Better support

**How to upgrade:**
1. Dashboard → Settings → Plan
2. Click "Change Plan"
3. Select "Starter" ($7/month) or higher
4. Enter payment info
5. Click "Upgrade"

**Plan Comparison:**

| Feature | Free | Starter ($7/mo) |
|---------|------|-----------------|
| RAM | 512 MB | 512 MB |
| Spin-down | 15 min | Never |
| Hours | 750/mo | Unlimited |
| Custom domain | ❌ | ✅ |
| Support | Community | Email |

### Shell Access (Paid Plans Only)

**Access your container shell:**
1. Upgrade to Starter plan
2. Dashboard → Shell tab
3. Opens interactive terminal
4. Run commands:
   ```bash
   ls -la /tmp/downloads
   ffmpeg -version
   yt-dlp --version
   ps aux
   ```

### Database Options (Future)

**If you want persistent storage:**

1. Add PostgreSQL:
   - New → PostgreSQL Database
   - Free tier available
   - Get connection URL
   - Add to environment variables

2. Modify app to use database instead of JSON file

### Monitoring & Alerting

**Set up alerts:**
1. Settings → Alerts
2. Configure:
   - Memory > 90%
   - CPU > 90%
   - Health check fails
3. Choose notification channel
4. Click "Create Alert"

---

## Quick Reference

### Useful URLs
```
Dashboard: https://dashboard.render.com
Your App: https://your-service-name.onrender.com
Health Check: https://your-service-name.onrender.com/health
Cookies Page: https://your-service-name.onrender.com/cookies
Logs: Dashboard → Your Service → Logs
```

### Key Commands

**Local Testing:**
```bash
# Test build script
bash build.sh

# Test app locally
python app.py

# Test with gunicorn
gunicorn --bind=0.0.0.0:5000 --workers=1 app:app
```

**Git Commands:**
```bash
# Check status
git status

# Add changes
git add .

# Commit
git commit -m "Your message"

# Push (triggers auto-deploy if enabled)
git push

# Force redeploy (same code)
git commit --allow-empty -m "Force redeploy"
git push
```

### Environment Variable Quick Add

Copy-paste these into Render's "Add from .env" option:
```env
PYTHON_VERSION=3.11.0
MAX_VIDEO_DURATION=21600
DOWNLOAD_TIMEOUT=3600
CONVERSION_TIMEOUT=21600
FILE_RETENTION_HOURS=6
MAX_FILESIZE=500M
```

(SESSION_SECRET should be generated separately)

---

## Final Checklist

Before going live:
- [ ] Repository pushed to GitHub
- [ ] render.yaml file present
- [ ] All environment variables set
- [ ] Health check path configured: `/health`
- [ ] Test video conversion successful
- [ ] Logs show no errors
- [ ] Health check shows "ok"
- [ ] Download works
- [ ] Cookie upload tested (optional)
- [ ] Bookmark your app URL
- [ ] Set up notifications (optional)

**Your app is ready! 🚀**

---

## Getting Help

**Render Support:**
- Free tier: Community forum
- Paid plans: Email support
- Status page: https://status.render.com

**Project Issues:**
- Check logs first (Dashboard → Logs)
- Review this troubleshooting guide
- Check GitHub issues (if public repo)

**Community:**
- Render Community: https://community.render.com
- Stack Overflow: Tag `render.com`
