"""
Instagram downloader using SSSInstagram.com
100% FREE, no API key, no Instagram login required
Uses browser automation to extract download URLs
"""
import asyncio
import re
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Browser
import httpx

from app.downloaders.base import BaseDownloader
from app.schemas import PlatformType, ContentTypes, MediaItem, MediaMetadata
from app.config import get_settings


class InstagramDownloader(BaseDownloader):
    """
    Instagram downloader using SSSInstagram.com
    
    ✅ 100% FREE - No API key needed
    ✅ No Instagram login required
    ✅ Works for reels, posts, IGTV, stories
    ⏱️ Takes 5-10 seconds per request
    """
    
    SITE_URL = "https://sssinstagram.com"
    
    def __init__(self, timeout: int = 60, headless: bool = True):
        super().__init__(timeout)
        self.platform = PlatformType.INSTAGRAM
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
    
    def _extract_shortcode(self, url: str) -> Optional[str]:
        """Extract shortcode from Instagram URL"""
        patterns = [
            r'instagram\.com\/reel\/([^\/\?\&]+)',
            r'instagram\.com\/p\/([^\/\?\&]+)',
            r'instagram\.com\/tv\/([^\/\?\&]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _detect_content_type(self, url: str) -> ContentTypes:
        """Detect content type from URL"""
        if '/reel/' in url:
            return ContentTypes.REEL
        elif '/tv/' in url:
            return ContentTypes.IGTV
        elif '/stories/' in url:
            return ContentTypes.STORY
        elif '/p/' in url:
            return ContentTypes.POST
        return ContentTypes.POST
    
    async def _get_browser(self) -> Browser:
        """Get or create browser instance"""
        if self.browser is None:
            from playwright.async_api import async_playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--disable-gpu',
                    '--disable-blink-features=AutomationControlled',
                ]
            )
        return self.browser
    
    async def _download_via_sss(self, url: str) -> Optional[Dict]:
        """
        Download via sssinstagram.com using browser automation
        """
        browser = await self._get_browser()
        page = await browser.new_page()
        
        try:
            # Set realistic headers
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            })
            
            # Navigate to sssinstagram.com
            print(f"📸 Navigating to {self.SITE_URL}...")
            await page.goto(self.SITE_URL, wait_until='networkidle', timeout=min(self.timeout * 1000, 30000))
            
            # Wait for page to load
            await page.wait_for_timeout(2000)
            
            # Find input field and paste URL
            print(f"🔗 Submitting URL: {url}")
            
            # Try to find input by various selectors
            input_found = False
            input_selectors = [
                'input[placeholder*="link"]',
                'input[placeholder*="URL"]',
                'input[placeholder*="Instagram"]',
                'input[type="url"]',
                'input.form-control',
                'input[name="url"]',
            ]
            
            for selector in input_selectors:
                try:
                    input_elem = await page.query_selector(selector)
                    if input_elem:
                        await input_elem.fill(url)
                        input_found = True
                        print(f"✅ Found input field: {selector}")
                        break
                except Exception:
                    continue
            
            if not input_found:
                # Try direct URL approach
                print("⚠️ No input found, trying direct URL navigation...")
                await page.goto(f"{self.SITE_URL}/en?url={url}", wait_until='networkidle', timeout=min(self.timeout * 1000, 30000))
                await page.wait_for_timeout(3000)
            
            # Click download button if we filled input
            if input_found:
                download_selectors = [
                    'button:has-text("Download")',
                    'button:has-text("download")',
                    'input[type="submit"]',
                    '.download-btn',
                    'button.btn-primary',
                    'button[type="submit"]',
                ]
                
                for selector in download_selectors:
                    try:
                        btn = await page.query_selector(selector)
                        if btn:
                            await btn.click()
                            print(f"✅ Clicked download button")
                            break
                    except Exception:
                        continue
            
            # Wait for processing
            print("⏳ Waiting for results...")
            await page.wait_for_timeout(5000)
            
            # Get page content and extract video URL
            content = await page.content()
            
            # Look for video URLs
            video_patterns = [
                r'(https://[^\s"\'<>]+\.mp4[^\s"\'<>]*)',
                r'(https://[^\s"\'<>]+cdninstagram\.com[^\s"\'<>]+)',
                r'(https://[^\s"\'<>]+fbcdn\.net[^\s"\'<>]+)',
            ]
            
            video_url = None
            for pattern in video_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    clean_url = match.replace('\\/', '/').replace('\\\\/', '/')
                    if any(x in clean_url for x in ['instagram.com', 'cdninstagram.com', 'fbcdn.net', 'video.cdninstagram.com']):
                        video_url = clean_url
                        print(f"✅ Found video URL: {video_url[:80]}...")
                        break
                if video_url:
                    break
            
            # If no video found in patterns, look for download links
            if not video_url:
                try:
                    download_links = await page.query_selector_all('a[href*=".mp4"], a[href*="cdninstagram"]')
                    if download_links:
                        href = await download_links[0].get_attribute('href')
                        if href:
                            video_url = href.replace('\\/', '/').replace('\\\\/', '/')
                            print(f"✅ Found video in download link: {video_url[:80]}...")
                except Exception:
                    pass
            
            # Get thumbnail
            thumbnail = None
            try:
                thumb_match = re.search(r'<meta property="og:image" content="([^"]+)"', content)
                if thumb_match:
                    thumbnail = thumb_match.group(1)
                    print(f"✅ Found thumbnail")
            except Exception:
                pass
            
            # Get title
            title = None
            try:
                title_match = re.search(r'<meta property="og:title" content="([^"]+)"', content)
                if title_match:
                    title = title_match.group(1)[:100]
                    print(f"✅ Found title")
            except Exception:
                pass
            
            if video_url:
                return {
                    'video_url': video_url,
                    'thumbnail': thumbnail,
                    'title': title,
                    'type': 'video'
                }
            
            print("❌ No video URL found")
            return None
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None
        finally:
            await page.close()
    
    async def _try_direct_embed(self, url: str) -> Optional[Dict]:
        """Fallback: Try Instagram embed URL"""
        shortcode = self._extract_shortcode(url)
        if not shortcode:
            return None
        
        try:
            embed_url = f"https://www.instagram.com/reel/{shortcode}/embed/"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                }
                
                response = await client.get(embed_url, headers=headers, follow_redirects=True)
                
                if response.status_code == 200:
                    html = response.text
                    video_match = re.search(r'"video_url":"([^"]+)"', html)
                    if video_match:
                        video_url = video_match.group(1).replace('\\/', '/').replace('\\u002F', '/')
                        return {'video_url': video_url, 'thumbnail': None, 'title': None, 'type': 'video'}
        except Exception:
            pass
        
        return None
    
    async def get_info(self, url: str) -> Dict[str, Any]:
        """Get Instagram media info"""
        shortcode = self._extract_shortcode(url)
        content_type = self._detect_content_type(url)
        
        if not shortcode:
            return {
                'success': False,
                'error': 'Invalid Instagram URL'
            }
        
        print(f"\n{'='*60}")
        print(f"📸 Downloading Instagram {content_type.value}")
        print(f"🔗 URL: {url}")
        print(f"{'='*60}")
        
        # Method 1: SSSInstagram (main)
        result = await self._download_via_sss(url)
        
        # Method 2: Direct embed (fallback)
        if not result:
            print("⚠️ SSSInstagram failed, trying direct extraction...")
            result = await self._try_direct_embed(url)
        
        if result and result.get('video_url'):
            media_items = [self._create_media_item(
                url=result['video_url'],
                quality='720p',
                format='mp4'
            )]
            
            metadata = self._create_metadata(
                title=result.get('title', f'Instagram {content_type.value}')[:100],
                thumbnail=result.get('thumbnail'),
            )
            
            print(f"\n✅ SUCCESS!")
            print(f"📹 Video URL: {result['video_url'][:100]}...")
            print(f"{'='*60}\n")
            
            return {
                'success': True,
                'platform': 'instagram',
                'content_type': content_type.value,
                'media_type': 'video',
                'title': result.get('title', f'Instagram {content_type.value}')[:50],
                'thumbnail': result.get('thumbnail'),
                'media': media_items,
                'metadata': metadata,
            }
        
        print(f"\n❌ FAILED - Could not extract video\n{'='*60}\n")
        
        return {
            'success': False,
            'error': 'Could not extract Instagram content. This reel may be private, deleted, or the site is temporarily unavailable.'
        }
    
    async def download(self, url: str, format: str = "best") -> Dict[str, Any]:
        """Download Instagram content"""
        return await self.get_info(url)
    
    async def close(self):
        """Clean up resources"""
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
