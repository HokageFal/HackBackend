"""
User service module.
Handles all user-related business logic.
"""

from app.services.user.exceptions import (
    UserAlreadyExists,
    InvalidCredentials,
    UserNotFound
)
from app.services.user.auth_service import (
    login_user,
    update_access,
    generate_auth_tokens
)
from app.services.user.user_management_service import (
    get_current_user_service,
    delete_user_service,
    update_user_profile_service
)

__all__ = [
    # Exceptions
    "UserAlreadyExists",
    "InvalidCredentials",
    "UserNotFound",
    # Auth
    "login_user",
    "update_access",
    "generate_auth_tokens",
    # User Management
    "get_current_user_service",
    "delete_user_service",
    "update_user_profile_service",
]
