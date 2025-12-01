import time
import logging
import sys
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("backend.log")
    ]
)
logger = logging.getLogger("qa_box")

class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Unified log format
        # Time | Method | Path | Status | Client IP | Duration
        log_msg = (
            f"{request.method} {request.url.path} "
            f"- {response.status_code} "
            f"- {request.client.host} "
            f"- {process_time:.4f}s"
        )
        
        if response.status_code >= 400:
            logger.error(log_msg)
        else:
            logger.info(log_msg)
            
        return response
