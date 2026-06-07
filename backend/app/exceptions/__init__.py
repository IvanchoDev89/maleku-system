from fastapi import HTTPException, status


class AppException(Exception):
    """Base application exception"""
    
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource not found"""
    
    def __init__(self, resource: str, resource_id: str = None):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with id {resource_id} not found"
        super().__init__(message)
        self.status_code = status.HTTP_404_NOT_FOUND


class AlreadyExistsException(AppException):
    """Resource already exists"""
    
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} already exists"
        if identifier:
            message = f"{resource} '{identifier}' already exists"
        super().__init__(message)
        self.status_code = status.HTTP_409_CONFLICT


class UnauthorizedException(AppException):
    """Unauthorized access"""
    
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message)
        self.status_code = status.HTTP_401_UNAUTHORIZED


class ForbiddenException(AppException):
    """Forbidden access"""
    
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message)
        self.status_code = status.HTTP_403_FORBIDDEN


class ValidationException(AppException):
    """Validation error"""
    
    def __init__(self, errors: dict):
        super().__init__("Validation error", errors)
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class AuthenticationException(AppException):
    """Authentication failed"""
    
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message)
        self.status_code = status.HTTP_401_UNAUTHORIZED


class PaymentException(AppException):
    """Payment processing error"""
    
    def __init__(self, message: str = "Payment failed"):
        super().__init__(message)
        self.status_code = status.HTTP_402_PAYMENT_REQUIRED


class RateLimitException(AppException):
    """Rate limit exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message)
        self.status_code = status.HTTP_429_TOO_MANY_REQUESTS


def http_exception_handler(exc: AppException) -> HTTPException:
    """Convert app exception to HTTP exception"""
    return HTTPException(
        status_code=exc.status_code,
        detail={"message": exc.message, "details": exc.details}
    )