"""
Rate limiting configuration for PerspectAI API
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/hour"],  # Global limit
    storage_uri="memory://"  # Use memory storage (simple, no Redis needed)
)

# Custom rate limit exceeded handler
def custom_rate_limit_exceeded_handler(request, exc):
    """Return friendly error message when rate limit exceeded"""
    return {
        "error": "Rate limit exceeded",
        "message": f"Too many requests. Please wait {exc.detail} before trying again.",
        "retry_after": exc.detail
    }
