"""
SSSInstagram.com downloader - Browser automation
This automates the sssinstagram.com website to download Instagram content
"""
import asyncio
import re
import time
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page
import tempfile
import os

from app.downloaders.base import BaseDownloader
from app.schemas import PlatformType, ContentTypes, MediaItem, MediaMetadata


class SSSInstagramDownloader(BaseDownloader):
    """
    Automates sssinstagram.com website for Instagram downloads
    
    This uses browser automation to interact with sssinstagram.com,
    which provides free Instagram downloads without authentication.
    
    Pros:
    - Free, no API key needed
    - No Instagram login required
    - Works for reels, posts, IGTV
    
    Cons:
    - Slower than direct API (5-10 seconds)
    - Requires browser (Playwright)
    - Site may change and break automation
    """
    
    SITE_URL = "https://sssinstagram.com"
    
    def __init__(self, timeout: int = 30, headless: bool = True):
        super().__init__(timeout)
        self.platform = PlatformType.INSTAGRAM
        self.headless = headless
        self.browser: Optional[Browser] = None
    
    async def _get_browser(self) -> Browser:
        """Get or create browser instance"""
        if self.browser is None:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--disable-gpu',
                ]
            )
        return self.browser
    
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
    
    async def _download_via_sss(self, url: str) -> Optional[Dict]:
        """
        Download via sssinstagram.com using browser automation
        """
        browser = await self._get_browser()
        page = await browser.new_page()
        
        try:
            # Set realistic user agent
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            })
            
            # Navigate to sssinstagram.com
            await page.goto(self.SITE_URL, wait_until='networkidle', timeout=self.timeout * 1000)
            
            # Wait for page to fully load
            await page.wait_for_timeout(2000)
            
            # Find and fill the input field
            # SSSInstagram typically has an input with placeholder like "Paste Instagram link here"
            input_selectors = [
                'input[placeholder*="link"]',
                'input[placeholder*="URL"]',
                'input[placeholder*="instagram"]',
                'input[type="url"]',
                'input.form-control',
            ]
            
            input_element = None
            for selector in input_selectors:
                try:
                    input_element = await page.query_selector(selector)
                    if input_element:
                        break
                except Exception:
                    continue
            
            if not input_element:
                # Try to find any input field
                input_element = await page.query_selector('input')
            
            if input_element:
                await input_element.fill(url)
            else:
                # If no input found, try direct URL navigation
                await page.goto(f"{self.SITE_URL}/en?url={url}", wait_until='networkidle', timeout=self.timeout * 1000)
            
            # Click download button
            download_selectors = [
                'button:has-text("Download")',
                'button:has-text("download")',
                'input[type="submit"]',
                '.download-btn',
                'button.btn-primary',
            ]
            
            download_clicked = False
            for selector in download_selectors:
                try:
                    download_btn = await page.query_selector(selector)
                    if download_btn:
                        await download_btn.click()
                        download_clicked = True
                        break
                except Exception:
                    continue
            
            # Wait for results - extended wait time
            await page.wait_for_timeout(5000)
            
            # Look for video URL in the page
            # SSSInstagram typically shows download links after processing
            page_content = await page.content()
            
            # Extract video URLs from the page - Updated patterns
            video_patterns = [
                # Direct MP4 URLs
                r'"(https://[^"\s]+\.mp4[^"]*)"',
                # Instagram CDN URLs
                r'(https://[a-zA-Z0-9.-]+cdninstagram\.com[^\s"\'<>()]+)',
                # Facebook CDN URLs
                r'(https://[a-zA-Z0-9.-]+fbcdn\.net[^\s"\'<>()]+)',
                # Data-href attributes
                r'data-href="([^"]+\.mp4[^"]+)"',
                # href in download links
                r'href="(https://[^"]+\.mp4[^"]+)"',
            ]
            
            video_url = None
            for pattern in video_patterns:
                matches = re.findall(pattern, page_content, re.IGNORECASE)
                if matches:
                    # Filter for Instagram CDN URLs
                    for match in matches:
                        clean_url = match.replace('\\/', '/').replace('&amp;', '&')
                        if any(x in clean_url for x in ['instagram.com', 'cdninstagram.com', 'fbcdn.net', 'scontent']):
                            video_url = clean_url
                            break
                    if video_url:
                        break
            
            if video_url:
                # Try to get thumbnail
                thumb_match = re.search(
                    r'<meta property="og:image" content="([^"]+)"',
                    page_content
                )
                thumbnail = thumb_match.group(1) if thumb_match else None
                
                # Try to get title
                title_match = re.search(
                    r'<meta property="og:title" content="([^"]+)"',
                    page_content
                )
                title = title_match.group(1) if title_match else None
                
                return {
                    'video_url': video_url,
                    'thumbnail': thumbnail,
                    'title': title,
                    'type': 'video'
                }
            
            # Try to find download button link
            download_links = await page.query_selector_all('a[href*=".mp4"], a[href*="cdninstagram.com"], a[href*="fbcdn.net"]')
            if download_links:
                href = await download_links[0].get_attribute('href')
                if href:
                    return {
                        'video_url': href.replace('\\/', '/').replace('&amp;', '&'),
                        'thumbnail': None,
                        'title': None,
                        'type': 'video'
                    }
            
            # Try to find video in download buttons with data attributes
            video_buttons = await page.query_selector_all('button[data-url*="mp4"], a[data-href*="mp4"]')
            if video_buttons:
                for btn in video_buttons:
                    data_url = await btn.get_attribute('data-url') or await btn.get_attribute('data-href')
                    if data_url and 'mp4' in data_url:
                        return {
                            'video_url': data_url.replace('\\/', '/').replace('&amp;', '&'),
                            'thumbnail': None,
                            'title': None,
                            'type': 'video'
                        }
            
            # Try to find video in JSON data embedded in page
            json_matches = re.findall(r'"video_versions":\s*\[([^\]]+)\]', page_content)
            if json_matches:
                for match in json_matches:
                    # Extract URL from JSON
                    url_match = re.search(r'"url":\s*"([^"]+)"', match)
                    if url_match:
                        video_url = url_match.group(1).replace('\\/', '/')
                        if any(x in video_url for x in ['instagram.com', 'cdninstagram.com', 'scontent']):
                            return {
                                'video_url': video_url,
                                'thumbnail': None,
                                'title': None,
                                'type': 'video'
                            }
            
            # Try to find video in meta tags
            video_meta = re.search(r'<meta property="og:video" content="([^"]+)"', page_content)
            if video_meta:
                video_url = video_meta.group(1).replace('\\/', '/')
                return {
                    'video_url': video_url,
                    'thumbnail': None,
                    'title': None,
                    'type': 'video'
                }
            
            return None
            
        except Exception as e:
            print(f"SSSInstagram error: {e}")
            return None
        finally:
            if page:
                await page.close()
    
    async def _download_via_direct(self, url: str) -> Optional[Dict]:
        """
        Alternative: Direct extraction from Instagram embed
        (Fallback if sssinstagram.com fails)
        """
        import httpx
        
        shortcode = self._extract_shortcode(url)
        if not shortcode:
            return None
        
        # Try multiple endpoints for better success rate
        endpoints = [
            f"https://www.instagram.com/reel/{shortcode}/",
            f"https://www.instagram.com/p/{shortcode}/",
            f"https://www.instagram.com/reel/{shortcode}/embed/",
        ]
        
        for embed_url in endpoints:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                    }
                    
                    response = await client.get(embed_url, headers=headers, follow_redirects=True)
                    
                    if response.status_code == 200:
                        html = response.text
                        
                        # Look for video URL in various formats
                        video_patterns = [
                            r'"video_url":"([^"]+)"',
                            r'"video_versions":\[\{\s*"url":"([^"]+)"',
                            r'"dash_url":"([^"]+)"',
                        ]
                        
                        for pattern in video_patterns:
                            match = re.search(pattern, html)
                            if match:
                                video_url = match.group(1).replace('\\/', '/')
                                return {
                                    'video_url': video_url,
                                    'thumbnail': None,
                                    'title': None,
                                    'type': 'video'
                                }
            except Exception:
                continue
        
        return None
                    if video_match:
                        video_url = video_match.group(1).replace('\\/', '/').replace('\\u002F', '/')
                        
                        thumb_match = re.search(r'"display_url":"([^"]+)"', html)
                        thumbnail = thumb_match.group(1).replace('\\/', '/').replace('\\u002F', '/') if thumb_match else None
                        
                        return {
                            'video_url': video_url,
                            'thumbnail': thumbnail,
                            'title': None,
                            'type': 'video'
                        }
        except Exception:
            pass
        
        return None
    
    async def get_info(self, url: str) -> Dict[str, Any]:
        """Get Instagram media info via SSSInstagram"""
        shortcode = self._extract_shortcode(url)
        content_type = self._detect_content_type(url)
        
        if not shortcode:
            return {
                'success': False,
                'error': 'Invalid Instagram URL'
            }
        
        # Method 1: Browser automation (most reliable)
        result = await self._download_via_sss(url)
        
        # Method 2: Direct extraction (fallback)
        if not result:
            result = await self._download_via_direct(url)
        
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
        
        return {
            'success': False,
            'error': 'Could not extract Instagram content. This reel may be private or deleted.'
        }
    
    async def download(self, url: str, format: str = "best") -> Dict[str, Any]:
        """Download Instagram content"""
        return await self.get_info(url)
    
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
            self.browser = None
