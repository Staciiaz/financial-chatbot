class BaseHttpError(Exception):
    """Base class for HTTP errors."""
    def __init__(self, status_code: int, message: str, error: str):
        self.status_code = status_code
        self.message = message
        self.error = error
        super().__init__(error)


class UnauthorizedError(BaseHttpError):
    """Exception raised for unauthorized access."""
    def __init__(self, error: str):
        super().__init__(status_code=401, message="Unauthorized", error=error)


class ForbiddenError(BaseHttpError):
    """Exception raised for forbidden access."""
    def __init__(self, error: str):
        super().__init__(status_code=403, message="Forbidden", error=error)
