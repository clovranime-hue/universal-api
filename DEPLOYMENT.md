# Deployment Guide - Universal Media Downloader API

## 🚀 Quick Deploy (5 Minutes)

### Option 1: Deploy from GitHub (Recommended)

#### Step 1: Push to GitHub

```bash
cd universal-downloader-api

# Initialize git (if not already done)
git init
git add .
git commit -m "Universal Media Downloader API - Initial commit"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/universal-downloader-api.git
git push -u origin main
```

#### Step 2: Deploy on Railway

1. **Go to** [railway.app](https://railway.app)
2. **Login** with GitHub
3. **Click** "New Project"
4. **Select** "Deploy from GitHub repo"
5. **Choose** your `universal-downloader-api` repository
6. **Wait** 2-3 minutes for build and deployment

#### Step 3: Configure (Optional)

In Railway dashboard:
- Click your project
- Go to **Variables** tab
- Add any optional environment variables (see below)

#### Step 4: Test Your API

```bash
# Get your Railway URL from dashboard
# Example: https://your-project.up.railway.app

# Test health
curl https://your-project.up.railway.app/health

# Test Instagram
curl -X POST https://your-project.up.railway.app/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.instagram.com/reel/DXWRqQ5iSTV/"}'

# Test YouTube
curl -X POST https://your-project.up.railway.app/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

---

### Option 2: Deploy from ZIP

If you prefer not to use GitHub:

#### Step 1: Extract ZIP

```bash
unzip universal-downloader-api-final.zip
cd universal-downloader-api
```

#### Step 2: Initialize Git

```bash
git init
git add .
git commit -m "Initial commit"
```

#### Step 3: Deploy to Railway

1. Go to Railway.app
2. New Project → Deploy from GitHub
3. Create new repository from Railway
4. Push your code:
   ```bash
   git remote add origin https://github.com/railwayapp-xyz/your-repo.git
   git push -u origin main
   ```

---

## 🔧 Environment Variables (Optional)

All variables are optional. The API works with defaults!

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REQUEST_TIMEOUT` | Request timeout in seconds | 60 | ❌ |
| `MAX_FILE_SIZE_MB` | Max file size in MB | 100 | ❌ |
| `PORT` | Server port | 8000 | ❌ (Railway sets this) |
| `HOST` | Server host | 0.0.0.0 | ❌ |

### How to Set in Railway

1. Go to your project dashboard
2. Click **Variables** tab
3. Click **New Variable**
4. Enter key and value
5. Click **Add**

Example:
```
REQUEST_TIMEOUT=60
MAX_FILE_SIZE_MB=100
```

---

## 📊 Railway Pricing

### Free Tier
- $0/month
- 500 hours/month runtime
- Shared CPU
- 512MB RAM
- **Perfect for testing!**

### Hobby Plan
- $5/month
- Always-on
- More resources
- **Recommended for production**

### Pro Plan
- $20/month
- Priority support
- More resources
- **For high traffic**

---

## 🧪 Testing Your Deployment

### 1. Health Check

```bash
curl https://your-project.up.railway.app/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "platforms": ["youtube", "instagram", "pinterest", ...]
}
```

### 2. Instagram Reel

```bash
curl -X POST https://your-project.up.railway.app/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.instagram.com/reel/DXWRqQ5iSTV/"}'
```

**Expected:** Success with video URL

### 3. YouTube Video

```bash
curl -X POST https://your-project.up.railway.app/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

**Expected:** Success with video URL

### 4. Pinterest Pin

```bash
curl -X POST https://your-project.up.railway.app/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.pinterest.com/pin/123456789/"}'
```

**Expected:** Success with image/video URL

---

## 🐛 Troubleshooting

### Build Fails

**Check:**
1. All files committed to Git
2. `requirements.txt` present
3. `nixpacks.toml` present
4. No syntax errors in Python files

**Fix:**
```bash
# Check git status
git status

# Add missing files
git add .
git commit -m "Fix missing files"
git push
```

### Instagram Downloads Fail

**Possible causes:**
- Reel is private
- Reel is deleted
- Timeout too short

**Fix:**
1. Set `REQUEST_TIMEOUT=60` in Railway variables
2. Try a different public reel
3. Check Railway logs for errors

### Slow Performance

**Causes:**
- Instagram uses browser automation (inherently slower)
- Railway free tier has limited resources

**Fix:**
1. Upgrade to Railway Hobby plan ($5/month)
2. Cache results to avoid duplicate requests
3. Set reasonable expectations (5-10s for Instagram is normal)

### API Returns 500 Error

**Check:**
1. Railway logs for error details
2. Input URL format
3. Platform is supported

**Fix:**
```bash
# Check logs in Railway dashboard
# Look for specific error messages
```

---

## 📈 Monitoring

### Railway Dashboard

- **Logs**: Real-time application logs
- **Metrics**: CPU, memory, network usage
- **Deployments**: Build history and status

### Health Endpoint

Use `/health` for uptime monitoring:

```bash
curl https://your-project.up.railway.app/health
```

Integrate with:
- UptimeRobot (free)
- Pingdom
- Custom monitoring

---

## 🔒 Security Best Practices

1. **No secrets in code** - Use Railway environment variables
2. **Rate limiting** - Built-in, but consider adding more for production
3. **Input validation** - All inputs validated via Pydantic
4. **HTTPS** - Automatic via Railway
5. **CORS** - Configured for web access

---

## 📦 File Structure

```
universal-downloader-api/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── schemas.py           # Request/response models
│   ├── detector.py          # URL auto-detection
│   └── downloaders/
│       ├── base.py          # Base downloader class
│       ├── youtube.py       # YouTube downloader
│       ├── instagram.py     # Instagram downloader (SSSInstagram)
│       ├── instagram_sss.py # SSSInstagram automation
│       ├── pinterest.py     # Pinterest downloader
│       └── generic.py       # Generic downloader (yt-dlp)
├── requirements.txt         # Python dependencies
├── nixpacks.toml           # Railway build config
├── railway.json            # Railway deployment config
├── Procfile                # Process file
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore file
├── README.md               # Main documentation
├── DEPLOYMENT.md           # This file
├── QUICK_START.md          # Quick start guide
└── SSSINSTAGRAM_METHOD.md  # Instagram method docs
```

---

## 🎯 Post-Deployment Checklist

- [ ] Health endpoint returns 200 OK
- [ ] Instagram reel downloads successfully
- [ ] YouTube video downloads successfully
- [ ] Pinterest pin downloads successfully
- [ ] Error messages are helpful
- [ ] Response times are acceptable
- [ ] Logs show no errors
- [ ] Environment variables set (if needed)

---

## 📞 Support

### Documentation
- `README.md` - Main documentation
- `DEPLOYMENT.md` - This file
- `QUICK_START.md` - Quick start guide
- `SSSINSTAGRAM_METHOD.md` - Instagram details

### Railway Support
- [Railway Docs](https://docs.railway.app/)
- [Railway Discord](https://discord.gg/railway)

### API Issues
- Check Railway logs first
- Test with known working URLs
- Verify environment variables

---

## 🎉 You're Done!

Your Universal Media Downloader API is now live and ready to use!

**Next Steps:**
1. Share your API URL with users
2. Integrate into your applications
3. Monitor usage and performance
4. Scale as needed (Railway makes it easy)

**Happy deploying! 🚀**
