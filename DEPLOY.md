# 🚀 Complete Deployment Guide for Render.com

**Estimated Total Time: 10-15 minutes**

This guide will walk you through every single step to deploy your YouTube to 3GP converter from Replit to Render.com with detailed explanations.

---

## 📋 What You'll Need

### Required (Free)
1. **GitHub Account** - To store your code
   - Sign up at: https://github.com/signup
   - Completely free forever
   
2. **Render.com Account** - To host your app
   - Sign up at: https://render.com/register
   - Free tier requires NO credit card
   - 750 hours/month free (enough for 24/7 hosting)

### Optional (For 24/7 Uptime)
3. **Cron-job.org Account** - To keep your app awake
   - Sign up at: https://cron-job.org/en/signup/
   - Completely free

---

## 🔧 Part 1: Upload Your Code to GitHub (5-7 minutes)

GitHub is like Dropbox for code - it stores your project files online so Render can access them.

### Step 1.1: Create a GitHub Repository

1. **Go to GitHub**: Open https://github.com in your browser
2. **Sign in** to your GitHub account (or create one if needed)
3. **Click the "+" icon** in the top-right corner of the page
4. **Select "New repository"** from the dropdown menu

### Step 1.2: Configure Your Repository

You'll see a form with several fields:

1. **Repository name**: 
   - Enter: `youtube-3gp-converter` (or any name you prefer)
   - This will be part of your GitHub URL
   - Example: `github.com/YOUR_USERNAME/youtube-3gp-converter`

2. **Description** (optional):
   - Enter: "Convert YouTube videos to 3GP format for feature phones"
   - This helps you remember what the project does

3. **Public or Private**:
   - Select: **Public** (required for Render free tier)
   - Private repos need paid Render plans

4. **Initialize repository**:
   - ❌ **DO NOT** check "Add a README file"
   - ❌ **DO NOT** add .gitignore
   - ❌ **DO NOT** choose a license
   - (We already have these files in the project)

5. **Click "Create repository"**

### Step 1.3: Note Your Repository URL

After creation, you'll see a page with repository URLs. Copy the **HTTPS URL** which looks like:
```
https://github.com/YOUR_USERNAME/youtube-3gp-converter.git
```

**Keep this URL handy** - you'll need it in the next step!

### Step 1.4: Upload Your Code from Replit

Now we'll push your code from Replit to GitHub.

**Option A: Using Replit's GitHub Integration (Easiest)**
1. In Replit, open the **"Version control"** panel (left sidebar, clock icon)
2. Click **"Create a Git repo"**
3. Enter commit message: "Initial commit - YouTube to 3GP converter"
4. Click **"Commit all"**
5. Click **"Connect to GitHub"**
6. Follow the prompts to authorize Replit with GitHub
7. Select your `youtube-3gp-converter` repository
8. Click **"Push"**

**Option B: Using Terminal Commands (Alternative)**
1. In Replit, open the **Shell** tab at the bottom
2. Run these commands one by one:

```bash
# Step 1: Initialize git (if not already done)
git init

# Step 2: Add all files to git
git add .

# Step 3: Create your first commit
git commit -m "Initial commit - YouTube to 3GP converter"

# Step 4: Set main as default branch
git branch -M main

# Step 5: Connect to your GitHub repository (replace with YOUR URL)
git remote add origin https://github.com/YOUR_USERNAME/youtube-3gp-converter.git

# Step 6: Push code to GitHub
git push -u origin main
```

**When prompted for credentials:**
- Username: Your GitHub username
- Password: Use a **Personal Access Token** (not your password)
  - Create one at: https://github.com/settings/tokens
  - Click "Generate new token (classic)"
  - Give it a name: "Replit Upload"
  - Check: `repo` (full control of private repositories)
  - Click "Generate token"
  - Copy the token and paste it as your password

### Step 1.5: Verify Upload

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/youtube-3gp-converter`
2. You should see all your files:
   - `app.py`
   - `templates/` folder
   - `requirements.txt`
   - `render.yaml`
   - `build.sh`
   - `README.md`
   - And other files

**✅ If you see all files, GitHub setup is complete!**

---

## 🌐 Part 2: Deploy to Render.com (5 minutes)

Render will automatically build and host your app for free.

### Step 2.1: Create Render Account

1. **Go to Render**: Open https://render.com
2. **Click "Get Started"** or "Sign Up"
3. **Choose sign-up method**:
   - **Recommended**: Click "Sign up with GitHub"
   - This automatically connects your GitHub account
   - Or use email (then connect GitHub later)
4. **Complete registration** - Follow the prompts
5. **Verify your email** if required

### Step 2.2: Connect GitHub to Render

If you didn't sign up with GitHub:
1. Go to **Account Settings** (click your avatar → Settings)
2. Click **"Connect Account"** next to GitHub
3. Authorize Render to access your GitHub repositories
4. You may need to select which repositories Render can see

### Step 2.3: Create New Web Service

1. **Click the "New +" button** in the top-right corner
2. **Select "Web Service"** from the dropdown

### Step 2.4: Connect Your Repository

You'll see a list of your GitHub repositories:

1. **Find your repository**: `youtube-3gp-converter`
   - Use the search box if you have many repos
2. **Click "Connect"** next to your repository

**What's happening?**
- Render now has access to read your code
- It will automatically detect configuration files

### Step 2.5: Configure Your Web Service

Render will auto-detect settings from `render.yaml`, but verify these:

#### Basic Settings:
1. **Name**: 
   - Auto-filled from `render.yaml`: `youtube-3gp-converter`
   - This becomes your URL: `https://youtube-3gp-converter.onrender.com`
   - **You can change it** to anything available
   - Example: `nokia-tube` → `https://nokia-tube.onrender.com`

2. **Region**:
   - Auto-selected: `Oregon (US West)`
   - Choose closest to your location for better speed
   - Options: Oregon, Ohio, Frankfurt, Singapore

3. **Branch**:
   - Should be: `main`
   - This is the GitHub branch Render will deploy

#### Build & Deploy Settings (Auto-detected from render.yaml):

4. **Runtime**:
   - Shows: `Python 3`
   - This tells Render you're using Python

5. **Build Command**:
   - Shows: `./build.sh`
   - **What this does**: 
     - Installs Python packages (Flask, yt-dlp, gunicorn)
     - Installs FFmpeg (for video conversion)
     - Creates download folder

6. **Start Command**:
   - Shows: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 600 app:app`
   - **What this does**:
     - Starts your Flask app using Gunicorn (production server)
     - `--workers 1`: Uses single worker (prevents file conflicts)
     - `--timeout 600`: Allows 10-minute requests (for video processing)

#### Environment Variables (Auto-set from render.yaml):

7. **Environment Variables** - Click to expand and verify:
   - `PYTHON_VERSION` = `3.11.0` (Python version)
   - `SESSION_SECRET` = Auto-generated (secure session key)
   - `MAX_VIDEO_DURATION` = `21600` (6 hours in seconds)
   - `DOWNLOAD_TIMEOUT` = `3600` (60 minutes)
   - `CONVERSION_TIMEOUT` = `21600` (6 hours)
   - `FILE_RETENTION_HOURS` = `6` (files deleted after 6 hours)
   - `MAX_FILESIZE` = `500M` (max download size)

   **What these do**:
   - Control video length limits
   - Set timeout durations
   - Configure automatic cleanup

8. **Instance Type**:
   - Select: **Free**
   - Free tier includes:
     - 512 MB RAM
     - Shared CPU
     - 750 hours/month (enough for 24/7!)

### Step 2.6: Start Deployment

1. **Scroll to bottom**
2. **Click "Create Web Service"** (big blue button)

**What happens next?**
- Render creates a virtual server for your app
- Starts the build process (5-10 minutes)

### Step 2.7: Monitor the Build

You'll be redirected to your service dashboard. Watch the **Logs** section:

**Build Progress (2-5 minutes):**
```
Installing Python dependencies...
Installing system dependencies...
apt-get update
apt-get install -y ffmpeg
Creating download folder...
Build completed successfully!
```

**Deployment Progress (1-2 minutes):**
```
Starting service with 'gunicorn --bind 0.0.0.0:$PORT...'
 * Running on http://0.0.0.0:10000
```

**Status Indicators:**
- 🟡 **Yellow "Building"**: Build in progress (be patient)
- 🟢 **Green "Live"**: App is running successfully! ✅
- 🔴 **Red "Build failed"**: Something went wrong (check logs)

### Step 2.8: Get Your App URL

When status shows **🟢 Live**:

1. **Find your URL** at the top of the dashboard:
   - Format: `https://your-app-name.onrender.com`
   - Example: `https://youtube-3gp-converter.onrender.com`

2. **Click the URL** to open your app
3. **First load**: May take 30-60 seconds (cold start)
4. **You should see**: Your YouTube to 3GP converter homepage!

**✅ Your app is now live and accessible worldwide!**

---

## 🔄 Part 3: Keep Your App Awake (Optional, 3 minutes)

**Why do this?**
- Render's free tier **sleeps after 15 minutes** of inactivity
- Wake-up takes 30-60 seconds (slow first load for users)
- This keeps it awake 24/7 by pinging it every 10 minutes

### Step 3.1: Create Cron-Job Account

1. **Go to**: https://cron-job.org/en/
2. **Click "Sign Up"** (top-right)
3. **Fill in**:
   - Email address
   - Password
   - Accept terms
4. **Click "Create Account"**
5. **Verify email** - Check inbox and click verification link

### Step 3.2: Create a Cron Job

1. **Log in** to cron-job.org
2. **Click "Create cronjob"** (blue button)

### Step 3.3: Configure the Cron Job

**Fill in these fields:**

1. **Title**:
   - Enter: `Keep YouTube Converter Awake`
   - Just a friendly name to identify this job

2. **Address (URL)**:
   - Enter your Render URL: `https://your-app-name.onrender.com/`
   - **Important**: Include the trailing slash `/`
   - Example: `https://youtube-3gp-converter.onrender.com/`

3. **Schedule**:
   - Click **"Every 10 minutes"**
   - Or customize: `*/10 * * * *` (cron syntax)
   
   **What this means**:
   - Every 10 minutes, cron-job.org visits your site
   - Prevents Render from putting it to sleep
   - Uses only ~4,320 pings/month (well within free limits)

4. **Execution**:
   - Leave **"Enabled"** checked
   - Start time: Now (default)
   - End time: Leave blank (run forever)

5. **Notifications** (optional):
   - Check **"Email on failure"** if you want alerts
   - Leave others unchecked to avoid spam

6. **HTTP Method**:
   - Select: **GET** (default)

7. **Click "Create cronjob"**

### Step 3.4: Verify It's Working

1. **Wait 1-2 minutes**
2. **Go to "Dashboard"** in cron-job.org
3. **Check execution log**:
   - Should show: ✅ Success (200 OK)
   - Last execution: < 10 minutes ago

**✅ Your app now stays awake 24/7!**

---

## 🎯 Part 4: Test Your Deployed App

### Test 1: Homepage

1. **Open your app URL**: `https://your-app-name.onrender.com`
2. **Should see**:
   - "YouTube to 3GP" header
   - URL input box
   - "Convert to 3GP" button
   - Information boxes with features

### Test 2: Convert a Short Video

1. **Paste this URL**: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
2. **Click "Convert to 3GP"**
3. **Wait for processing**:
   - Status page auto-refreshes every 30 seconds
   - Download button appears when ready (1-3 minutes)
4. **Click "Download 3GP File"**
5. **File should download**: `video_XXXXX.3gp` (~3-4 MB)

**✅ If video converts and downloads, everything works perfectly!**

---

## 📱 Part 5: Use on Your Feature Phone

### Transfer the 3GP File

**Option A: Direct Download (If phone has internet)**
1. Open Opera Mini 4.4 on your Nokia 5310
2. Navigate to: `https://your-app-name.onrender.com`
3. Paste YouTube URL
4. Wait for conversion (be patient on 2G!)
5. Download directly to phone

**Option B: Transfer via Computer**
1. Download 3GP file to computer
2. Connect Nokia 5310 with USB cable
3. Copy 3GP file to phone's Videos folder
4. Disconnect phone
5. Open Videos app → Play

### Expected Quality
- **Resolution**: 176x144 (small but clear on feature phone)
- **File size**: ~2-3 MB per 5 minutes
- **Works on**: Nokia 5310, 3310, and most feature phones
- **Audio**: Clear AAC audio at 8kHz

---

## 🔧 Understanding Your Render Dashboard

After deployment, here's what you'll see:

### Dashboard Elements Explained:

1. **Service Name** (top)
   - Your app's name
   - Click to change or view settings

2. **Status Indicator**
   - 🟢 **Live**: App is running
   - 🟡 **Building**: Deployment in progress
   - 🔴 **Failed**: Check logs for errors
   - ⚪ **Suspended**: Free tier sleep (wakes on request)

3. **URL** (below name)
   - Your public URL
   - Click to open app
   - Click "⚙️" to add custom domain (paid feature)

4. **Logs Tab** (left sidebar)
   - **Build logs**: Installation process
   - **Deploy logs**: App startup
   - **Runtime logs**: Errors, requests, conversions
   - **Filter**: Search for specific errors

5. **Events Tab**
   - Deployment history
   - Build successes/failures
   - Automatic deploys from GitHub

6. **Environment Tab**
   - View/edit environment variables
   - Add new variables
   - Generate secrets

7. **Settings Tab**
   - Change instance type
   - Modify build/start commands
   - Configure auto-deploy
   - Delete service

### Monitoring Your App:

**Check Logs Regularly**:
- Look for errors during video conversion
- Monitor cleanup operations
- Check for failed downloads

**When to Check**:
- If conversions fail repeatedly
- If app becomes slow
- If users report issues

---

## 🚨 Troubleshooting Common Issues

### Issue 1: Build Failed

**Symptoms**: Red "Build failed" status

**Solutions**:
1. **Check build logs**:
   - Look for error messages
   - Common: `build.sh: Permission denied`
   
2. **Fix permissions**:
   - In Replit, run: `chmod +x build.sh`
   - Commit and push to GitHub
   - Render will auto-redeploy

3. **Missing files**:
   - Verify all files in GitHub
   - Check `requirements.txt` exists
   - Ensure `render.yaml` is present

### Issue 2: App Won't Start

**Symptoms**: "Live" but shows error when visiting URL

**Solutions**:
1. **Check deploy logs**:
   - Look for `ModuleNotFoundError`
   - Look for port binding errors

2. **Verify environment variables**:
   - Ensure `SESSION_SECRET` is set
   - Check other variables in Environment tab

3. **Check start command**:
   - Should be: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 600 app:app`

### Issue 3: Conversions Fail

**Symptoms**: All videos show "Conversion Failed"

**Solutions**:
1. **Check runtime logs**:
   - Look for `ffmpeg` or `yt-dlp` errors
   
2. **Verify ffmpeg installed**:
   - Build logs should show: "Installing ffmpeg"
   
3. **Test with short video**:
   - Try 1-2 minute videos first
   - Long videos may timeout on free tier

### Issue 4: Slow Performance

**Symptoms**: Takes 5+ minutes for short videos

**Solutions**:
1. **Free tier limitations**:
   - Shared CPU (slower processing)
   - 512 MB RAM (limited)
   - Normal for free tier

2. **Optimize**:
   - Use cron-job to prevent sleep
   - Reduce `MAX_VIDEO_DURATION` if needed
   - Process shorter videos

### Issue 5: App Goes to Sleep

**Symptoms**: First request takes 30-60 seconds

**Solutions**:
1. **Expected behavior**: Free tier sleeps after 15 minutes
2. **Solution**: Set up cron-job.org (Part 3 above)
3. **Alternative**: Upgrade to paid tier ($7/month for always-on)

### Issue 6: "Service Unavailable"

**Symptoms**: 503 error when visiting URL

**Solutions**:
1. **Wait**: App might be starting up (30-60 seconds)
2. **Check status**: Ensure dashboard shows "Live"
3. **Restart**: Settings → Manual Deploy → "Clear build cache & deploy"

---

## 💰 Understanding Render's Free Tier

### What's Included (FREE):
- ✅ 750 hours/month compute time
  - = 31.25 days worth of uptime
  - Enough for 24/7 hosting with cron-job
- ✅ 512 MB RAM
- ✅ Shared CPU
- ✅ 100 GB bandwidth/month
- ✅ Unlimited web services
- ✅ SSL/HTTPS included
- ✅ Auto-deploy from GitHub
- ✅ No credit card required

### Limitations:
- ⏸️ Sleeps after 15 minutes inactivity
- 🐌 Shared CPU (slower than dedicated)
- 💾 Limited RAM (512 MB)
- ⏱️ May timeout on very long videos (4-6 hours)

### When to Upgrade ($7/month):
- ⚡ Need faster processing
- 🏃 Want always-on (no sleep)
- 📈 Processing many videos
- 💪 Need more RAM (2 GB+)

**For personal use: Free tier is perfect!**

---

## 🔄 Updating Your App

### When to Update:
- Fix bugs
- Add features  
- Update yt-dlp version
- Change conversion settings

### How to Update:

1. **Make changes in Replit**
2. **Test locally** to ensure it works
3. **Commit changes**:
   ```bash
   git add .
   git commit -m "Describe your changes"
   git push origin main
   ```
4. **Render auto-deploys**:
   - Watches for GitHub changes
   - Automatically rebuilds
   - Takes 3-5 minutes
5. **Check status** in Render dashboard
6. **Test** your deployed app

**Auto-deploy disabled?**
- Go to Settings tab in Render
- Enable "Auto-Deploy"

---

## 🎉 Congratulations!

**You now have:**
- ✅ Live YouTube to 3GP converter
- ✅ Free hosting forever
- ✅ 24/7 uptime (with cron-job)
- ✅ Public URL to share
- ✅ Feature phone compatible
- ✅ No ads, completely free

**Your app URL**: `https://your-app-name.onrender.com`

### Share Your App:
- Send URL to friends with feature phones
- Works in areas with only 2G networks
- Perfect for Nokia 5310, 3310, etc.
- Bookmark on Opera Mini 4.4

### Next Steps:
1. Test with various YouTube videos
2. Share with friends
3. Monitor Render logs occasionally
4. Update when needed

---

## 📞 Getting Help

### If Something Goes Wrong:

1. **Check This Guide**: Re-read relevant section
2. **Check Render Logs**: Often shows exact error
3. **Check GitHub**: Ensure all files uploaded
4. **Restart Service**: Settings → Manual Deploy

### Useful Resources:
- Render Docs: https://render.com/docs
- yt-dlp Issues: https://github.com/yt-dlp/yt-dlp/issues
- FFmpeg Docs: https://ffmpeg.org/documentation.html

---

**Made with ❤️ for feature phone users everywhere!**
