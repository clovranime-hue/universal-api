"""
Base downloader class
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import time
from app.schemas import MediaItem, MediaMetadata, PlatformType


class BaseDownloader(ABC):
    """Abstract base class for all downloaders"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.platform: PlatformType = PlatformType.UNKNOWN
    
    @abstractmethod
    async def get_info(self, url: str) -> Dict[str, Any]:
        """Get media info without downloading"""
        pass
    
    @abstractmethod
    async def download(self, url: str, format: str = "best") -> Dict[str, Any]:
        """Download media and return download URLs"""
        pass
    
    def _create_media_item(
        self,
        url: str,
        quality: Optional[str] = None,
        format: Optional[str] = None,
        size_mb: Optional[float] = None,
        duration: Optional[int] = None
    ) -> MediaItem:
        """Create a MediaItem instance"""
        return MediaItem(
            url=url,
            quality=quality,
            format=format,
            size_mb=size_mb,
            duration=duration
        )
    
    def _create_metadata(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        author: Optional[str] = None,
        author_url: Optional[str] = None,
        thumbnail: Optional[str] = None,
        views: Optional[int] = None,
        likes: Optional[int] = None,
        duration: Optional[int] = None,
        upload_date: Optional[str] = None
    ) -> MediaMetadata:
        """Create a MediaMetadata instance"""
        return MediaMetadata(
            title=title,
            description=description,
            author=author,
            author_url=author_url,
            thumbnail=thumbnail,
            views=views,
            likes=likes,
            duration=duration,
            upload_date=upload_date
        )
    
    def _measure_time(self, func):
        """Decorator to measure execution time"""
        async def wrapper(*args, **kwargs):
            start = time.time()
            result = await func(*args, **kwargs)
            end = time.time()
            result['processing_time_ms'] = int((end - start) * 1000)
            return result
        return wrapper
