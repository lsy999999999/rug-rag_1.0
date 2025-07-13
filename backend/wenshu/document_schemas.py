from pydantic import BaseModel, Field
from typing import List, Dict, Any

class FillingInstruction(BaseModel):
    table: int = Field(..., description="目标表格的编号 (1-based)")
    row: int = Field(..., description="目标单元格的行索引 (0-based)")
    col: int = Field(..., description="目标单元格的列索引 (0-based)")
    value: str = Field(..., description="要填充的值")
    reason: str = Field(..., description="选择此位置的原因")

class LLMResponse(BaseModel):
    extracted_info: Dict[str, Any] = Field(..., description="从用户指令中提取的结构化信息")
    filling_instructions: List[FillingInstruction] = Field(..., description="具体的填充指令列表")