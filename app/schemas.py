"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from enum import Enum


class PlatformType(str, Enum):
    """Supported platforms"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    PINTEREST = "pinterest"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    VIMEO = "vimeo"
    UNKNOWN = "unknown"


class MediaType(str, Enum):
    """Media types"""
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    MIXED = "mixed"


class ContentTypes(str, Enum):
    """Instagram content types"""
    REEL = "reel"
    POST = "post"
    STORY = "story"
    HIGHLIGHT = "highlight"
    IGTV = "igtv"
    PROFILE = "profile"


class MediaItem(BaseModel):
    """Individual media item"""
    url: str = Field(..., description="Direct download URL")
    quality: Optional[str] = Field(None, description="Quality (e.g., 720p, 1080p)")
    format: Optional[str] = Field(None, description="File format (mp4, jpg, etc.)")
    size_mb: Optional[float] = Field(None, description="File size in MB")
    duration: Optional[int] = Field(None, description="Duration in seconds (for video/audio)")


class MediaMetadata(BaseModel):
    """Media metadata"""
    title: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    author_url: Optional[str] = None
    thumbnail: Optional[str] = None
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    upload_date: Optional[str] = None
    duration: Optional[int] = None


class DownloadRequest(BaseModel):
    """Download request schema"""
    url: HttpUrl = Field(..., description="Media URL to download")
    format: Optional[str] = Field("best", description="Format preference (best, mp4, mp3, etc.)")
    quality: Optional[str] = Field(None, description="Quality preference (720p, 1080p, etc.)")


class DownloadResponse(BaseModel):
    """Download response schema"""
    success: bool = Field(..., description="Whether the request succeeded")
    platform: str = Field(..., description="Detected platform")
    content_type: Optional[str] = Field(None, description="Content type (reel, post, video, etc.)")
    media_type: Optional[str] = Field(None, description="Media type (video, image, etc.)")
    title: Optional[str] = Field(None, description="Media title")
    thumbnail: Optional[str] = Field(None, description="Thumbnail URL")
    media: List[MediaItem] = Field(default_factory=list, description="Download URLs")
    metadata: Optional[MediaMetadata] = Field(None, description="Media metadata")
    error: Optional[str] = Field(None, description="Error message if failed")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")


class InfoResponse(BaseModel):
    """Media info response (without download URLs)"""
    success: bool
    platform: str
    content_type: Optional[str]
    media_type: Optional[str]
    title: Optional[str]
    thumbnail: Optional[str]
    metadata: Optional[MediaMetadata]
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str = "1.0.0"
    platforms: List[str] = [
        "youtube",
        "instagram", 
        "pinterest",
        "tiktok",
        "twitter",
        "facebook",
        "vimeo"
    ]
