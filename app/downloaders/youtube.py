"""
YouTube downloader using yt-dlp
"""
import asyncio
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import yt_dlp

from app.downloaders.base import BaseDownloader
from app.schemas import PlatformType, MediaItem, MediaMetadata


class YouTubeDownloader(BaseDownloader):
    """Downloader for YouTube videos using yt-dlp"""
    
    def __init__(self, timeout: int = 30):
        super().__init__(timeout)
        self.platform = PlatformType.YOUTUBE
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
    
    def _extract_info(self, info: Dict) -> Dict[str, Any]:
        """Extract standardized info from yt-dlp result"""
        media_items = []
        
        # Get best video format
        if info.get('url'):
            # Direct URL available
            media_items.append(self._create_media_item(
                url=info['url'],
                quality=info.get('resolution', 'unknown'),
                format=info.get('ext', 'mp4'),
                size_mb=info.get('filesize_approx', 0) / (1024 * 1024) if info.get('filesize_approx') else None,
                duration=info.get('duration')
            ))
        elif info.get('formats'):
            # Multiple formats available - get best video and audio
            formats = info['formats']
            
            # Sort by quality
            video_formats = [f for f in formats if f.get('vcodec') != 'none']
            audio_formats = [f for f in formats if f.get('acodec') != 'none']
            
            # Get best combined or separate streams
            if info.get('requested_formats'):
                for fmt in info['requested_formats']:
                    if fmt.get('url'):
                        media_items.append(self._create_media_item(
                            url=fmt['url'],
                            quality=fmt.get('resolution', fmt.get('format_note', 'unknown')),
                            format=fmt.get('ext', 'mp4'),
                            size_mb=fmt.get('filesize_approx', 0) / (1024 * 1024) if fmt.get('filesize_approx') else None,
                            duration=fmt.get('duration')
                        ))
        
        metadata = self._create_metadata(
            title=info.get('title'),
            description=info.get('description', '')[:500] if info.get('description') else None,
            author=info.get('uploader'),
            author_url=info.get('uploader_url'),
            thumbnail=info.get('thumbnail') or info.get('thumbnails', [{}])[-1].get('url') if info.get('thumbnails') else None,
            views=info.get('view_count'),
            likes=info.get('like_count'),
            duration=info.get('duration'),
            upload_date=info.get('upload_date')
        )
        
        return {
            'success': True,
            'platform': 'youtube',
            'content_type': 'video',
            'media_type': 'video',
            'title': info.get('title'),
            'thumbnail': metadata.thumbnail,
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
    
    async def get_info(self, url: str) -> Dict[str, Any]:
        """Get video info without downloading"""
        try:
            options = self._get_ydl_options()
            info = await self._run_ydl(url, options)
            
            if not info:
                return {
                    'success': False,
                    'error': 'Failed to extract video info'
                }
            
            return self._extract_info(info)
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def download(self, url: str, format: str = "best") -> Dict[str, Any]:
        """Download video and return download URLs"""
        return await self.get_info(url)
