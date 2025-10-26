# Docker Deployment Guide

## Overview
This guide covers deploying the YouTube to 3GP converter using Docker, optimized for Render's free tier constraints and other hosting platforms.

## Docker Optimizations Applied

### Addressing Render's Cons & Limitations

#### 1. Memory Constraints (512MB RAM)
**Problem**: Render's free tier has only 512MB RAM
**Solutions Implemented**:
- **Multi-stage Docker build**: Reduces final image size
- **Single worker**: `--workers=1` prevents memory exhaustion
- **Thread-based concurrency**: 2 threads instead of multiple workers
- **Worker recycling**: Auto-restart after 50 requests to prevent leaks
- **FFmpeg optimization**: Single thread, 1MB buffer, ultrafast preset
- **Python optimization**: `MALLOC_TRIM_THRESHOLD_` env vars for better memory management

#### 2. Spin-Down After Inactivity
**Problem**: Free tier spins down after 15 minutes
**Solutions Implemented**:
- **Health check endpoint**: `/health` route for monitoring
- **Docker HEALTHCHECK**: Automatic health verification every 30s
- **Keep-alive**: 5-second keep-alive on gunicorn

#### 3. Ephemeral Storage
**Problem**: `/tmp` storage resets on container restart
**Solutions Implemented**:
- **Graceful shutdown handler**: Cleans up temp files on SIGTERM/SIGINT
- **Automatic cleanup thread**: Removes old files every 30 minutes
- **6-hour file retention**: Users encouraged to download quickly
- **Status tracking in JSON**: Survives restarts if volume mounted

#### 4. Shared CPU (Slow Performance)
**Problem**: Free tier has minimal CPU allocation
**Solutions Implemented**:
- **FFmpeg ultrafast preset**: Trades quality for speed
- **Single thread encoding**: Prevents CPU thrashing
- **4-strategy fallback**: Tries multiple download methods efficiently
- **Progressive delays**: Prevents rate limiting from rapid retries

#### 5. Build Time Limitations
**Problem**: Slow build times on free tier
**Solutions Implemented**:
- **Slim base image**: `python:3.11-slim` instead of full
- **Minimal dependencies**: Only ffmpeg and yt-dlp
- **No cache pip install**: Faster builds, less disk usage
- **Apt cache cleanup**: Removes unnecessary files after install

## Quick Start

### Option 1: Docker Compose (Recommended for Local Testing)

1. **Build and run**:
```bash
docker-compose up --build
```

2. **Access app**:
```
http://localhost:5000
```

3. **Stop**:
```bash
docker-compose down
```

### Option 2: Direct Docker Commands

1. **Build image**:
```bash
docker build -t youtube-3gp-converter .
```

2. **Run container**:
```bash
docker run -d \
  --name youtube-3gp \
  -p 5000:5000 \
  -e SESSION_SECRET=your-secret-here \
  -e MAX_VIDEO_DURATION=21600 \
  -e DOWNLOAD_TIMEOUT=3600 \
  -e FILE_RETENTION_HOURS=6 \
  -e MAX_FILESIZE=500M \
  --memory=512m \
  --cpus=0.5 \
  youtube-3gp-converter
```

3. **View logs**:
```bash
docker logs -f youtube-3gp
```

4. **Stop container**:
```bash
docker stop youtube-3gp
docker rm youtube-3gp
```

## Deploying to Render

### Method 1: Using Dockerfile (Recommended)

1. **Push to GitHub**:
```bash
git add .
git commit -m "Add Docker support"
git push
```

2. **Create Web Service on Render**:
   - Go to https://render.com/dashboard
   - Click "New +" → "Web Service"
   - Connect your repository
   - Render auto-detects Dockerfile

3. **Configure**:
   - **Name**: youtube-3gp-converter
   - **Environment**: Docker
   - **Plan**: Free
   - **Health Check Path**: `/health`

4. **Environment Variables** (auto-set from render.yaml):
   - All variables are pre-configured
   - SESSION_SECRET is auto-generated

5. **Deploy**:
   - Click "Create Web Service"
   - Wait 5-10 minutes for build

### Method 2: Using render.yaml

Render can auto-deploy using the included `render.yaml`:

```bash
# Just push to GitHub - Render handles the rest
git push
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SESSION_SECRET` | (required) | Flask session secret key |
| `MAX_VIDEO_DURATION` | 21600 | Max video length (seconds) |
| `DOWNLOAD_TIMEOUT` | 3600 | Download timeout (seconds) |
| `CONVERSION_TIMEOUT` | 21600 | Conversion timeout (seconds) |
| `FILE_RETENTION_HOURS` | 6 | Auto-delete after (hours) |
| `MAX_FILESIZE` | 500M | Max download file size |
| `PORT` | 5000 | Server port |

## Docker Image Details

### Image Size
- **Base image**: python:3.11-slim (~140MB)
- **Final image**: ~400-500MB (with ffmpeg, yt-dlp)
- **Multi-stage build**: Reduces unnecessary build dependencies

### Security Features
- **Non-root user**: Runs as `appuser` (UID 1000)
- **Read-only templates**: Mounted read-only
- **Minimal attack surface**: Only required packages installed

### Health Checks
The Docker image includes automatic health checks:
- **Interval**: Every 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3 attempts before unhealthy
- **Endpoint**: `GET /health`

Test health manually:
```bash
docker exec youtube-3gp curl http://localhost:5000/health
```

Expected response:
```json
{"status": "ok", "service": "youtube-3gp-converter"}
```

## Performance Tuning

### For 512MB RAM Limit
Already optimized in Dockerfile:
- 1 worker, 2 threads
- Worker temp dir in `/dev/shm` (RAM)
- Max 50 requests before worker restart
- 1MB FFmpeg buffer size

### For 1GB+ RAM
Edit `Dockerfile` CMD section:
```dockerfile
CMD ["gunicorn", \
     "--workers", "2", \
     "--threads", "2", \
     ...
```

### For Faster Builds
Use Docker BuildKit:
```bash
DOCKER_BUILDKIT=1 docker build -t youtube-3gp-converter .
```

## Troubleshooting

### Container Exits Immediately
**Check logs**:
```bash
docker logs youtube-3gp
```

**Common causes**:
- Missing environment variables
- Port already in use
- Insufficient memory

### Health Check Failing
**Test manually**:
```bash
docker exec youtube-3gp curl http://localhost:5000/health
```

**Check if app is running**:
```bash
docker exec youtube-3gp ps aux
```

### Out of Memory Errors
**Monitor memory usage**:
```bash
docker stats youtube-3gp
```

**If consistently high**:
- Reduce MAX_VIDEO_DURATION
- Lower MAX_FILESIZE
- Don't process multiple videos simultaneously

### Conversion Fails
**Check FFmpeg**:
```bash
docker exec youtube-3gp ffmpeg -version
```

**Check yt-dlp**:
```bash
docker exec youtube-3gp yt-dlp --version
```

### Render-Specific Issues

#### Build Fails on Render
- Check Render build logs
- Ensure Dockerfile is in repository root
- Verify base image is accessible

#### App Unreachable After Deploy
- Wait 30-60 seconds for container to start
- Check health check endpoint is responding
- Verify PORT environment variable is set to 5000

#### Memory Errors on Render
- App is optimized for 512MB
- Try shorter videos first
- Avoid concurrent conversions

## Monitoring

### Check Container Health
```bash
docker inspect --format='{{.State.Health.Status}}' youtube-3gp
```

### View Real-Time Logs
```bash
docker logs -f --tail=100 youtube-3gp
```

### Monitor Resource Usage
```bash
docker stats youtube-3gp
```

### Test Health Endpoint
```bash
curl http://localhost:5000/health
```

## Best Practices

1. **Always use health checks**: Prevents unexpected downtime
2. **Set memory limits**: Prevents container from consuming all host memory
3. **Use environment variables**: Don't hardcode secrets in Dockerfile
4. **Regular updates**: Keep base image and dependencies updated
5. **Monitor logs**: Watch for errors and performance issues

## Cleanup

### Stop and Remove Container
```bash
docker stop youtube-3gp
docker rm youtube-3gp
```

### Remove Image
```bash
docker rmi youtube-3gp-converter
```

### Clean All Docker Resources
```bash
docker system prune -a
```

## Production Checklist

- [ ] Set strong SESSION_SECRET
- [ ] Configure health check monitoring
- [ ] Set appropriate memory limits
- [ ] Enable logging/monitoring
- [ ] Test with sample videos
- [ ] Verify cleanup thread works
- [ ] Test graceful shutdown
- [ ] Monitor resource usage first week

## Comparison: Docker vs Native

| Aspect | Docker | Native (render.yaml) |
|--------|--------|---------------------|
| Portability | ✅ High | ❌ Platform-specific |
| Build time | ~5-7 min | ~3-5 min |
| Memory usage | +50MB overhead | Lower |
| Isolation | ✅ Better | ❌ Shared |
| Debugging | Harder | Easier |
| **Recommendation** | Production | Development/Render |

For Render free tier, **use native render.yaml** deployment (faster builds, less overhead). Use Docker for:
- Local development
- Other hosting platforms
- When you need consistent environments

## Support

For issues:
1. Check Docker logs
2. Verify health endpoint
3. Test with short video first
4. Review Render deployment logs
5. Ensure cookies uploaded if needed

## Summary

This Docker setup is optimized for:
- ✅ Render's 512MB RAM limit
- ✅ Single CPU core
- ✅ Ephemeral storage
- ✅ Fast builds
- ✅ Graceful shutdowns
- ✅ Health monitoring
- ✅ Memory efficiency

Deploy with confidence knowing all of Render's limitations have been addressed!
