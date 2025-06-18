"""
API endpoints
"""

from .chat import setup_chat_routes
from .documents import setup_document_routes

__all__ = ["setup_chat_routes", "setup_document_routes"]
