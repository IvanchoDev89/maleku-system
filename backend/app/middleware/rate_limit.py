"""Rate limiting middleware with Redis-like memory storage."""
import time
from typing import Dict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_client_ip(request: Request) -> str:
    """Resolve the real client IP, honoring X-Forwarded-For / X-Real-IP.

    Behind a load balancer or reverse proxy, ``request.client.host`` points to
    the proxy itself, which would lump every visitor into the same bucket.
    """
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting by IP address."""

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        # In-memory storage: {ip: [timestamp, ...]}
        self.requests: Dict[str, list] = {}
        self.blocked_ips: Dict[str, float] = {}  # ip: unblock_time

    async def dispatch(self, request: Request, call_next):
        client_ip = get_client_ip(request)
        current_time = time.time()

        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            if current_time < self.blocked_ips[client_ip]:
                logger.warning(f"Blocked request from {client_ip}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please try again later."
                )
            else:
                del self.blocked_ips[client_ip]
                self.requests[client_ip] = []

        # Clean old requests (older than 60 seconds)
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if current_time - req_time < 60
            ]
        else:
            self.requests[client_ip] = []

        # Check rate limit
        request_count = len(self.requests[client_ip])
        if request_count >= self.requests_per_minute:
            # Block IP for 5 minutes
            self.blocked_ips[client_ip] = current_time + 300
            logger.warning(f"Rate limit exceeded for {client_ip}. Blocked for 5 minutes.")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again in 5 minutes."
            )

        # Record request
        self.requests[client_ip].append(current_time)

        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, self.requests_per_minute - len(self.requests.get(client_ip, [])))
        )

        return response
