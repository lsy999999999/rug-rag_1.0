import io
import asyncio
import os
from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from docx import Document
from llama_index.core import Settings

from pydantic import BaseModel

from ..services.session_service import session_service
from ..processors.form_filler import DocxFormFiller
from ..services.agent_service import agent_service
from fastapi.responses import StreamingResponse
from ..llms.gpt_llm import GPTCustomLLM

router = APIRouter(prefix="/autofill", tags=["Document Autofill"])

class RefineRequest(BaseModel):
    session_id: str
    feedback: str


# Get OpenAI API Key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY environment variable not set. GPT-based autofill will not work.")

async def get_llm():
    """Dependency to get the currently configured LLM."""
    if not Settings.llm:
        raise HTTPException(status_code=500, detail="LLM not initialized")
    return Settings.llm

async def get_gpt_llm():
    """Dependency to get the GPT LLM for specific autofill modes."""
    # The OPENAI_API_KEY is now checked inside the GPTCustomLLM's __init__
    # We can specify a model optimized for form filling if we want.
    return GPTCustomLLM(model="gpt-4-turbo")

async def _get_context_from_knowledge_base(query: str) -> str:
    """Gets relevant context from the RAG agent based on a query."""
    agent = agent_service.get_agent_for_query(query)
    if not agent:
        return "No context could be retrieved from the knowledge base."
    try:
        response = await agent.achat(query)
        return str(response)
    except Exception as e:
        print(f"Error getting context from agent: {e}")
        return "Failed to retrieve context from knowledge base."

async def _read_docx_text(file: UploadFile) -> str:
    """Reads the text content from an uploaded .docx file."""
    try:
        file_bytes = await file.read()
        await file.seek(0) # Reset file pointer after reading
        doc_stream = io.BytesIO(file_bytes)
        doc = Document(doc_stream)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error reading docx file {file.filename}: {e}")
        return ""

@router.post("/start")
async def start_autofill_session(template_file: UploadFile = File(...), content_files: List[UploadFile] = File([]), llm = Depends(get_llm)):
    """
    Starts a new autofill session. If content_files are provided, it uses RAG and uploaded files.
    If no content_files, it starts a conversational fill session.
    """
    if not template_file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Template must be a .docx file.")

    try:
        template_bytes = await template_file.read()
        document = Document(io.BytesIO(template_bytes))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read template file: {e}")

    session_id = session_service.create_session()
    session_service.update_session(session_id, "document_state", document)

    if content_files:
        # RAG mode: Combine context from uploaded files and knowledge base
        content_coroutines = [_read_docx_text(f) for f in content_files]
        all_content_texts = await asyncio.gather(*content_coroutines)
        all_content_text = "\n\n".join(all_content_texts)
        
        knowledge_base_context = await _get_context_from_knowledge_base("Summarize all information for form filling.")
        
        final_context = f"""**Context from Uploaded Files:**
{all_content_text}

**Context from Knowledge Base:**
{knowledge_base_context}"""

        session_service.add_history(session_id, {"type": "retrieval", "content": final_context[:1000] + "..."})

        filler = DocxFormFiller(llm=llm) # Use default LLM (GoogleGenAI)
        filler.load_document(document)
        instructions = await filler.analyze_for_autofill(final_context)
        
        if not instructions.get("filling_instructions"):
            return {
                "session_id": session_id,
                "message": "Session started, but no automatic fillings were found. Please use the refinement chat.",
                "preview": {"filling_instructions": []}
            }

        filler.apply_instructions(instructions["filling_instructions"])
        session_service.add_history(session_id, {"type": "ai_fill", "instructions": instructions})

        return {
            "session_id": session_id,
            "message": "Session started and initial fill complete.",
            "preview": instructions
        }
    else:
        # Conversational fill mode: No initial content, just start session for refinement
        session_service.update_session(session_id, "mode", "conversational")
        session_service.update_session(session_id, "llm_type", "gpt") # Mark session to use GPT LLM
        return {
            "session_id": session_id,
            "message": "Conversational autofill session started. Please provide instructions.",
            "preview": {"filling_instructions": []}
        }

@router.post("/start_from_file")
async def start_autofill_from_file_session(template_file: UploadFile = File(...), content_file: UploadFile = File(...), gpt_llm = Depends(get_gpt_llm)):
    """
    Starts a new autofill session using only a single content file for context (no RAG).
    """
    if not template_file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Template must be a .docx file.")
    if not content_file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Content file must be a .docx file.")

    try:
        template_bytes = await template_file.read()
        document = Document(io.BytesIO(template_bytes))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read template file: {e}")

    session_id = session_service.create_session()
    session_service.update_session(session_id, "document_state", document)
    session_service.update_session(session_id, "mode", "from_file")
    session_service.update_session(session_id, "llm_type", "gpt") # Mark session to use GPT LLM

    # Read content file
    content_text = await _read_docx_text(content_file)
    
    # Perform initial fill using only the content file
    filler = DocxFormFiller(llm=gpt_llm) # Use GPT LLM
    filler.load_document(document)
    instructions = await filler.analyze_for_autofill(content_text)
    
    if not instructions.get("filling_instructions"):
        return {
            "session_id": session_id,
            "message": "Session started, but no automatic fillings were found from the content file. Please use the refinement chat.",
            "preview": {"filling_instructions": []}
        }

    filler.apply_instructions(instructions["filling_instructions"])
    session_service.add_history(session_id, {"type": "ai_fill", "instructions": instructions})

    return {
        "session_id": session_id,
        "message": "Session started and initial fill complete from file.",
        "preview": instructions
    }

@router.post("/refine")
async def refine_autofill_session(
    request: RefineRequest, # <--- 修改这里
    llm_default = Depends(get_llm), 
    gpt_llm_dep = Depends(get_gpt_llm)
):
    """
    Refines the document based on user feedback, using the appropriate LLM for the session mode.
    """
    session_id = request.session_id # <--- 从 request 对象中获取
    feedback = request.feedback   # <--- 从 request 对象中获取


    session = session_service.get_session(session_id)
    if not session or "document_state" not in session:
        raise HTTPException(status_code=404, detail="Session or document not found.")

    document = session["document_state"]
    session_service.add_history(session_id, {"type": "user_feedback", "content": feedback})

    # Determine which LLM to use based on session mode
    llm_to_use = llm_default # Default to GoogleGenAI
    if session.get("llm_type") == "gpt":
        llm_to_use = gpt_llm_dep

    filler = DocxFormFiller(llm=llm_to_use)
    filler.load_document(document)

    # Generate new instructions based on feedback
    new_instructions = await filler.refine_with_feedback(feedback)
    
    if not new_instructions.get("filling_instructions"):
        raise HTTPException(status_code=400, detail="Could not interpret the refinement instruction. Please try rephrasing.")

    # Apply the new instructions
    filler.apply_instructions(new_instructions["filling_instructions"])
    
    session_service.add_history(session_id, {"type": "ai_refinement", "instructions": new_instructions})
    session_service.update_session(session_id, "document_state", document)

    return {
        "session_id": session_id,
        "message": "Feedback applied and document updated.",
        "preview": new_instructions
    }

@router.get("/download/{session_id}")
async def download_filled_document(session_id: str):
    """
    Downloads the final filled document and ends the session.
    """
    session = session_service.get_session(session_id)
    if not session or "document_state" not in session:
        raise HTTPException(status_code=404, detail="Session or document not found.")

    document = session["document_state"]
    doc_stream = io.BytesIO()
    document.save(doc_stream)
    doc_stream.seek(0)

    session_service.end_session(session_id)

    return StreamingResponse(
        doc_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=filled_document_{session_id[:8]}.docx"}
    )

def setup_autofill_routes(app):
    app.include_router(router)