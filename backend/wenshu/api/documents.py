import hashlib
import json
import pickle
from datetime import datetime

from fastapi import File, Form, HTTPException, UploadFile

from ..config import APIConfig
from ..models.document_schemas import DOCUMENT_TYPE_REGISTRY, get_model_for_type
from ..services.agent_service import agent_service


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

        try:
            # Parse confirmed metadata
            confirmed_metadata = json.loads(metadata)

            # Validate metadata against the appropriate Pydantic model
            doc_type = confirmed_metadata.get("document_type")
            if doc_type not in DOCUMENT_TYPE_REGISTRY:
                raise HTTPException(
                    status_code=400, detail=f"Invalid document type: {doc_type}"
                )

            pydantic_model = get_model_for_type(doc_type)
            extracted_fields = confirmed_metadata.get("extracted_fields", {})

            # Validate using Pydantic model
            try:
                validated_metadata = pydantic_model(**extracted_fields)
                validated_dict = validated_metadata.model_dump()
                print("[Storage] Metadata validation successful")
            except Exception as validation_error:
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

            try:
                with open(cache_file_path, "rb") as cache_file:
                    original_document = pickle.load(cache_file)
                print("[Storage] Loaded cached original document successfully")
            except Exception as e:
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
                raise HTTPException(
                    status_code=400, detail="Could not process document into nodes"
                )

            print(f"[Storage] Generated {len(nodes)} nodes for storage")

            # Add to existing index
            index.insert_nodes(nodes)

            # Persist the updated index
            index.storage_context.persist(APIConfig.STORAGE_DIR)
            print("[Storage] Index persisted successfully.")

            # --- CRITICAL STEP: Reload the agent to use the updated index ---
            agent_service.reload_agent()

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
