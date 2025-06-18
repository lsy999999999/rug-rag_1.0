"""
Document models and schemas
"""

from .document_schemas import (
    DOCUMENT_TYPE_REGISTRY,
    AcademicPaper,
    AdministrativeDocument,
    MeetingMinutes,
    get_available_types,
    get_model_for_type,
)

__all__ = [
    "AcademicPaper",
    "AdministrativeDocument",
    "MeetingMinutes",
    "DOCUMENT_TYPE_REGISTRY",
    "get_model_for_type",
    "get_available_types",
]
