"""
Wenshu - 中国人民大学信息学院「文枢」大模型
智能文档管理和问答系统
"""

# flake8: noqa
# ruff: noqa

__version__ = "0.1.0"
__author__ = "RUC Information School"
__email__ = "info@ruc.edu.cn"

from .api.chat import setup_chat_routes
from .api.documents import setup_document_routes
from .config import APIConfig, init_settings, load_vector_index
from .models.document_schemas import DOCUMENT_TYPE_REGISTRY
from .processors.document_processor import DocumentProcessor

# from .agents.tools import create_agent
from .agents.callbacks import StreamingCallbackHandler

# from .main import main

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "setup_chat_routes",
    "setup_document_routes",
    "APIConfig",
    "init_settings",
    "load_vector_index",
    "DOCUMENT_TYPE_REGISTRY",
    "DocumentProcessor",
    # "create_agent",
    "StreamingCallbackHandler",
    # "main",
]
