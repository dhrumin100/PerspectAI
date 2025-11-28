"""
Structured logging configuration for PerspectAI
"""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict

class StructuredLogger:
    """JSON structured logger for better observability"""
    
    def __init__(self, name: str = "perspectai"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Console handler with JSON format
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
    
    def log_request(self, query: str, intent: str, cache_hit: bool, **kwargs):
        """Log an incoming request"""
        self.logger.info(json.dumps({
            "event": "request_received",
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "query": query[:100],  # Truncate for privacy
            "intent": intent,
            "cache_hit": cache_hit,
            **kwargs
        }))
    
    def log_verdict(self, verdict: str, confidence: float, sources_count: int, **kwargs):
        """Log a verdict generation"""
        self.logger.info(json.dumps({
            "event": "verdict_generated",
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "verdict": verdict,
            "confidence": confidence,
            "sources_count": sources_count,
            **kwargs
        }))
    
    def log_performance(self, operation: str, duration_ms: int, **kwargs):
        """Log performance metrics"""
        self.logger.info(json.dumps({
            "event": "performance_metric",
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "operation": operation,
            "duration_ms": duration_ms,
            **kwargs
        }))
    
    def log_error(self, error: str, context: Dict[str, Any] = None):
        """Log an error with context"""
        self.logger.error(json.dumps({
            "event": "error",
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "error": str(error),
            "context": context or {}
        }))


class JSONFormatter(logging.Formatter):
    """Format logs as JSON"""
    
    def format(self, record):
        # If the message is already JSON, return it
        try:
            json.loads(record.msg)
            return record.msg
        except:
            # Otherwise wrap in JSON
            return json.dumps({
                "level": record.levelname,
                "message": record.msg,
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            })


# Global logger instance
logger = StructuredLogger()
