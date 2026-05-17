"""
URL detector - automatically identifies platform from URL
"""
import re
from typing import Tuple, Optional
from app.schemas import PlatformType, ContentTypes


class URLDetector:
    """Detects platform and content type from URL"""
    
    # Platform patterns
    PATTERNS = {
        PlatformType.YOUTUBE: [
            r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})',
            r'youtube\.com\/shorts\/',
            r'youtube\.com\/live\/',
        ],
        PlatformType.INSTAGRAM: [
            r'instagram\.com\/reel\/',
            r'instagram\.com\/p\/',
            r'instagram\.com\/tv\/',
            r'instagram\.com\/stories\/',
            r'instagram\.com\/[^\/]+\/',
        ],
        PlatformType.PINTEREST: [
            r'pinterest\.com\/pin\/',
            r'pinterest\.com\/[^\/]+\/[^\/]+\/',
            r'pin\.it\/',
        ],
        PlatformType.TIKTOK: [
            r'tiktok\.com\/@[^\/]+\/video\/',
            r'tiktok\.com\/t\/',
            r'vm\.tiktok\.com\/',
        ],
        PlatformType.TWITTER: [
            r'twitter\.com\/[^\/]+\/status\/',
            r'x\.com\/[^\/]+\/status\/',
        ],
        PlatformType.FACEBOOK: [
            r'facebook\.com\/.*\/videos\/',
            r'facebook\.com\/.*\/posts\/',
            r'fb\.watch\/',
        ],
        PlatformType.VIMEO: [
            r'vimeo\.com\/',
        ],
    }
    
    # Content type patterns for Instagram
    INSTAGRAM_CONTENT_PATTERNS = {
        ContentTypes.REEL: r'instagram\.com\/reel\/',
        ContentTypes.POST: r'instagram\.com\/p\/',
        ContentTypes.IGTV: r'instagram\.com\/tv\/',
        ContentTypes.STORY: r'instagram\.com\/stories\/',
        ContentTypes.PROFILE: r'instagram\.com\/[^\/]+\/?(?:\?.*)?$',
    }
    
    @classmethod
    def detect_platform(cls, url: str) -> PlatformType:
        """Detect platform from URL"""
        url_lower = url.lower()
        
        for platform, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url_lower):
                    return platform
        
        return PlatformType.UNKNOWN
    
    @classmethod
    def detect_instagram_content_type(cls, url: str) -> ContentTypes:
        """Detect Instagram content type from URL"""
        url_lower = url.lower()
        
        for content_type, pattern in cls.INSTAGRAM_CONTENT_PATTERNS.items():
            if re.search(pattern, url_lower):
                return content_type
        
        return ContentTypes.POST  # Default to post
    
    @classmethod
    def detect(cls, url: str) -> Tuple[PlatformType, Optional[ContentTypes]]:
        """
        Detect platform and content type from URL
        
        Returns:
            Tuple of (PlatformType, ContentTypes or None)
        """
        platform = cls.detect_platform(url)
        content_type = None
        
        if platform == PlatformType.INSTAGRAM:
            content_type = cls.detect_instagram_content_type(url)
        
        return platform, content_type
    
    @classmethod
    def is_supported(cls, url: str) -> bool:
        """Check if URL is from a supported platform"""
        return cls.detect_platform(url) != PlatformType.UNKNOWN
    
    @classmethod
    def extract_video_id(cls, url: str, platform: PlatformType) -> Optional[str]:
        """Extract video/content ID from URL"""
        if platform == PlatformType.YOUTUBE:
            match = re.search(
                r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})',
                url
            )
            return match.group(1) if match else None
        
        elif platform == PlatformType.INSTAGRAM:
            # Extract reel/post ID
            match = re.search(
                r'instagram\.com\/(?:reel|p|tv)\/([^\/\?]+)',
                url
            )
            return match.group(1) if match else None
        
        elif platform == PlatformType.PINTEREST:
            # Extract pin ID
            match = re.search(r'pinterest\.com\/pin\/(\d+)', url)
            if not match:
                match = re.search(r'pin\.it\/([^\/\?]+)', url)
            return match.group(1) if match else None
        
        return None
