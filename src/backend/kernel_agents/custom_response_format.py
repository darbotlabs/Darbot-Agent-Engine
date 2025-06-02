"""
Custom ResponseFormat implementation to fix compatibility issues.
"""
# Thought into existence by Darbot

# Make this module export the ResponseFormat class directly
# This allows "from backend.kernel_agents.custom_response_format import ResponseFormat" to work
__all__ = ["ResponseFormat"]

from typing import Any, Dict
from pydantic import BaseModel, Field

class ResponseFormat(BaseModel):
    type: str = Field(..., description="e.g. 'json_object'")
    schema: Dict[str, Any] = Field(default_factory=dict)
