# ⚡ 5-Minute Quick Start Guide

Get your YouTube to 3GP converter running in 5 minutes!

---

## 🎯 What You Need

- [ ] GitHub account (free)
- [ ] Render account (free, no credit card needed)
- [ ] 5 minutes

That's it!

---

## 📝 Step 1: Fork/Upload to GitHub (2 minutes)

### Option A: If you have this code locally
```bash
# In your project folder
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/youtube-3gp-converter.git
git push -u origin main
```

### Option B: Download and upload
1. Download this project as ZIP
2. Go to https://github.com/new
3. Create new repository: `youtube-3gp-converter`
4. Upload all files

---

## 🚀 Step 2: Deploy to Render (3 minutes)

### 2.1 Create Account
1. Go to https://render.com
2. Click "Get Started"
3. Sign up with GitHub (free, no credit card!)

### 2.2 Create Web Service
1. Click **"New +"** → **"Web Service"**
2. Click **"Connect GitHub"** → Select your repository
3. Render auto-detects everything from `render.yaml`!

### 2.3 Deploy
1. Render shows all settings (already configured!)
2. Click **"Create Web Service"**
3. Wait 3-5 minutes... ☕

**Done!** Your app is live at: `https://YOUR-APP-NAME.onrender.com`

---

## ✅ Step 3: Test It (1 minute)

1. Visit your app URL
2. Paste any YouTube URL (try a short video first)
3. Click "Convert to 3GP"
4. Wait for conversion
5. Download your 3GP file!

---

## 🎉 That's It!

Your YouTube to 3GP converter is live and working!

---

## ❓ What If Something Goes Wrong?

### Build Failed
- Check Render logs for errors
- Make sure all files are uploaded
- See [ERROR_GUIDE.md](ERROR_GUIDE.md)

### "Service Unavailable"
- Wait 30-60 seconds (app is waking up)
- Refresh the page

### Video Won't Download
- Try a different video
- Most videos work without cookies
- If needed: [COOKIE_SETUP_GUIDE.md](COOKIE_SETUP_GUIDE.md)

### App Keeps Crashing
- You're trying too long videos
- Try videos under 30 minutes on free tier
- See [ERROR_GUIDE.md](ERROR_GUIDE.md) → "Memory & Timeout Issues"

---

## 📚 Want to Learn More?

**Next steps**:
1. ✅ **[MONITORING_GUIDE.md](MONITORING_GUIDE.md)** - Set up monitoring
2. ✅ **[ERROR_GUIDE.md](ERROR_GUIDE.md)** - Bookmark for troubleshooting
3. ✅ **[ADVANCED_TINKERING.md](ADVANCED_TINKERING.md)** - Customize your app

**Full documentation**: [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)

---

## 💡 Pro Tips

### Keep Your App Awake
- Free tier sleeps after 15 minutes
- Set up UptimeRobot (free): https://uptimerobot.com
- Ping: `https://your-app.onrender.com/health` every 5 minutes

### Best Video Lengths
- ✅ **Perfect**: 5-30 minutes
- ⚠️ **OK**: 30-60 minutes
- 🔴 **Risky**: 1+ hours (may crash on free tier)

### If Downloads Keep Failing
- Upload cookies (see COOKIE_SETUP_GUIDE.md)
- Wait 10-15 minutes (rate limit)
- Try different video

---

## 🎯 Summary

**What you just deployed**:
- ✅ YouTube to 3GP converter
- ✅ Optimized for Render's free tier
- ✅ No cookies needed (for most videos)
- ✅ Auto-cleanup after 6 hours
- ✅ Feature phone compatible (176x144)

**Your app**:
- 🌐 Live at: `https://your-app.onrender.com`
- 💰 Cost: **FREE** (Render free tier)
- 📊 Limits: 750 hours/month, 512MB RAM
- 🔄 Auto-deploys when you push to GitHub

---

## ✨ Enjoy!

You now have your own YouTube to 3GP converter running 24/7 for free!

---

**Need help?** → [ERROR_GUIDE.md](ERROR_GUIDE.md) has answers to 95% of questions!

**Want to customize?** → [ADVANCED_TINKERING.md](ADVANCED_TINKERING.md) shows you how!

**Happy converting!** 📱🎥
