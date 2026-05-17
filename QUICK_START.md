# Quick Start - Universal Media Downloader API

## 3-Minute Setup

### 1. Deploy to Railway

```bash
# In the universal-downloader-api folder
git init
git add .
git commit -m "Deploy to Railway"
git remote add origin https://github.com/YOUR_USERNAME/universal-downloader-api.git
git push -u origin main
```

Then on Railway.app:
- New Project → Deploy from GitHub → Select repo
- Wait 2-3 minutes for build

### 2. Get Instagram Working (Optional but Recommended)

1. Visit https://hikerapi.com
2. Sign up (free, no credit card)
3. Verify via Telegram (1 minute)
4. Copy your access token
5. In Railway dashboard: Variables → Add `HIKERAPI_TOKEN=your_token`

### 3. Test Your API

```bash
# Replace with your Railway URL
API_URL=https://your-project.up.railway.app

# Test YouTube (always works)
curl -X POST $API_URL/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Test Instagram (works with HikerAPI token)
curl -X POST $API_URL/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.instagram.com/reel/DYYpzu5yCaH"}'

# Health check
curl $API_URL/health
```

## That's It! 🎉

Your API is now live and ready to use.

## Supported Platforms

✅ **Excellent**: YouTube, TikTok, Twitter, Facebook, Vimeo, 1000+ sites  
✅ **Good**: Instagram (with HikerAPI token), Pinterest  
⚠️ **Limited**: Instagram (without token)

## Common Commands

```bash
# Download any video
curl -X POST $API_URL/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "YOUR_URL_HERE"}'

# Get info without downloading
curl "$API_URL/api/info?url=YOUR_URL_HERE"

# Check supported platforms
curl $API_URL/api/supported
```

## Need Help?

- **Instagram issues**: See `INSTAGRAM_SETUP.md`
- **Deployment issues**: See `DEPLOYMENT.md`
- **Full docs**: See `README.md` and `FINAL_SUMMARY.md`

---

**Cost**: Free to start (Railway free tier + 100 free HikerAPI requests)  
**Time**: ~5 minutes total
