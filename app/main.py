"""
Universal Media Downloader API - Main Application
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any
import time
from contextlib import asynccontextmanager

from app.config import get_settings
from app.schemas import (
    DownloadRequest,
    DownloadResponse,
    InfoResponse,
    HealthResponse,
    PlatformType,
)
from app.detector import URLDetector
from app.downloaders import (
    YouTubeDownloader,
    InstagramDownloader,
    PinterestDownloader,
    GenericDownloader,
)


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print(f"🚀 Starting Universal Media Downloader API")
    print(f"📍 Host: {settings.host}:{settings.port}")
    print(f"⏱️  Timeout: {settings.request_timeout}s")
    print(f"📦 Max file size: {settings.max_file_size_mb}MB")
    yield
    # Shutdown
    print("👋 Shutting down...")


app = FastAPI(
    title="Universal Media Downloader API",
    description="Download media from YouTube, Instagram, Pinterest, and 1000+ other sites",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate limiting storage (simple in-memory for Railway)
rate_limit_store: Dict[str, list] = {}


def check_rate_limit(client_ip: str) -> bool:
    """Check if client has exceeded rate limit"""
    now = time.time()
    window_start = now - 3600  # 1 hour window
    
    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = []
    
    # Clean old entries
    rate_limit_store[client_ip] = [
        t for t in rate_limit_store[client_ip] if t > window_start
    ]
    
    # Check limit
    if len(rate_limit_store[client_ip]) >= settings.rate_limit:
        return False
    
    # Record this request
    rate_limit_store[client_ip].append(now)
    return True


def get_downloader(platform: PlatformType):
    """Get appropriate downloader for platform"""
    if platform == PlatformType.YOUTUBE:
        return YouTubeDownloader(timeout=settings.request_timeout)
    elif platform == PlatformType.INSTAGRAM:
        return InstagramDownloader(timeout=settings.request_timeout)
    elif platform == PlatformType.PINTEREST:
        return PinterestDownloader(timeout=settings.request_timeout)
    else:
        return GenericDownloader(timeout=settings.request_timeout)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API info"""
    return {
        "name": "Universal Media Downloader API",
        "version": "1.0.0",
        "description": "Download media from YouTube, Instagram, Pinterest, and 1000+ other sites",
        "endpoints": {
            "download": "POST /api/download",
            "info": "GET /api/info",
            "health": "GET /health",
        },
        "supported_platforms": [
            "youtube",
            "instagram",
            "pinterest",
            "tiktok",
            "twitter",
            "facebook",
            "vimeo",
            "and 1000+ more",
        ],
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint for Railway"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        platforms=[
            "youtube",
            "instagram",
            "pinterest",
            "tiktok",
            "twitter",
            "facebook",
            "vimeo",
        ],
    )


@app.post("/api/download", response_model=DownloadResponse, tags=["Download"])
async def download_media(request: DownloadRequest, req: Request):
    """
    Download media from any supported URL
    
    Auto-detects platform and returns direct download links
    """
    # Rate limiting
    client_ip = req.client.host if req.client else "unknown"
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
    
    url = str(request.url)
    
    # Detect platform
    platform, content_type = URLDetector.detect(url)
    
    if platform == PlatformType.UNKNOWN:
        # Try with generic downloader anyway
        platform_name = "unknown"
    else:
        platform_name = platform.value
    
    # Get downloader
    downloader = get_downloader(platform)
    
    # Download
    try:
        result = await downloader.download(url, format=request.format or "best")
        
        if not result.get('success'):
            return DownloadResponse(
                success=False,
                platform=platform_name,
                error=result.get('error', 'Unknown error'),
            )
        
        # Build response
        response = DownloadResponse(
            success=True,
            platform=platform_name,
            content_type=result.get('content_type'),
            media_type=result.get('media_type'),
            title=result.get('title'),
            thumbnail=result.get('thumbnail'),
            media=result.get('media', []),
            metadata=result.get('metadata'),
            processing_time_ms=result.get('processing_time_ms'),
        )
        
        return response
    
    except Exception as e:
        return DownloadResponse(
            success=False,
            platform=platform_name,
            error=str(e),
        )


@app.get("/api/info", response_model=InfoResponse, tags=["Download"])
async def get_media_info(url: str, req: Request):
    """
    Get media info without downloading
    
    Returns metadata and thumbnail without download URLs
    """
    # Rate limiting
    client_ip = req.client.host if req.client else "unknown"
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
    
    # Detect platform
    platform, content_type = URLDetector.detect(url)
    
    if platform == PlatformType.UNKNOWN:
        platform_name = "unknown"
    else:
        platform_name = platform.value
    
    # Get downloader
    downloader = get_downloader(platform)
    
    try:
        result = await downloader.get_info(url)
        
        if not result.get('success'):
            return InfoResponse(
                success=False,
                platform=platform_name,
                error=result.get('error', 'Unknown error'),
            )
        
        return InfoResponse(
            success=True,
            platform=platform_name,
            content_type=result.get('content_type'),
            media_type=result.get('media_type'),
            title=result.get('title'),
            thumbnail=result.get('thumbnail'),
            metadata=result.get('metadata'),
        )
    
    except Exception as e:
        return InfoResponse(
            success=False,
            platform=platform_name,
            error=str(e),
        )


@app.get("/api/supported", tags=["Info"])
async def supported_sites():
    """Get list of supported platforms and sites"""
    return {
        "platforms": {
            "youtube": {
                "name": "YouTube",
                "content_types": ["video", "shorts", "playlist", "live"],
                "requires_login": False,
            },
            "instagram": {
                "name": "Instagram",
                "content_types": ["reel", "post", "story", "highlight", "igtv"],
                "requires_login": False,
                "note": "Login required for private profiles",
            },
            "pinterest": {
                "name": "Pinterest",
                "content_types": ["pin", "video", "image"],
                "requires_login": False,
            },
            "tiktok": {
                "name": "TikTok",
                "content_types": ["video"],
                "requires_login": False,
            },
            "twitter": {
                "name": "Twitter/X",
                "content_types": ["video", "gif"],
                "requires_login": False,
            },
            "facebook": {
                "name": "Facebook",
                "content_types": ["video", "post"],
                "requires_login": False,
                "note": "Public content only",
            },
            "vimeo": {
                "name": "Vimeo",
                "content_types": ["video"],
                "requires_login": False,
            },
            "generic": {
                "name": "1000+ Sites",
                "description": "Via yt-dlp - includes TikTok, Twitter, Facebook, Dailymotion, and many more",
                "requires_login": False,
            },
        },
        "rate_limits": {
            "requests_per_hour": settings.rate_limit,
        },
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": f"Internal server error: {str(exc)}"},
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
