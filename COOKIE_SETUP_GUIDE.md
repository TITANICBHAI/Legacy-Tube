# Cookie Setup Guide - Fix YouTube Blocking Issues

## Problem
Your YouTube to 3GP converter is showing these errors:
- ✘ "Sign in to confirm you're not a bot"
- ✘ "Please try again after 10 minutes"
- ✘ Error 111: Connection refused

**Why?** YouTube's 2025 bot detection blocks downloads from cloud servers, even for public videos.

## Solution: Upload YouTube Cookies

### Quick Steps

1. **Install Browser Extension**
   - **Chrome/Edge**: Search for "Get cookies.txt LOCALLY" in Chrome Web Store
   - **Firefox**: Search for "cookies.txt" in Firefox Add-ons

2. **Export Cookies**
   - Visit `youtube.com` in your browser
   - No need to log in (but logging in helps with age-restricted videos)
   - Click the extension icon
   - Click "Export" or "Download"
   - Save as `cookies.txt`

3. **Upload to Your App**
   - Go to `/cookies` page (or click the link on homepage)
   - Upload your `cookies.txt` file
   - System validates the cookies automatically
   - If valid, you'll see "Cookies uploaded and validated successfully!"

4. **Test**
   - Go back to homepage
   - You should see: ✓ "Cookies configured - ready to bypass YouTube restrictions"
   - Try converting a YouTube video
   - Should work without errors!

## Validation Requirements

The app checks for these authentication tokens in your cookies:
- `LOGIN_INFO` - YouTube session token
- `__Secure-1PSID` or `__Secure-3PSID` - Secure session identifiers

If your cookies are rejected, try:
1. Re-export cookies from a fresh browser session
2. Visit youtube.com first, then immediately export
3. If needed, log into YouTube first, then export

## Cookie Lifespan

- Cookies typically last 2-4 weeks
- Re-upload when you see authentication errors return
- The app will tell you if cookies expire

## Privacy & Security

- Cookies stored at `/tmp/cookies/youtube_cookies.txt` on server
- Never shared or transmitted elsewhere
- Only used for yt-dlp downloads
- Delete anytime from `/cookies` page

## Troubleshooting

**"Cookie validation failed: YouTube cookies found but missing LOGIN_INFO"**
→ Export cookies while visiting youtube.com, or log into YouTube first

**"Invalid cookie file: must contain YouTube cookies"**
→ Make sure you exported from youtube.com, not another site

**Still getting "sign in required" errors after upload**
→ Try logging into YouTube, then re-export cookies

**"Error 111 Connection Refused" persists**
→ Ensure cookies uploaded successfully (check /cookies page shows "Valid YouTube cookies")

## Support

For more details, see the full documentation in `replit.md`.
