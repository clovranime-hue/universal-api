"""
Pinterest downloader
"""
import asyncio
import re
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import httpx

from app.downloaders.base import BaseDownloader
from app.schemas import PlatformType, MediaItem, MediaMetadata


class PinterestDownloader(BaseDownloader):
    """Downloader for Pinterest pins"""
    
    def __init__(self, timeout: int = 30):
        super().__init__(timeout)
        self.platform = PlatformType.PINTEREST
        self.executor = ThreadPoolExecutor(max_workers=3)
    
    async def _extract_pin_id(self, url: str) -> Optional[str]:
        """Extract pin ID from URL"""
        # Try different Pinterest URL patterns
        patterns = [
            r'pinterest\.com\/pin\/(\d+)',
            r'pin\.it\/([a-zA-Z0-9]+)',
            r'pinterest\.com\/pin\/[^\/]+\/(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    async def _fetch_pin_data(self, pin_id: str) -> Optional[Dict]:
        """Fetch pin data from Pinterest API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Pinterest's public API endpoint for pin data
                url = f"https://api.pinterest.com/v3/pidgets/pins/info/?pin_ids={pin_id}"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                }
                
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get('pinned_response', {}).get('data')
        except Exception:
            pass
        
        return None
    
    async def _extract_from_page(self, url: str) -> Optional[Dict]:
        """Extract media from Pinterest page HTML"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                }
                
                response = await client.get(url, headers=headers, follow_redirects=True)
                
                if response.status_code == 200:
                    html = response.text
                    
                    # Try to find video URL
                    video_patterns = [
                        r'"contentUrl":"([^"]+\.mp4[^"]*)"',
                        r'"video_url":"([^"]+)"',
                        r'<meta property="og:video" content="([^"]+)"',
                    ]
                    
                    for pattern in video_patterns:
                        match = re.search(pattern, html)
                        if match:
                            video_url = match.group(1).replace('\\u002F', '/')
                            
                            # Find thumbnail
                            thumb_match = re.search(
                                r'<meta property="og:image" content="([^"]+)"',
                                html
                            )
                            thumbnail = thumb_match.group(1) if thumb_match else None
                            
                            # Find title
                            title_match = re.search(
                                r'<meta property="og:title" content="([^"]+)"',
                                html
                            )
                            title = title_match.group(1) if title_match else None
                            
                            return {
                                'video_url': video_url,
                                'thumbnail': thumbnail,
                                'title': title,
                                'type': 'video'
                            }
                    
                    # Try to find image URL
                    image_patterns = [
                        r'<meta property="og:image" content="([^"]+)"',
                        r'"imageUrl":"([^"]+)"',
                    ]
                    
                    for pattern in image_patterns:
                        match = re.search(pattern, html)
                        if match:
                            image_url = match.group(1).replace('\\u002F', '/')
                            
                            title_match = re.search(
                                r'<meta property="og:title" content="([^"]+)"',
                                html
                            )
                            title = title_match.group(1) if title_match else None
                            
                            return {
                                'image_url': image_url,
                                'thumbnail': image_url,
                                'title': title,
                                'type': 'image'
                            }
        except Exception:
            pass
        
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
            # Extract pin ID
            pin_id = await self._extract_pin_id(url)
            
            if pin_id:
                # Try API first
                data = await self._fetch_pin_data(pin_id)
                if data:
                    pins = data.get('pins', [])
                    if pins:
                        pin_data = pins[0].get('pinned_description', {})
                        return self._create_response({
                            'title': pin_data.get('title'),
                            'thumbnail': pin_data.get('image_large_url'),
                            'video_url': pin_data.get('video_url'),
                        }, url)
            
            # Fallback to page extraction
            data = await self._extract_from_page(url)
            if data:
                return self._create_response(data, url)
            
            return {
                'success': False,
                'error': 'Could not extract Pinterest pin data'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def download(self, url: str, format: str = "best") -> Dict[str, Any]:
        """Download Pinterest pin"""
        return await self.get_info(url)
