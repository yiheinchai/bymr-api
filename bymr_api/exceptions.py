"""Custom exceptions for the BYMR API SDK."""


class BYMRAPIError(Exception):
    """Base exception for all BYMR API errors."""
    
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class AuthenticationError(BYMRAPIError):
    """Raised when authentication fails."""
    pass


class ValidationError(BYMRAPIError):
    """Raised when request validation fails."""
    pass


class NetworkError(BYMRAPIError):
    """Raised when network-related errors occur."""
    pass


class ServerError(BYMRAPIError):
    """Raised when server returns 5xx errors."""
    pass
