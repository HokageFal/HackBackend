"""
DEPRECATED: Use app.schemas.api_response instead.
This file is kept for backward compatibility.
"""

from app.schemas.api_response import ErrorResponse, ApiError

# Alias for backward compatibility
ErrorDetail = ApiError

__all__ = ["ErrorResponse", "ApiError", "ErrorDetail"]
