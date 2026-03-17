"""
User service exceptions.
"""


class UserAlreadyExists(Exception):
    """Raised when trying to create a user that already exists."""
    
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(message)


class InvalidCredentials(Exception):
    """Raised when user credentials are invalid."""
    
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(message)


class UserNotFound(Exception):
    """Raised when user is not found in database."""
    
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(message)


class EmailNotVerified(Exception):
    """Raised when user's email is not verified."""
    
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(message)


class InvalidOperation(Exception):
    """Raised when operation is not allowed for this user type."""
    
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(message)
