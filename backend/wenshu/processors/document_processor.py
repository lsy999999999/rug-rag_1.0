from typing import List, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path
import json

from llama_index.core import Document, SimpleDirectoryReader
from llama_index.core.readers.base import BaseReader
from llama_index.node_parser.docling import DoclingNodeParser  # type: ignore
from llama_index.readers.docling import DoclingReader  # type: ignore
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.program import LLMTextCompletionProgram
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from docling_core.types.doc.document import DoclingDocument

from ..models.document_schemas import DOCUMENT_TYPE_REGISTRY, get_model_for_type
from ..config import APIConfig

import os
from typing import List, Dict
from docx import Document

class DocumentProcessor:
    """Handle document processing and metadata extraction using Pydantic models and Docling

    优化方案：
    - 单次解析：只用 DoclingDocument JSON 解析一次
    - 双重利用：从 DoclingDocument 导出 Markdown 用于元数据提取，同时保留 JSON 用于存储
    """

    def __init__(self, llm):
        self.llm = llm
        self.temp_dir = Path(APIConfig.TEMP_UPLOAD_DIR)
        self.temp_dir.mkdir(exist_ok=True, parents=True)

        # 只需要一个 DoclingReader，使用 JSON 格式
        self.docling_reader = DoclingReader(export_type=DoclingReader.ExportType.JSON)

        self.file_extractor: dict[str, BaseReader] = {
            ".docx": self.docling_reader,
            ".pptx": self.docling_reader,
            ".pdf": self.docling_reader,
            ".xlsx": self.docling_reader,
            ".txt": None,  # Use default for text files
            ".md": None,  # Use default for markdown
        }

        # 用于最终存储的 node parser
        self.node_parser = DoclingNodeParser(
            chunker=HybridChunker(tokenizer="Qwen/Qwen3-Embedding-4B", max_tokens=10240)
        )

    def identify_document_type(self, filename: str, content: str) -> str:
        """Identify document type based on filename and content"""
        filename_lower = filename.lower()
        content_lower = content.lower()

        # Enhanced heuristics for document type identification
        if any(
            keyword in filename_lower
            for keyword in ["paper", "journal", "article", "research"]
        ):
            return "academic_paper"
        elif any(
            keyword in content_lower
            for keyword in ["会议纪要", "会议记录", "参会人员", "议程"]
        ):
            return "meeting_minutes"
        elif any(
            keyword in content_lower
            for keyword in ["通知", "公告", "决定", "文件", "发文"]
        ):
            return "administrative_document"
        else:
            # Default fallback
            return "administrative_document"

    def parse_docling_document_from_json(self, json_text: str) -> DoclingDocument:
        """Parse DoclingDocument from JSON string"""
        try:
            # 解析 JSON 字符串为字典
            doc_dict = json.loads(json_text)

            # 创建 DoclingDocument 对象
            docling_doc = DoclingDocument.model_validate(doc_dict)

            return docling_doc
        except Exception as e:
            print(f"Error parsing DoclingDocument from JSON: {e}")
            raise

    def read_and_process_document(self, file_path: Path) -> Tuple[str, Document]:
        """
        单次读取文档，返回 Markdown 内容（用于元数据提取）和原始 Document（用于存储）

        Returns:
            Tuple[str, Document]: (markdown_content, original_document)
        """
        file_extension = file_path.suffix.lower()

        try:
            if (
                file_extension in self.file_extractor
                and self.file_extractor[file_extension] is not None
            ):
                # 使用 Docling JSON reader 读取文档（只解析一次）
                print(
                    "[Optimization] Single document parsing with DoclingReader JSON..."
                )
                documents = self.docling_reader.load_data(str(file_path))

                if not documents:
                    raise ValueError("Could not read document content")

                original_doc = documents[0]
                json_text = original_doc.text

                print("[Optimization] Document parsed successfully:")
                print(f"  - JSON content length: {len(json_text)} characters")

                # 从 JSON 创建 DoclingDocument 对象
                docling_doc = self.parse_docling_document_from_json(json_text)

                # 导出为 Markdown 用于元数据提取
                markdown_content = docling_doc.export_to_markdown()

                print("[Optimization] Markdown exported from DoclingDocument:")
                print(f"  - Markdown length: {len(markdown_content)} characters")
                print(f"  - Markdown preview: {markdown_content[:300]}...")

                return markdown_content, original_doc

            else:
                # 对于简单文本文件，使用 SimpleDirectoryReader
                reader = SimpleDirectoryReader(input_files=[str(file_path)])
                documents = reader.load_data()

                if not documents:
                    raise ValueError("Could not read document content")

                doc = documents[0]
                # 对于纯文本文件，Markdown 和原始内容相同
                return doc.text, doc

        except Exception as e:
            print(f"Error reading and processing document: {e}")
            # Fallback to SimpleDirectoryReader
            try:
                reader = SimpleDirectoryReader(input_files=[str(file_path)])
                documents = reader.load_data()
                if documents:
                    doc = documents[0]
                    return doc.text, doc
                else:
                    raise ValueError("Fallback reading failed")
            except Exception as fallback_error:
                raise Exception(
                    f"Both primary and fallback reading failed: {e}, {fallback_error}"
                )

    async def extract_metadata_with_pydantic(
        self, markdown_content: str, doc_type: str
    ) -> Dict[str, Any]:
        """Extract metadata using Pydantic models from Markdown content

        使用从 DoclingDocument 导出的 Markdown 内容进行元数据提取
        """

        # Get the Pydantic model for this document type
        pydantic_model = get_model_for_type(doc_type)

        # Create PydanticOutputParser
        output_parser = PydanticOutputParser(output_cls=pydantic_model)

        # Create a specialized prompt template for metadata extraction
        prompt_template_str = f"""
请仔细分析以下从DoclingDocument导出的Markdown格式文档内容，并提取结构化的元数据。

文档内容（从DoclingDocument导出的高质量Markdown格式）：
{markdown_content[:3000]}...

请根据文档内容提取相关信息。注意：
1. 这是从DoclingDocument导出的高质量Markdown，保留了良好的文档结构
2. 利用Markdown的标题层级（#, ##, ###等）来理解文档结构
3. 注意表格、列表等格式化内容
4. 提取关键信息如作者、日期、主题等
5. 如果某个字段无法从文档中获取，请设为null
6. 确保输出格式严格按照要求的JSON结构

{{format_instructions}}
"""

        # Create LLMTextCompletionProgram with Pydantic output parser
        program: LLMTextCompletionProgram = LLMTextCompletionProgram.from_defaults(
            llm=self.llm,
            output_parser=output_parser,
            prompt_template_str=prompt_template_str,
            verbose=True,
        )

        try:
            # Execute the program - this will return a validated Pydantic object
            metadata_obj = await program.acall()

            # Convert Pydantic object to dict for JSON serialization
            metadata_dict = metadata_obj.model_dump()

            return {
                "document_type": doc_type,
                "template_name": pydantic_model.__doc__ or f"{doc_type} metadata",
                "extracted_fields": metadata_dict,
                "extraction_time": datetime.now().isoformat(),
                "model_used": pydantic_model.__name__,
                "extraction_method": "docling_exported_markdown",  # 标记优化后的提取方法
            }

        except Exception as e:
            print(f"Error extracting metadata with Pydantic: {e}")
            # Return empty structure with error info
            empty_fields = {field: None for field in pydantic_model.model_fields.keys()}
            return {
                "document_type": doc_type,
                "template_name": pydantic_model.__doc__ or f"{doc_type} metadata",
                "extracted_fields": empty_fields,
                "extraction_time": datetime.now().isoformat(),
                "extraction_error": str(e),
                "model_used": pydantic_model.__name__,
                "extraction_method": "docling_exported_markdown",
            }

    def process_document_for_storage(
        self, original_document: Document, validated_metadata: Dict[str, Any]
    ) -> List:
        """Process document for final storage using DoclingNodeParser

        使用原始的 DoclingDocument JSON 格式进行高质量的 chunking
        """
        # Add validated metadata to document
        original_document.metadata.update(validated_metadata)

        # 使用 DoclingNodeParser 进行高质量的文档分块
        # 这会保留页码、边界框等结构信息
        nodes = self.node_parser.get_nodes_from_documents([original_document])

        print(f"[Storage] Created {len(nodes)} nodes with DoclingNodeParser")
        if nodes:
            print(
                f"[Storage] Sample node metadata keys: {list(nodes[0].metadata.keys())}"
            )
            # 打印一个节点的详细信息来验证结构保留
            if len(nodes) > 0:
                sample_node = nodes[0]
                print(
                    f"[Storage] Sample node text preview: {sample_node.text[:200]}..."
                )

        return nodes

    def get_document_schema(self, doc_type: str) -> Dict[str, Any]:
        """Get JSON schema for a document type"""
        pydantic_model = get_model_for_type(doc_type)
        return {
            "type": doc_type,
            "name": pydantic_model.__doc__ or f"{doc_type} metadata",
            "schema": pydantic_model.model_json_schema(),
            "fields": {
                field_name: field_info.description or field_name
                for field_name, field_info in pydantic_model.model_fields.items()
            },
        }

    def get_all_schemas(self) -> Dict[str, Any]:
        """Get all available document schemas"""
        return {
            doc_type: self.get_document_schema(doc_type)
            for doc_type in DOCUMENT_TYPE_REGISTRY.keys()
        }

#