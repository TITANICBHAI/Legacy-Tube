# 📊 Monitoring & Maintenance Guide

## 🎯 Overview

This guide helps you monitor your YouTube to 3GP converter and catch issues before they become problems.

---

## 🔍 What to Monitor

### 1. Service Health (Check Daily)

**Where**: Render Dashboard → Your Service

**Green Dot** ✅ = Everything OK  
**Yellow Dot** ⚠️ = Deploying/Restarting  
**Red Dot** 🔴 = Service Down  

**Action if Red**:
1. Check logs for errors
2. Click "Manual Deploy" → "Deploy Latest Commit"
3. If still red, check Render status page

---

### 2. Memory Usage (Check if Crashes Occur)

**Where**: Render Logs

**Look for**:
```
✅ GOOD: "Memory usage: 45%"
⚠️ WARNING: "Memory usage: 75%"
🔴 BAD: "Worker killed by signal 9"
```

**Action if High Memory**:
```yaml
# Edit render.yaml
- key: MAX_VIDEO_DURATION
  value: 10800  # Reduce from 21600 to 10800 (3 hours)

- key: MAX_FILESIZE
  value: 200M   # Reduce from 500M to 200M
```

---

### 3. Error Frequency (Check Weekly)

**Where**: Render Logs tab

**Search for** (Ctrl+F in logs):
```
"Error:"
"Exception:"
"failed"
"timeout"
"signal 9"
```

**Normal errors** (OK to ignore):
- "Retrying with iOS client..." (part of fallback system)
- "Rate limited, waiting..." (automatic retry)
- Occasional download failures (YouTube issues)

**Concerning errors** (investigate):
- Multiple "signal 9" (out of memory)
- "ffmpeg command failed" repeatedly
- "Internal Server Error" frequently

---

### 4. Free Tier Usage (Check Monthly)

**Where**: Render Dashboard → Account → Usage

**Monitor**:
- ✅ Hours used: Target < 750/month
- ✅ Bandwidth: Target < 100GB/month

**If close to limits**:
1. Don't set up keep-awake service (saves hours)
2. Reduce FILE_RETENTION_HOURS to 3 (saves bandwidth)
3. Consider upgrade to paid tier

---

## 🚨 Setting Up Alerts

### Option 1: UptimeRobot (Free, Recommended)

**Setup** (5 minutes):

1. **Sign up**: https://uptimerobot.com (free)

2. **Add Monitor**:
   - Type: HTTP(s)
   - URL: `https://your-app.onrender.com/health`
   - Name: "YouTube 3GP Converter"
   - Interval: 5 minutes

3. **Set up Alerts**:
   - Email: Your email
   - Get notified when: Down
   - ✅ You'll get email if app goes down!

**What you'll monitor**:
- ✅ App availability (is it up?)
- ✅ Response time (is it fast?)
- ✅ Uptime percentage

---

### Option 2: Render Native Notifications

**Setup**:

1. Render Dashboard → Your Service → Settings
2. Scroll to "Notifications"
3. Add email address
4. Select events:
   - ✅ Deploys fail
   - ✅ Service crashes
   - ✅ Auto-deploy status

**What you'll monitor**:
- ✅ Build failures
- ✅ Deploy status
- ✅ Service crashes

---

### Option 3: Better Uptime (Advanced)

**Free features**:
- 10 monitors
- 3-minute checks
- Status page
- Incident management

**Setup**: https://betteruptime.com

Similar to UptimeRobot but with prettier interface.

---

## 📈 Log Analysis

### Daily Quick Check (2 minutes)

**Render Dashboard → Logs**, look for:

```
✅ GOOD SIGNS:
"Build completed successfully!"
"Conversion complete!"
"Health check: OK"

⚠️ WARNING SIGNS:
"Retrying download..." (>10 times)
"Memory usage: 80%"
"Timeout exceeded"

🔴 URGENT:
"signal 9" (out of memory)
"Build failed"
"Service unhealthy"
```

---

### Weekly Deep Dive (10 minutes)

**1. Check Success Rate**

Count in logs:
- ✅ "Conversion complete!" = Success
- ❌ "All download strategies failed" = Failure

**Target**: 80%+ success rate

**If below 80%**:
- Upload cookies (see COOKIE_SETUP_GUIDE.md)
- Check YouTube isn't blocking your IP
- Verify videos are public

---

**2. Check Average Conversion Time**

Look for: "Conversion complete in X seconds"

**Normal times**:
- 5-min video: 2-4 minutes
- 30-min video: 10-20 minutes
- 1-hour video: 30-60 minutes

**If much slower**:
- Render might be throttling (normal on free tier)
- Consider off-peak hours
- Upgrade to paid tier for faster CPU

---

**3. Check for Pattern Failures**

Look for repeated errors on specific:
- ✅ Video types (age-restricted, music videos)
- ✅ Times of day (YouTube rate limiting)
- ✅ Video lengths (memory issues on long videos)

**Take action based on patterns**.

---

## 🔧 Automated Monitoring Script

**Create `monitor.py`** (optional, advanced):

```python
import requests
import time
from datetime import datetime

APP_URL = "https://your-app.onrender.com"

def check_health():
    try:
        response = requests.get(f"{APP_URL}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ {datetime.now()}: Service healthy")
            return True
        else:
            print(f"⚠️ {datetime.now()}: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"🔴 {datetime.now()}: Service down - {e}")
        return False

if __name__ == "__main__":
    while True:
        check_health()
        time.sleep(300)  # Check every 5 minutes
```

**Run locally**:
```bash
python monitor.py
```

This keeps app awake AND alerts you to issues!

---

## 📊 Metrics to Track

### Keep a Simple Spreadsheet

**Weekly tracking** (every Sunday):

| Date | Uptime % | Conversions | Errors | Notes |
|------|----------|-------------|--------|-------|
| Jan 1 | 99.5% | 45 | 2 | All good |
| Jan 8 | 95.2% | 38 | 8 | Rate limited |
| Jan 15 | 100% | 52 | 1 | Added cookies |

**Red flags**:
- Uptime < 95%
- Error rate > 20%
- Sudden drop in conversions

---

## 🛠️ Maintenance Schedule

### Daily (2 minutes)
```
[ ] Check Render dashboard (green dot?)
[ ] Quick scan of logs (any red errors?)
```

### Weekly (10 minutes)
```
[ ] Review logs for patterns
[ ] Check success rate
[ ] Test with sample video
[ ] Verify health endpoint works
```

### Monthly (30 minutes)
```
[ ] Check free tier usage
[ ] Review uptime reports
[ ] Update yt-dlp if needed
[ ] Test various video types
[ ] Check cookies expiration
```

### Quarterly (1 hour)
```
[ ] Full system test
[ ] Update all dependencies
[ ] Review and update documentation
[ ] Check for yt-dlp updates
[ ] Re-export cookies
```

---

## 🚦 Health Dashboard (DIY)

**Quick visual check** - visit these URLs:

1. **Main App**: `https://your-app.onrender.com/`
   - ✅ Should load homepage

2. **Health Check**: `https://your-app.onrender.com/health`
   - ✅ Should show: `{"status":"ok"}`

3. **Test Conversion**: Try 2-minute video
   - ✅ Should complete in < 3 minutes

**All green?** → Everything working!  
**Any red?** → Check logs and ERROR_GUIDE.md

---

## 📱 Mobile Monitoring (Advanced)

**Use Telegram Bot** for alerts:

1. Create bot: https://t.me/BotFather
2. Get bot token
3. Add to UptimeRobot notifications
4. ✅ Get alerts on your phone!

**Alternative**: Discord webhook
- Create Discord webhook
- Add to UptimeRobot
- Get alerts in Discord

---

## 🎯 Key Performance Indicators (KPIs)

**Track these metrics**:

### Availability
- **Target**: 95%+ uptime
- **Measurement**: UptimeRobot reports
- **Action if below**: Check logs, restart service

### Success Rate
- **Target**: 80%+ conversions succeed
- **Measurement**: Count "Conversion complete" in logs
- **Action if below**: Upload cookies, reduce limits

### Response Time
- **Target**: < 5 seconds for homepage
- **Measurement**: UptimeRobot response time
- **Action if slow**: Render may be overloaded, try restart

### Memory Usage
- **Target**: < 70% average
- **Measurement**: Check logs for memory stats
- **Action if high**: Reduce video limits

### Error Rate
- **Target**: < 10% of conversions
- **Measurement**: Count errors in logs
- **Action if high**: See ERROR_GUIDE.md

---

## 🔔 Alert Thresholds

**Set up alerts for**:

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Uptime | < 98% | < 95% | Investigate logs |
| Response | > 3s | > 10s | Check Render status |
| Memory | > 70% | > 85% | Reduce limits |
| Errors | > 15% | > 30% | Check cookies |
| Disk | > 80% | > 95% | Manual cleanup |

---

## 📝 Incident Response Plan

**When something breaks**:

### Level 1: Minor Issue (< 10% users affected)
```
1. Note the issue
2. Check logs for cause
3. Fix within 24 hours
4. Monitor for recurrence
```

### Level 2: Major Issue (> 10% users affected)
```
1. IMMEDIATE: Check if service is up
2. If down: Restart service
3. Check logs for root cause
4. Fix within 4 hours
5. Post-mortem: Why did it happen?
```

### Level 3: Critical Outage (service down)
```
1. IMMEDIATE: Restart service on Render
2. If restart fails: Redeploy
3. If redeploy fails: Rollback to previous version
4. Check Render status page
5. Fix within 1 hour
6. Full post-mortem and prevention plan
```

---

## 🎓 Learning from Incidents

**After each issue, document**:

1. **What happened?** (symptoms)
2. **When?** (date, time)
3. **Why?** (root cause)
4. **How fixed?** (solution)
5. **How to prevent?** (action items)

**Keep incident log** in simple text file:

```
2024-01-15: Out of memory on 2-hour video
- Cause: Video too large for free tier
- Fix: Reduced MAX_VIDEO_DURATION to 3 hours
- Prevention: Added memory warning in UI

2024-01-22: Rate limited by YouTube
- Cause: Too many requests
- Fix: Uploaded cookies
- Prevention: Documentation updated
```

---

## ✅ Monitoring Checklist

**Initial Setup** (One-time):
```
[ ] Set up UptimeRobot
[ ] Enable Render email notifications
[ ] Bookmark Render logs page
[ ] Bookmark ERROR_GUIDE.md
[ ] Test health endpoint
[ ] Create monitoring spreadsheet
```

**Ongoing** (Regular):
```
Daily:
[ ] Check dashboard (green dot?)
[ ] Quick log scan

Weekly:
[ ] Review logs
[ ] Test sample video
[ ] Check metrics

Monthly:
[ ] Check usage limits
[ ] Update dependencies
[ ] Review incidents
```

---

## 🆘 Emergency Contacts

**When you need help**:

1. ✅ **This guide** (ERROR_GUIDE.md)
2. ✅ **Render Support** (render.com/docs)
3. ✅ **Render Status** (status.render.com)
4. ✅ **yt-dlp Issues** (github.com/yt-dlp/yt-dlp/issues)

**Before asking for help**, collect:
- Render logs (last 100 lines)
- Error messages
- What you tried
- When it started

---

## 🎯 Success Metrics

**Your monitoring is working if**:

✅ You catch issues before users report them  
✅ You know uptime % without checking  
✅ You can predict when limits will be hit  
✅ You get alerts before service goes down  
✅ Incidents are resolved in < 1 hour  

---

**Remember**: Good monitoring prevents 80% of issues. The other 20% you'll catch early!

Happy monitoring! 📊
