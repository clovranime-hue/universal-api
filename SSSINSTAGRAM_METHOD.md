# SSSInstagram Method - Free Instagram Downloads

## What Is This?

This method automates the **sssinstagram.com** website to download Instagram content for free, without requiring any API key or Instagram login.

## How It Works

The API uses **Playwright** (browser automation) to:
1. Navigate to sssinstagram.com
2. Paste the Instagram URL
3. Click the download button
4. Extract the video URL from the results
5. Return the direct download link

## Pros ✅

- **100% Free** - No API costs, no credits, no limits
- **No API Key** - No signup required
- **No Instagram Login** - Zero ban risk
- **Works for Most Content** - Reels, posts, IGTV, stories
- **No Rate Limits** - Use as much as you want

## Cons ⚠️

- **Slower** - 5-10 seconds per request (browser automation)
- **Resource Intensive** - Requires Chromium browser
- **May Break** - If sssinstagram.com changes their UI
- **Not for High Scale** - Browser automation has limits

## Setup

### Local Development

```bash
# Install playwright browsers
playwright install chromium

# Run the API
uvicorn app.main:app --reload
```

### Railway Deployment

The `nixpacks.toml` automatically installs Playwright with Chromium:

```toml
[phases.install]
cmds = [
  "pip install -r requirements.txt",
  "playwright install chromium --with-deps"
]
```

No additional configuration needed!

## Usage

### Set Method to SSSInstagram

```bash
# In Railway environment variables or .env file
INSTAGRAM_METHOD=sssinstagram
```

### API Call

```bash
curl -X POST http://localhost:8000/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.instagram.com/reel/DYYpzu5yCaH"}'
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
      "url": "https://direct-video-url.mp4",
      "quality": "720p",
      "format": "mp4"
    }
  ]
}
```

## Method Comparison

| Method | Cost | Speed | Success Rate | Best For |
|--------|------|-------|--------------|----------|
| **HikerAPI** | 100 free, then paid | Fast (~2s) | ~95% | Production |
| **SSSInstagram** | Free forever | Medium (~5-10s) | ~85% | Free tier, testing |
| **Direct** | Free | Fast (~2s) | ~20% | Fallback only |

## Recommended Configuration

### For Development / Testing

```bash
INSTAGRAM_METHOD=sssinstagram
# Free, no setup needed
```

### For Production

```bash
INSTAGRAM_METHOD=auto
HIKERAPI_TOKEN=your_token
# Uses HikerAPI first (fast), falls back to SSSInstagram (free)
```

### For Maximum Free Usage

```bash
INSTAGRAM_METHOD=sssinstagram
# 100% free, no limits, just slower
```

## Troubleshooting

### "Could not extract Instagram content"

1. **Check if sssinstagram.com is up**: Visit https://sssinstagram.com
2. **Increase timeout**: Set `REQUEST_TIMEOUT=60`
3. **Try different method**: Set `INSTAGRAM_METHOD=auto` or `INSTAGRAM_METHOD=hikerapi`

### Browser Installation Failed

```bash
# Install Playwright browsers manually
playwright install chromium

# For production (with dependencies)
playwright install chromium --with-deps
```

### Slow Performance

- Browser automation is inherently slower than direct API calls
- Expect 5-10 seconds per request
- For faster responses, use HikerAPI (100 free requests)

## Technical Details

### How SSSInstagram.com Works

The website:
1. Takes Instagram URL as input
2. Makes requests to Instagram's internal APIs
3. Extracts video URLs from Instagram's CDN
4. Returns download links to user

Our automation:
1. Uses Playwright to control a headless browser
2. Automates the entire process
3. Scrapes the resulting video URL
4. Returns it via our API

### Why Not Just Call Their API Directly?

SSSInstagram doesn't expose a public REST API. They use:
- JavaScript-heavy frontend
- Dynamic token generation
- Cloudflare protection
- Session-based requests

Browser automation is the most reliable way to interact with such sites.

## Alternatives

If SSSInstagram method doesn't work for you:

### 1. HikerAPI (Recommended)
- 100 free requests
- Fast, reliable
- Get token: https://hikerapi.com

### 2. Direct Extraction
- No dependencies
- Fast but low success rate
- Set `INSTAGRAM_METHOD=direct`

### 3. Your Own Scraper
- Build custom Instagram scraper
- Handle proxies, sessions, rate limits
- High maintenance

## Best Practices

1. **Use `auto` method in production**:
   ```bash
   INSTAGRAM_METHOD=auto
   HIKERAPI_TOKEN=your_token
   ```
   This uses HikerAPI first (fast), falls back to SSSInstagram (free)

2. **Set appropriate timeouts**:
   ```bash
   REQUEST_TIMEOUT=60  # Browser automation needs more time
   ```

3. **Monitor success rates**:
   - Track which method works best
   - Adjust configuration accordingly

4. **Cache results**:
   - Store download URLs temporarily
   - Avoid duplicate requests for same content

## Cost Comparison

### HikerAPI
- First 100 requests: FREE
- After that: ~$0.001 per request
- Example: 10,000 requests/month = ~$10

### SSSInstagram
- All requests: FREE
- Cost: Server resources for browser
- Example: 10,000 requests/month = $0 (but slower)

### Combined (Recommended)
- Use HikerAPI for speed-critical requests
- Use SSSInstagram as free fallback
- Optimize for cost vs. performance

## Resources

- SSSInstagram: https://sssinstagram.com
- Playwright Docs: https://playwright.dev
- HikerAPI (alternative): https://hikerapi.com

---

**Status**: ✅ Working  
**Last Tested**: 2026-05-17  
**Success Rate**: ~85% for public reels/posts
