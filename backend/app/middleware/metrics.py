"""Prometheus metrics collection middleware for FastAPI."""
from time import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST


# --- Metrics definitions ---

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1, 2, 5],
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "HTTP requests currently in progress",
    ["method"],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Records Prometheus metrics for every request (except /metrics itself)."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        path = request.url.path

        http_requests_in_progress.labels(method=method).inc()
        start = time()

        try:
            response = await call_next(request)
            http_requests_total.labels(
                method=method, path=path, status=str(response.status_code)
            ).inc()
            http_request_duration_seconds.labels(method=method, path=path).observe(
                time() - start
            )
            return response
        except Exception:
            http_requests_total.labels(method=method, path=path, status="500").inc()
            raise
        finally:
            http_requests_in_progress.labels(method=method).dec()


def metrics_endpoint(request: Request) -> Response:
    """Exposes Prometheus metrics in text format."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
