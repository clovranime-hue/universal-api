"""
YouTube downloader using yt-dlp - Optimized for Shorts and regular videos
"""
import asyncio
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import yt_dlp

from app.downloaders.base import BaseDownloader
from app.schemas import PlatformType, MediaItem, MediaMetadata


class YouTubeDownloader(BaseDownloader):
    """Downloader for YouTube videos using yt-dlp"""
    
    def __init__(self, timeout: int = 60):
        super().__init__(timeout)
        self.platform = PlatformType.YOUTUBE
        self.executor = ThreadPoolExecutor(max_workers=3)
    
    def _get_ydl_options(self, format: str = "best") -> Dict:
        """Get yt-dlp options optimized for YouTube & Shorts"""
        return {
            'format': format,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'socket_timeout': self.timeout,
            'retries': 3,
            'noprogress': True,
            'nocheckcertificate': True,
            # YouTube-specific options for better compatibility
            'extractor_args': {
                'youtube': {
                    'player_client': ['web', 'ios', 'android'],  # Multiple clients
                }
            },
            # Better error handling
            'ignoreerrors': False,
        }
    
    def _create_media_item(self, url: str, quality: str = "best", format: str = "mp4", 
                           size_mb: Optional[float] = None, duration: Optional[int] = None) -> MediaItem:
        """Create a media item with proper formatting"""
        return MediaItem(
            url=url,
            quality=quality or "best",
            format=format or "mp4",
            size_mb=round(size_mb, 2) if size_mb else None,
            duration=duration
        )
    
    def _extract_info(self, info: Dict) -> Dict[str, Any]:
        """Extract standardized info from yt-dlp result"""
        if not info:
            return {
                'success': False,
                'error': 'No video info returned'
            }
        
        media_items = []
        
        # Try to get direct video URL
        if info.get('url'):
            media_items.append(self._create_media_item(
                url=info['url'],
                quality=info.get('resolution', info.get('format_note', 'best')),
                format=info.get('ext', 'mp4'),
                size_mb=info.get('filesize_approx', 0) / (1024 * 1024) if info.get('filesize_approx') else None,
                duration=info.get('duration')
            ))
        
        # Also check formats array
        if not media_items and info.get('formats'):
            formats = info.get('formats', [])
            # Get best format with URL
            for fmt in reversed(formats):
                if fmt.get('url') and fmt.get('vcodec') != 'none':
                    media_items.append(self._create_media_item(
                        url=fmt['url'],
                        quality=fmt.get('resolution', fmt.get('format_note', 'best')),
                        format=fmt.get('ext', 'mp4'),
                        size_mb=fmt.get('filesize_approx', 0) / (1024 * 1024) if fmt.get('filesize_approx') else None,
                        duration=fmt.get('duration')
                    ))
                    break
        
        # Get thumbnail
        thumbnail = None
        if info.get('thumbnail'):
            thumbnail = info['thumbnail']
        elif info.get('thumbnails'):
            thumbnails = info.get('thumbnails', [])
            if thumbnails:
                thumbnail = thumbnails[-1].get('url')
        
        metadata = {
            'title': info.get('title'),
            'description': (info.get('description', '')[:500] if info.get('description') else None),
            'author': info.get('uploader'),
            'author_url': info.get('uploader_url'),
            'thumbnail': thumbnail,
            'views': info.get('view_count'),
            'likes': info.get('like_count'),
            'duration': info.get('duration'),
            'upload_date': info.get('upload_date')
        }
        
        return {
            'success': True,
            'platform': 'youtube',
            'content_type': info.get('_type', 'video'),
            'media_type': 'video',
            'title': info.get('title', 'YouTube Video'),
            'thumbnail': thumbnail,
            'media': media_items,
            'metadata': metadata,
        }
    
    async def _run_ydl(self, url: str, options: Dict) -> Dict:
        """Run yt-dlp in thread pool"""
        loop = asyncio.get_event_loop()
        
        def _extract():
            try:
                with yt_dlp.YoutubeDL(options) as ydl:
                    return ydl.extract_info(url, download=False)
            except yt_dlp.utils.DownloadError as e:
                return {'error': str(e)}
            except Exception as e:
                return {'error': f'Unexpected error: {str(e)}'}
        
        return await loop.run_in_executor(self.executor, _extract)
    
    async def get_info(self, url: str) -> Dict[str, Any]:
        """Get video info without downloading"""
        try:
            options = self._get_ydl_options()
            info = await self._run_ydl(url, options)
            
            # Check for errors
            if not info:
                return {
                    'success': False,
                    'error': 'Failed to extract video info - empty response'
                }
            
            if info.get('error'):
                return {
                    'success': False,
                    'error': info['error']
                }
            
            return self._extract_info(info)
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Extractor error: {str(e)}'
            }
    
    async def download(self, url: str, format: str = "best") -> Dict[str, Any]:
        """Download video and return download URLs"""
        return await self.get_info(url)
