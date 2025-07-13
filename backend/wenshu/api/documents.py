import hashlib
import json
import pickle
from datetime import datetime

from fastapi import File, Form, HTTPException, UploadFile

from ..config import APIConfig
from ..models.document_schemas import DOCUMENT_TYPE_REGISTRY, get_model_for_type
from ..services.agent_service import agent_service


from typing import Optional

def setup_document_routes(app, doc_processor, index):
    """Setup document-related API routes with optimized single-parsing approach"""

    @app.post("/upload_document")
    async def upload_document(file: UploadFile = File(...)):
        """Handle document upload and metadata extraction using single DoclingDocument parsing

        优化方案：单次解析 DoclingDocument，导出 Markdown 用于元数据提取，缓存结果用于后续存储
        """
        if not doc_processor:
            raise HTTPException(
                status_code=500, detail="Document processor not initialized"
            )

        try:
            # Save uploaded file temporarily
            file_hash = hashlib.md5(await file.read()).hexdigest()
            await file.seek(0)  # Reset file pointer

            temp_file_path = doc_processor.temp_dir / f"{file_hash}_{file.filename}"
            with open(temp_file_path, "wb") as temp_file:
                content = await file.read()
                temp_file.write(content)

            # 单次解析：获取 Markdown 和原始 Document
            try:
                print("[Optimization] Starting single document parsing...")
                markdown_content, original_document = (
                    doc_processor.read_and_process_document(temp_file_path)
                )

                print("[Optimization] Single parsing completed successfully:")
                print(f"  - Markdown length: {len(markdown_content)} characters")
                print("  - Original document preserved for storage")

                # 缓存原始文档用于后续存储（避免重新解析）
                cache_file_path = doc_processor.temp_dir / f"{file_hash}_cached_doc.pkl"
                with open(cache_file_path, "wb") as cache_file:
                    pickle.dump(original_document, cache_file)
                print("[Optimization] Original document cached for later use")

                # 使用 Markdown 内容进行文档类型识别
                doc_type = doc_processor.identify_document_type(
                    file.filename, markdown_content
                )
                print(f"[Optimization] Document type identified: {doc_type}")

                # 使用 Markdown 内容进行元数据提取
                print(
                    "[Optimization] Starting metadata extraction from exported Markdown..."
                )
                metadata = await doc_processor.extract_metadata_with_pydantic(
                    markdown_content, doc_type
                )
                print("[Optimization] Metadata extraction completed")
            # ** CRITICAL CHECK **
            # 如果元数据提取失败 (函数可能返回None或一个包含错误的字典)
                if not metadata or not metadata.get("extracted_fields") or metadata.get("error"):
                    error_message = metadata.get("error", "Unknown error during metadata extraction.")
                    print(f"❌ Metadata extraction failed: {error_message}")
                    raise HTTPException(
                        status_code=503,  # Service Unavailable or 422 Unprocessable Entity
                        detail=f"Metadata extraction failed: {error_message}. Please check the LLM API key and network connectivity."
                    )

                print("[Optimization] Metadata extraction completed successfully.")



                # Get schema for frontend validation
                schema_info = doc_processor.get_document_schema(doc_type)

                return {
                    "status": "success",
                    "file_id": file_hash,
                    "filename": file.filename,
                    "document_type": doc_type,
                    "metadata": metadata,
                    "schema": schema_info,
                    "content_preview": (
                        markdown_content[:300] + "..."
                        if len(markdown_content) > 300
                        else markdown_content
                    ),
                }

            except Exception as e:
                temp_file_path.unlink(missing_ok=True)
                cache_file_path = doc_processor.temp_dir / f"{file_hash}_cached_doc.pkl"
                cache_file_path.unlink(missing_ok=True)
                # Clean up temp files
                if temp_file_path.exists():
                    temp_file_path.unlink()
                cache_file_path = doc_processor.temp_dir / f"{file_hash}_cached_doc.pkl"
                if cache_file_path.exists():
                    cache_file_path.unlink()
                raise HTTPException(
                    status_code=400, detail=f"Error processing document: {str(e)}"
                )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    @app.post("/confirm_document")
    async def confirm_document(
        file_id: str = Form(...), metadata: str = Form(...), filename: str = Form(...)
    ):
        """Confirm metadata and add document to knowledge base using cached DoclingDocument

        优化方案：使用缓存的原始 DoclingDocument，无需重新解析
        """
        if not index or not doc_processor:
            raise HTTPException(status_code=500, detail="System not initialized")

        print(f"--- Entering confirm_document endpoint ---")
        try:
            # Parse confirmed metadata
            print(f"Received file_id: {file_id}, filename: {filename}")
            print(f"Received metadata (raw): {metadata[:200]}...") # Print first 200 chars
            confirmed_metadata = json.loads(metadata)
            print(f"Parsed confirmed_metadata: {confirmed_metadata}")

            # Validate metadata against the appropriate Pydantic model
            doc_type = confirmed_metadata.get("document_type")
            if doc_type not in DOCUMENT_TYPE_REGISTRY:
                raise HTTPException(
                    status_code=400, detail=f"Invalid document type: {doc_type}"
                )

            pydantic_model = get_model_for_type(doc_type)
            extracted_fields = confirmed_metadata.get("extracted_fields", {})

            # Validate using Pydantic model
            print(f"Attempting to validate metadata for doc_type: {doc_type}")
            try:
                validated_metadata = pydantic_model(**extracted_fields)
                validated_dict = validated_metadata.model_dump()
                print("[Storage] Metadata validation successful")
            except Exception as validation_error:
                print(f"[Storage] Metadata validation failed: {validation_error}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Metadata validation failed: {str(validation_error)}",
                )

            # 加载缓存的原始文档（避免重新解析）
            cache_file_path = doc_processor.temp_dir / f"{file_id}_cached_doc.pkl"
            if not cache_file_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail="Cached document not found. Please re-upload the file.",
                )

            print(f"Attempting to load cached document from: {cache_file_path}")
            try:
                with open(cache_file_path, "rb") as cache_file:
                    original_document = pickle.load(cache_file)
                print("[Storage] Loaded cached original document successfully")
            except Exception as e:
                print(f"[Storage] Error loading cached document: {e}")
                raise HTTPException(
                    status_code=500, detail=f"Error loading cached document: {str(e)}"
                )

            # Prepare metadata for storage
            storage_metadata = {
                "file_name": filename,
                "upload_time": datetime.now().isoformat(),
                "document_type": doc_type,
                **validated_dict,  # Add all validated metadata fields
            }

            # 使用缓存的 DoclingDocument 进行高质量存储（无需重新解析）
            print(
                "[Storage] Processing cached document for storage with DoclingNodeParser..."
            )
            nodes = doc_processor.process_document_for_storage(
                original_document, storage_metadata
            )

            if not nodes:
                print("[Storage] No nodes generated from document.")
                raise HTTPException(
                    status_code=400, detail="Could not process document into nodes"
                )

            print(f"[Storage] Generated {len(nodes)} nodes for storage")

            # Add to existing index
            print("[Storage] Attempting to insert nodes into index...")
            index.insert_nodes(nodes)
            print("[Storage] Nodes inserted successfully.")

            # Persist the updated index
            print(f"[Storage] Attempting to persist index to {APIConfig.STORAGE_DIR}...")
            index.storage_context.persist(APIConfig.STORAGE_DIR)
            print("[Storage] Index persisted successfully.")

            # --- CRITICAL STEP: Reload the agent to use the updated index ---
            print("[Storage] Reloading agent...")
            agent_service.reload_agent()
            print("[Storage] Agent reloaded.")

            # Clean up temp files
            temp_file_path = doc_processor.temp_dir / f"{file_id}_{filename}"
            if temp_file_path.exists():
                temp_file_path.unlink()

            if cache_file_path.exists():
                cache_file_path.unlink()

            return {
                "status": "success",
                "message": f"Document '{filename}' has been successfully added to the knowledge base",
                "nodes_added": len(nodes),
                "validated_metadata": validated_dict,
                "document_type": doc_type,
            }

        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid metadata JSON")
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error adding document: {str(e)}"
            )

    @app.get("/document_templates")
    async def get_document_templates():
        """Return available document templates with full schema information"""
        if not doc_processor:
            raise HTTPException(
                status_code=500, detail="Document processor not initialized"
            )

        return {
            "templates": doc_processor.get_all_schemas(),
            "available_types": list(DOCUMENT_TYPE_REGISTRY.keys()),
        }

    @app.get("/document_schema/{doc_type}")
    async def get_document_schema(doc_type: str):
        """Get JSON schema for a specific document type"""
        if not doc_processor:
            raise HTTPException(
                status_code=500, detail="Document processor not initialized"
            )

        try:
            schema = doc_processor.get_document_schema(doc_type)
            return schema
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))


    @app.post("/auto_fill_form")
    async def auto_fill_form(
        file: UploadFile = File(...),
        data_file: Optional[UploadFile] = File(None),
        db_table: Optional[str] = Form(None),
        db_query: Optional[str] = Form(None),
    ):
        """
        自动填表API：
        - file: Word表单文件
        - data_file: 结构化数据文件（如csv、xlsx、json），可选
        - db_table/db_query: 数据库表名和查询条件，可选
        """
        import tempfile
        import pandas as pd
        from docx import Document
        import shutil
        import sqlite3
        import os
        import json as pyjson

        # 1. 保存上传的Word表单
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_docx:
            shutil.copyfileobj(file.file, tmp_docx)
            docx_path = tmp_docx.name

        # 2. 解析数据源
        data_dict = None
        # 2.1 优先结构化文件
        if data_file:
            ext = os.path.splitext(data_file.filename)[-1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_data:
                shutil.copyfileobj(data_file.file, tmp_data)
                data_path = tmp_data.name
            if ext in [".csv", ".xls", ".xlsx"]:
                df = pd.read_csv(data_path) if ext == ".csv" else pd.read_excel(data_path)
                data_dict = df.iloc[0].to_dict()
            elif ext == ".json":
                with open(data_path, "r", encoding="utf-8") as f:
                    data_dict = pyjson.load(f)
        # 2.2 数据库
        elif db_table:
            # 假设sqlite，数据库文件路径可通过配置或环境变量
            db_path = os.getenv("AUTO_FILL_DB_PATH", "data/auto_fill.db")
            conn = sqlite3.connect(db_path)
            query = f"SELECT * FROM {db_table} {db_query or ''}"
            df = pd.read_sql(query, conn)
            if not df.empty:
                data_dict = df.iloc[0].to_dict()
            conn.close()
        # 2.3 无数据源
        if not data_dict:
            raise HTTPException(status_code=400, detail="未提供有效的数据源")

        # 3. 自动填表逻辑（利用AdaptiveLLMFormFiller）
        # 这里直接复用你给的AdaptiveLLMFormFiller核心逻辑
        # 为了集成，建议将AdaptiveLLMFormFiller类单独放到backend/wenshu/utils/llm_form_filler.py
        from ..utils.llm_form_filler import AdaptiveLLMFormFiller
        API_KEY = os.getenv("OPENAI_API_KEY", "sk-xxx")
        filler = AdaptiveLLMFormFiller(API_KEY)
        filler.load_document(docx_path)
        fill_result = filler.fill_from_dict(data_dict)
        # 4. 保存新文档
        output_path = docx_path.replace('.docx', '_auto_filled.docx')
        filler.save_document(output_path)
        # 5. 返回结果
        with open(output_path, "rb") as f:
            filled_bytes = f.read()
        return {
            "status": "success",
            "filled_items": fill_result,
            "file_name": os.path.basename(output_path),
            "file_bytes": filled_bytes.hex()  # 前端可用hex转回bytes
        }
