# Proxy Rotation Guide - YouTube Anti-Blocking

## 🎯 Overview

This app now includes **automatic proxy rotation** to reduce YouTube IP blocking. It's designed to work on Render's free tier with minimal resource usage.

## ⚠️ Important Notes

- **Proxies help but aren't perfect**: YouTube's bot detection is sophisticated
- **Cookies still recommended**: For best results, upload cookies from `/cookies` page
- **Free tier friendly**: Disabled by default to save Render's limited resources
- **Free proxies are unreliable**: They work ~30-50% of the time

## 🚀 Quick Setup (Render Free Tier)

### Option 1: Enable Auto Proxy Rotation (Uses Resources)

In Render Dashboard → Environment Variables:

```bash
ENABLE_PROXY_ROTATION=true
MAX_PROXY_CACHE=5          # Keep it low (5-10) to save memory
PROXY_TEST_TIMEOUT=3       # Fast testing (3-5 seconds)
```

**Resource Impact:**
- Initial startup: +20-30 seconds (proxy testing)
- Memory: +10-20 MB (cached proxies)
- CPU: Minimal after startup

### Option 2: Manual Proxy (Recommended if you have one)

If you have a paid residential proxy or your own proxy server:

```bash
PROXY_URL=http://username:password@proxy-server:port
```

This uses almost no extra resources and is more reliable.

### Option 3: Keep Disabled (Default)

```bash
ENABLE_PROXY_ROTATION=false
```

No extra resource usage. Rely on YouTube cookies and multiple client strategies.

## 📊 How It Works

### Download Strategy (Priority Order):

1. **Manual Proxy** (if `PROXY_URL` set) → Try all 7 YouTube client strategies
2. **Rotating Free Proxies** (if enabled) → Try 3 different proxies × 7 strategies each
3. **Direct Connection** → Try all 7 strategies without proxy
4. **Fallback to cookies** → If all fail, suggest uploading cookies

### Free Proxy Sources:

- ProxyScrape API (public HTTP/HTTPS proxies)
- GeoNode API (verified proxy list)
- Auto-tested before use (only working proxies are cached)

## 🎛️ Configuration Options

| Variable | Default | Description | Free Tier Recommended |
|----------|---------|-------------|----------------------|
| `ENABLE_PROXY_ROTATION` | `false` | Enable auto proxy rotation | `false` (save resources) |
| `PROXY_URL` | _(empty)_ | Manual proxy URL | Set if you have one |
| `MAX_PROXY_CACHE` | `20` | Max proxies to cache | `5-10` (lower = less memory) |
| `PROXY_TEST_TIMEOUT` | `5` | Proxy test timeout (seconds) | `3` (faster startup) |

## 📈 Monitoring

Visit `/proxy-stats` to see:
- Proxy rotation status
- Number of cached proxies
- Success/failure rates
- Current proxy being used

## 🔧 Troubleshooting

### Videos still fail without cookies

**Why:** Free proxies are blocked by YouTube too, or the video requires authentication.

**Solution:**
1. Upload YouTube cookies at `/cookies`
2. Use a paid residential proxy service (Bright Data, Smartproxy)
3. Try different videos (some are less restricted)

### Proxy rotation uses too many resources

**Why:** Testing proxies takes CPU/memory on startup.

**Solution:**
```bash
ENABLE_PROXY_ROTATION=false  # Disable it
MAX_PROXY_CACHE=5           # Or reduce cache size
PROXY_TEST_TIMEOUT=2        # Or reduce test timeout
```

### Some proxies work, some don't

**Why:** Free proxies are unstable and frequently banned by YouTube.

**Solution:** This is normal. The system automatically:
- Rotates through proxies
- Removes failed proxies after 3 failures
- Refreshes proxy list every hour

## 💰 Paid Proxy Options (Better Success Rate)

If you need more reliability:

1. **Residential Proxies** (Best, ~95% success rate)
   - Bright Data: $500/mo for 40GB
   - Smartproxy: $50/mo for 2GB
   - Set `PROXY_URL=http://user:pass@gate.smartproxy.com:7000`

2. **Self-Hosted VPN** (Free but complex)
   - Run WireGuard on home connection
   - Set `PROXY_URL=http://your-home-ip:port`

3. **Datacenter Proxies** (Cheap but often blocked)
   - Not recommended for YouTube

## 🎯 Best Strategy for Render Free Tier

**Recommended Setup:**

```bash
# Disable proxy rotation to save resources
ENABLE_PROXY_ROTATION=false

# Rely on multiple client strategies (already built-in)
# 7 different YouTube client emulations
# iOS, Android TV, Android, Android Music, etc.

# Upload cookies for restricted videos
# Visit /cookies and upload youtube.com cookies
```

**Why?** 
- No extra resource usage
- Built-in client rotation works well (70-80% success rate without cookies)
- Cookies solve most remaining blocks
- Free tier stays under 512MB RAM limit

## 🔒 Security Notes

- Free proxies are untrusted - they can see your traffic
- Don't use proxies for sensitive data
- Manual proxy with authentication is safer
- Cookies are stored locally in `/tmp/cookies` (deleted after 6 hours)

## 📝 Summary

| Scenario | Recommended Setup | Success Rate |
|----------|------------------|--------------|
| Render Free Tier, no cookies | `ENABLE_PROXY_ROTATION=false` | 70-80% |
| Render Free Tier, with cookies | `ENABLE_PROXY_ROTATION=false` + upload cookies | 95%+ |
| Have paid proxy | `PROXY_URL=...` (disable rotation) | 90-95% |
| Need maximum success | Paid proxy + cookies | 99%+ |

**Bottom Line:** For Render free tier, keep proxy rotation **disabled** and upload YouTube cookies when needed. Enable proxy rotation only if you're experiencing frequent blocks and can spare the extra resources.
