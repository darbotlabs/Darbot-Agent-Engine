# custom_exceptions.py
"""
Custom exception classes for enhanced error handling
Thought into existence by Darbot
"""
from typing import Any, Dict, Optional

from fastapi import HTTPException
from starlette.status import *


class DarbotEngineException(HTTPException):
    """Base exception class for Darbot Agent Engine"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = None,
        extra_data: Dict[str, Any] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code or self.__class__.__name__
        self.extra_data = extra_data or {}


class ConfigurationException(DarbotEngineException):
    """Raised when there's a configuration error"""
    
    def __init__(self, detail: str, config_key: str = None):
        super().__init__(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="CONFIGURATION_ERROR",
            extra_data={"config_key": config_key} if config_key else {}
        )


class AuthenticationException(DarbotEngineException):
    """Raised when authentication fails"""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTHENTICATION_FAILED"
        )


class AuthorizationException(DarbotEngineException):
    """Raised when authorization fails"""
    
    def __init__(self, detail: str = "Access denied", required_role: str = None):
        super().__init__(
            status_code=HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="AUTHORIZATION_FAILED",
            extra_data={"required_role": required_role} if required_role else {}
        )


class ValidationException(DarbotEngineException):
    """Raised when input validation fails"""
    
    def __init__(self, detail: str, field: str = None, value: Any = None):
        super().__init__(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
            extra_data={
                "field": field,
                "value": str(value) if value is not None else None
            }
        )


class AgentException(DarbotEngineException):
    """Raised when agent operations fail"""
    
    def __init__(self, detail: str, agent_type: str = None, agent_id: str = None):
        super().__init__(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="AGENT_ERROR",
            extra_data={
                "agent_type": agent_type,
                "agent_id": agent_id
            }
        )


class TaskException(DarbotEngineException):
    """Raised when task processing fails"""
    
    def __init__(self, detail: str, task_id: str = None, task_type: str = None):
        super().__init__(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="TASK_ERROR",
            extra_data={
                "task_id": task_id,
                "task_type": task_type
            }
        )


class AzureServiceException(DarbotEngineException):
    """Raised when Azure service operations fail"""
    
    def __init__(
        self, 
        detail: str, 
        service_name: str = None, 
        azure_error_code: str = None
    ):
        super().__init__(
            status_code=HTTP_502_BAD_GATEWAY,
            detail=detail,
            error_code="AZURE_SERVICE_ERROR",
            extra_data={
                "service_name": service_name,
                "azure_error_code": azure_error_code
            }
        )


class DatabaseException(DarbotEngineException):
    """Raised when database operations fail"""
    
    def __init__(self, detail: str, operation: str = None, collection: str = None):
        super().__init__(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR",
            extra_data={
                "operation": operation,
                "collection": collection
            }
        )


class RateLimitException(DarbotEngineException):
    """Raised when rate limits are exceeded"""
    
    def __init__(self, detail: str = "Rate limit exceeded", retry_after: int = None):
        super().__init__(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="RATE_LIMIT_EXCEEDED",
            extra_data={"retry_after": retry_after} if retry_after else {}
        )


class ExternalServiceException(DarbotEngineException):
    """Raised when external service calls fail"""
    
    def __init__(
        self, 
        detail: str, 
        service_name: str = None, 
        status_code: int = HTTP_502_BAD_GATEWAY
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
            error_code="EXTERNAL_SERVICE_ERROR",
            extra_data={"service_name": service_name}
        )