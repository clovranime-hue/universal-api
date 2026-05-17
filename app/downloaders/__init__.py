"""
Downloaders for different platforms
"""
from app.downloaders.base import BaseDownloader
from app.downloaders.youtube import YouTubeDownloader
from app.downloaders.instagram import InstagramDownloader
from app.downloaders.pinterest import PinterestDownloader
from app.downloaders.generic import GenericDownloader

__all__ = [
    "BaseDownloader",
    "YouTubeDownloader",
    "InstagramDownloader", 
    "PinterestDownloader",
    "GenericDownloader",
]
