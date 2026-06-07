from fastapi import Request
from fastapi.responses import JSONResponse
import time
import hashlib

class CacheMiddleware:
    """Simple in-memory cache middleware for FastAPI"""
    
    def __init__(self, app, cache_ttl: int = 300):
        self.app = app
        self.cache = {}
        self.cache_ttl = cache_ttl  # seconds
        
    async def __call__(self, scope, receive):
        if scope["type"] != "http":
            await self.app(scope, receive)
            return
            
        request = Request(scope, receive)
        
        # Skip POST, PUT, DELETE, and admin routes
        if request.method != "GET" or "/admin" in request.url.path:
            await self.app(scope, receive)
            return
            
        # Generate cache key
        cache_key = self._generate_cache_key(request)
        
        # Check cache
        if cache_key in self.cache:
            cached_time, cached_response = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                # Return cached response
                response = JSONResponse(content=cached_response)
                response.headers["X-Cache"] = "HIT"
                await response(scope, receive)
                return
        
        # Process request
        # (simplified - would need proper ASGI handling)
        await self.app(scope, receive)
    
    def _generate_cache_key(self, request: Request) -> str:
        url = str(request.url)
        return hashlib.md5(url.encode()).hexdigest()


def generate_cache_key(url: str) -> str:
    """Generate a simple cache key from URL"""
    return hashlib.md5(url.encode()).hexdigest()