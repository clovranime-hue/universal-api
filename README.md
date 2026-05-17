# Universal Media Downloader API

🚀 **Deploy-ready API for downloading media from Instagram, YouTube, Pinterest, TikTok, Twitter, Facebook, and 1000+ more sites!**

## ✨ Features

- 📸 **Instagram** - Reels, posts, IGTV, stories (100% FREE via SSSInstagram)
- 🎬 **YouTube** - Videos, shorts, playlists (via yt-dlp)
- 📌 **Pinterest** - Pins, videos, images
- 🌐 **1000+ Sites** - TikTok, Twitter, Facebook, Vimeo, etc.
- ⚡ **Fast & Production-Ready** - Optimized for Railway.app
- 🔍 **Auto-Detection** - Automatically detects platform from URL

## 🚀 Deploy to Railway (2 Minutes)

### Step 1: Push to GitHub

```bash
cd universal-downloader-api
git init
git add .
git commit -m "Universal Media Downloader API"
git remote add origin https://github.com/YOUR_USERNAME/universal-downloader-api.git
git push -u origin main
```

### Step 2: Deploy on Railway

1. Go to [railway.app](https://railway.app)
2. Click **New Project**
3. Select **Deploy from GitHub**
4. Choose your `universal-downloader-api` repository
5. Railway auto-builds and deploys! 🎉

### Step 3: Done!

Your API is live at: `https://your-project.up.railway.app`

## 📡 API Usage

### Download Media

```bash
curl -X POST https://your-project.up.railway.app/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.instagram.com/reel/DXWRqQ5iSTV/"}'
```

### Response

```json
{
  "success": true,
  "platform": "instagram",
  "content_type": "reel",
  "media_type": "video",
  "title": "Instagram reel",
  "thumbnail": "https://...",
  "media": [
    {
      "url": "https://direct-download-link.mp4",
      "quality": "720p",
      "format": "mp4"
    }
  ],
  "metadata": {
    "author": "username",
    "views": 10000,
    "likes": 500
  }
}
```

### Get Media Info (Without Download)

```bash
curl "https://your-project.up.railway.app/api/info?url=https://www.instagram.com/reel/DXWRqQ5iSTV/"
```

### Health Check

```bash
curl https://your-project.up.railway.app/health
```

## 🔧 Configuration (Optional)

All optional via environment variables in Railway dashboard:

| Variable | Description | Default |
|----------|-------------|---------|
| `REQUEST_TIMEOUT` | Request timeout in seconds | 60 |
| `MAX_FILE_SIZE_MB` | Max file size in MB | 100 |
| `PORT` | Server port | 8000 |

**No API keys required!** Everything works out of the box.

## 📱 Supported Platforms

| Platform | Content Types | Status |
|----------|--------------|--------|
| **Instagram** | Reels, Posts, IGTV, Stories | ✅ 100% FREE |
| **YouTube** | Videos, Shorts, Playlists | ✅ Perfect |
| **Pinterest** | Pins, Videos, Images | ✅ Good |
| **TikTok** | Videos | ✅ Good |
| **Twitter/X** | Videos, GIFs | ✅ Good |
| **Facebook** | Public Videos | ✅ Good |
| **Vimeo** | Videos | ✅ Good |
| **1000+ More** | Various | ✅ Via yt-dlp |

## 🧪 Test Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Install browser for Instagram
playwright install chromium

# Run API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Test
curl -X POST http://localhost:8000/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.instagram.com/reel/DXWRqQ5iSTV/"}'
```

## 📚 Documentation

- **SSSInstagram Method**: See [`SSSINSTAGRAM_METHOD.md`](SSSINSTAGRAM_METHOD.md)
- **Deployment Guide**: See [`DEPLOYMENT.md`](DEPLOYMENT.md)
- **Quick Start**: See [`QUICK_START.md`](QUICK_START.md)

## 💰 Cost

- **Railway**: Free tier available, $5/month for production
- **API**: 100% FREE - No API keys, no subscriptions
- **Instagram**: 100% FREE via SSSInstagram (no limits)

## ⚡ Performance

- **YouTube**: ~2-5 seconds
- **Instagram**: ~5-10 seconds (browser automation)
- **Pinterest**: ~3-6 seconds
- **Others**: ~2-5 seconds

## 🔒 Security

- No user data stored
- SSL encryption (via Railway)
- No Instagram login required
- No API keys to leak
- Rate limiting built-in

## 🐛 Troubleshooting

### Instagram downloads failing

- Increase `REQUEST_TIMEOUT` to 60 or higher
- The reel may be private or deleted
- Try a different public reel to test

### Slow performance

- Instagram uses browser automation (inherently slower)
- Consider Railway paid plan for more resources
- Cache results to avoid duplicate requests

### Build fails on Railway

- Check logs in Railway dashboard
- Ensure all files are committed to Git
- Verify `nixpacks.toml` and `requirements.txt` are present

## 📞 Support

- **Issues**: Open GitHub issue
- **Docs**: See documentation files in repo
- **Status**: Check `/health` endpoint

## 📄 License

MIT License - Use freely for personal and commercial projects.

---

**Built with**: FastAPI, Playwright, yt-dlp  
**Deployed on**: Railway.app  
**Status**: ✅ Production Ready
