"""
Pinterest downloader - Updated with better extraction methods
"""
import asyncio
import re
import json
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import httpx

from app.downloaders.base import BaseDownloader
from app.schemas import PlatformType, MediaItem, MediaMetadata


class PinterestDownloader(BaseDownloader):
    """Downloader for Pinterest pins"""
    
    def __init__(self, timeout: int = 60):
        super().__init__(timeout)
        self.platform = PlatformType.PINTEREST
        self.executor = ThreadPoolExecutor(max_workers=3)
    
    async def _extract_from_page(self, url: str) -> Optional[Dict]:
        """Extract media from Pinterest page HTML"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
                
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    html = response.text
                    
                    # Look for Pinterest embedded data
                    # Pinterest stores data in <script> tags with id="__PWS_DATA__"
                    data_match = re.search(r'<script id="__PWS_DATA__" type="application/json">({.+?})</script>', html, re.DOTALL)
                    
                    if data_match:
                        try:
                            pws_data = json.loads(data_match.group(1))
                            
                            # Navigate the Pinterest data structure
                            resource_response = pws_data.get('resource_response', {})
                            data = resource_response.get('data', {})
                            
                            # Try to get video
                            if data.get('video_status') == 'published' or data.get('is_video'):
                                video_list = data.get('video_list', {})
                                # Try different quality levels
                                for quality in ['V_720p', 'V_480p', 'V_360p']:
                                    if quality in video_list:
                                        video_url = video_list[quality].get('url')
                                        if video_url:
                                            return {
                                                'video_url': video_url,
                                                'thumbnail': data.get('image_large_url') or data.get('images', {}).get('700x', {}).get('url'),
                                                'title': data.get('title'),
                                                'type': 'video'
                                            }
                                
                                video_url = data.get('video_url')
                                if video_url:
                                    return {
                                        'video_url': video_url,
                                        'thumbnail': data.get('image_large_url') or data.get('images', {}).get('700x', {}).get('url'),
                                        'title': data.get('title'),
                                        'type': 'video'
                                    }
                            
                            # Try to get image
                            image_url = data.get('image_large_url') or data.get('images', {}).get('700x', {}).get('url')
                            if image_url:
                                return {
                                    'image_url': image_url,
                                    'thumbnail': image_url,
                                    'title': data.get('title'),
                                    'type': 'image'
                                }
                        except json.JSONDecodeError:
                            pass
                    
                    # Fallback: Try meta tags
                    # Video URL
                    video_match = re.search(r'<meta property="og:video" content="([^"]+)"', html)
                    if video_match:
                        video_url = video_match.group(1).replace('\\u002F', '/')
                        
                        thumb_match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
                        title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html)
                        
                        return {
                            'video_url': video_url,
                            'thumbnail': thumb_match.group(1) if thumb_match else None,
                            'title': title_match.group(1) if title_match else None,
                            'type': 'video'
                        }
                    
                    # Image URL from Open Graph
                    image_match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
                    if image_match:
                        image_url = image_match.group(1)
                        title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html)
                        
                        return {
                            'image_url': image_url,
                            'thumbnail': image_url,
                            'title': title_match.group(1) if title_match else None,
                            'type': 'image'
                        }
                    
                    # Try Pinterest video URLs (v1.pinimg.com or v.pinimg.com)
                    video_matches = re.findall(r'https://v[0-9]*\.pinimg\.com/videos/[^"\s\']+\.mp4', html)
                    if video_matches:
                        # Get best quality video
                        video_url = video_matches[0]
                        # Also try to find better quality
                        for v in video_matches:
                            if '_720w.mp4' in v or '720p' in v:
                                video_url = v
                                break
                        
                        thumb_match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
                        title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html)
                        
                        return {
                            'video_url': video_url,
                            'thumbnail': thumb_match.group(1) if thumb_match else None,
                            'title': title_match.group(1).replace(' - Pinterest', '') if title_match else None,
                            'type': 'video'
                        }
                    
                    # Try Pinterest CDN image URLs
                    cdn_matches = re.findall(r'https://i\.pinimg\.com/[^"\s\']+\.(jpg|jpeg|png)', html)
                    if cdn_matches:
                        # Get the highest resolution image (736x is usually good)
                        image_url = cdn_matches[0]
                        title_match = re.search(r'<title>([^<]+)</title>', html)
                        
                        return {
                            'image_url': image_url,
                            'thumbnail': image_url,
                            'title': title_match.group(1).replace(' - Pinterest', '') if title_match else None,
                            'type': 'image'
                        }
                        
        except Exception as e:
            print(f"Pinterest extraction error: {e}")
        
        return None
    
    def _create_response(self, data: Dict, url: str) -> Dict[str, Any]:
        """Create standardized response"""
        media_items = []
        media_type = 'image'
        
        if data.get('video_url'):
            media_items.append(self._create_media_item(
                url=data['video_url'],
                quality='720p',
                format='mp4'
            ))
            media_type = 'video'
        elif data.get('image_url'):
            media_items.append(self._create_media_item(
                url=data['image_url'],
                format='jpg'
            ))
        
        metadata = self._create_metadata(
            title=data.get('title'),
            thumbnail=data.get('thumbnail'),
        )
        
        return {
            'success': True,
            'platform': 'pinterest',
            'content_type': 'pin',
            'media_type': media_type,
            'title': data.get('title', 'Pinterest Pin'),
            'thumbnail': data.get('thumbnail'),
            'media': media_items,
            'metadata': metadata,
        }
    
    async def get_info(self, url: str) -> Dict[str, Any]:
        """Get Pinterest pin info"""
        try:
            # Try page extraction (most reliable method)
            data = await self._extract_from_page(url)
            
            if data:
                return self._create_response(data, url)
            
            return {
                'success': False,
                'error': 'Could not extract Pinterest pin data - pin may be private or deleted'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Pinterest error: {str(e)}'
            }
    
    async def download(self, url: str, format: str = "best") -> Dict[str, Any]:
        """Download Pinterest pin"""
        return await self.get_info(url)
