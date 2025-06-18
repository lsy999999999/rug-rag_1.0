from typing import Dict, List, Optional, Type

from pydantic import BaseModel, Field


class AcademicPaper(BaseModel):
    """学术论文元数据模型"""

    title: str = Field(..., description="论文标题")
    authors: List[str] = Field(..., description="作者列表")
    journal: Optional[str] = Field(None, description="期刊名称")
    publication_date: Optional[str] = Field(None, description="发表时间")
    keywords: List[str] = Field(default=[], description="关键词列表")
    abstract: Optional[str] = Field(None, description="摘要")
    doi: Optional[str] = Field(None, description="DOI号")
    field: Optional[str] = Field(None, description="学科领域")


class AdministrativeDocument(BaseModel):
    """行政文件元数据模型"""

    document_type: str = Field(..., description="文件类型")
    issuing_department: str = Field(..., description="发文单位")
    document_number: Optional[str] = Field(None, description="文号")
    subject: str = Field(..., description="主题")
    issue_date: Optional[str] = Field(None, description="发文日期")
    key_personnel: List[str] = Field(default=[], description="关键人员")
    deadline: Optional[str] = Field(None, description="截止时间")
    priority: Optional[str] = Field(None, description="优先级")


class MeetingMinutes(BaseModel):
    """会议纪要元数据模型"""

    meeting_title: str = Field(..., description="会议名称")
    meeting_date: Optional[str] = Field(None, description="会议时间")
    participants: List[str] = Field(default=[], description="参会人员")
    agenda: List[str] = Field(default=[], description="会议议程")
    decisions: List[str] = Field(default=[], description="决议事项")
    action_items: List[str] = Field(default=[], description="行动项")
    next_meeting: Optional[str] = Field(None, description="下次会议时间")


# Document type registry mapping types to Pydantic models
DOCUMENT_TYPE_REGISTRY: Dict[str, Type[BaseModel]] = {
    "academic_paper": AcademicPaper,
    "administrative_document": AdministrativeDocument,
    "meeting_minutes": MeetingMinutes,
}


def get_model_for_type(doc_type: str) -> Type[BaseModel]:
    """Get Pydantic model for document type"""
    if doc_type not in DOCUMENT_TYPE_REGISTRY:
        raise ValueError(f"Unknown document type: {doc_type}")
    return DOCUMENT_TYPE_REGISTRY[doc_type]


def get_available_types() -> List[str]:
    """Get list of available document types"""
    return list(DOCUMENT_TYPE_REGISTRY.keys())
