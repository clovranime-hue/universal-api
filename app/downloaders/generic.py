"""
Generic downloader using yt-dlp for 1000+ supported sites
"""
import asyncio
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor
import yt_dlp

from app.downloaders.base import BaseDownloader
from app.schemas import PlatformType, MediaItem, MediaMetadata


class GenericDownloader(BaseDownloader):
    """Generic downloader using yt-dlp for supported sites"""
    
    def __init__(self, timeout: int = 30):
        super().__init__(timeout)
        self.platform = PlatformType.UNKNOWN
        self.executor = ThreadPoolExecutor(max_workers=3)
    
    def _get_ydl_options(self, format: str = "best") -> Dict:
        """Get yt-dlp options"""
        return {
            'format': format,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'socket_timeout': self.timeout,
            'retries': 3,
            'noprogress': True,
            'ignoreerrors': True,
        }
    
    def _extract_info(self, info: Dict, platform: str = "unknown") -> Dict[str, Any]:
        """Extract standardized info from yt-dlp result"""
        media_items = []
        
        # Get media URL
        if info.get('url'):
            media_items.append(self._create_media_item(
                url=info['url'],
                quality=info.get('resolution', info.get('format_note', 'unknown')),
                format=info.get('ext', 'mp4'),
                size_mb=info.get('filesize_approx', 0) / (1024 * 1024) if info.get('filesize_approx') else None,
                duration=info.get('duration')
            ))
        elif info.get('formats'):
            # Get best format
            formats = sorted(
                [f for f in info['formats'] if f.get('url')],
                key=lambda x: x.get('filesize_approx', 0) or 0,
                reverse=True
            )
            
            if formats:
                best = formats[0]
                media_items.append(self._create_media_item(
                    url=best['url'],
                    quality=best.get('resolution', best.get('format_note', 'unknown')),
                    format=best.get('ext', 'mp4'),
                    size_mb=best.get('filesize_approx', 0) / (1024 * 1024) if best.get('filesize_approx') else None,
                    duration=best.get('duration')
                ))
        
        # Determine media type
        media_type = 'video'
        if info.get('vcodec') == 'none' and info.get('acodec') != 'none':
            media_type = 'audio'
        elif info.get('vcodec') == 'none' and info.get('acodec') == 'none':
            media_type = 'image'
        
        # Get thumbnail
        thumbnail = info.get('thumbnail')
        if not thumbnail and info.get('thumbnails'):
            thumbnails = info['thumbnails']
            if thumbnails:
                thumbnail = thumbnails[-1].get('url')
        
        metadata = self._create_metadata(
            title=info.get('title'),
            description=info.get('description', '')[:500] if info.get('description') else None,
            author=info.get('uploader'),
            author_url=info.get('uploader_url'),
            thumbnail=thumbnail,
            views=info.get('view_count'),
            likes=info.get('like_count'),
            duration=info.get('duration'),
            upload_date=info.get('upload_date')
        )
        
        return {
            'success': True,
            'platform': platform,
            'content_type': 'media',
            'media_type': media_type,
            'title': info.get('title'),
            'thumbnail': thumbnail,
            'media': media_items,
            'metadata': metadata,
        }
    
    async def _run_ydl(self, url: str, options: Dict) -> Dict:
        """Run yt-dlp in thread pool"""
        loop = asyncio.get_event_loop()
        
        def _extract():
            with yt_dlp.YoutubeDL(options) as ydl:
                return ydl.extract_info(url, download=False)
        
        return await loop.run_in_executor(self.executor, _extract)
    
    async def get_info(self, url: str, platform: str = "unknown") -> Dict[str, Any]:
        """Get media info"""
        try:
            options = self._get_ydl_options()
            info = await self._run_ydl(url, options)
            
            if not info:
                return {
                    'success': False,
                    'error': 'Failed to extract media info'
                }
            
            return self._extract_info(info, platform)
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def download(self, url: str, format: str = "best", platform: str = "unknown") -> Dict[str, Any]:
        """Download media"""
        return await self.get_info(url, platform)
