from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from llama_index.core.callbacks import CallbackManager

from .agents.callbacks import StreamingCallbackHandler
from .api.chat import setup_chat_routes
from .api.documents import setup_document_routes
from .api.autofill import setup_autofill_routes

# Import our modules
from .config import APIConfig, init_settings, load_vector_index
from .processors.document_processor import DocumentProcessor
from .services.agent_service import agent_service

# Global variables for sharing between modules
index = None
callback_handler = None
doc_processor = None
search_tool = None


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(title=APIConfig.TITLE)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=APIConfig.CORS_ORIGINS,
        allow_credentials=APIConfig.CORS_CREDENTIALS,
        allow_methods=APIConfig.CORS_METHODS,
        allow_headers=APIConfig.CORS_HEADERS,
    )

    return app


def initialize_system() -> None:
    """Initialize all system components"""
    global index, callback_handler, doc_processor, search_tool

    # Initialize callback handler
    callback_handler = StreamingCallbackHandler()
    callback_manager = CallbackManager([callback_handler])

    # Initialize LlamaIndex settings
    init_settings(callback_manager)

    # Load vector index
    index = load_vector_index()

    # Initialize document processor
    from llama_index.core import Settings

    doc_processor = DocumentProcessor(Settings.llm) if Settings.llm else None

    # Initialize the agent service with the index and callback manager
    agent_service.initialize(index, callback_manager)

    print("✅ System initialization completed!")


# This function can be used for local testing if needed, but startup event is primary
def main() -> FastAPI:
    """Main application entry point"""
    # Create FastAPI app
    app = create_app()

    # Initialize system components
    initialize_system()

    # Setup API routes
    setup_chat_routes(app, callback_handler)
    setup_document_routes(app, doc_processor, index)
    setup_autofill_routes(app)

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "index_loaded": index is not None,
            "agent_service_ready": agent_service._index is not None,
            "doc_processor_ready": doc_processor is not None,
        }

    return app


# Create app instance
app = create_app()


# Initialize on startup
@app.on_event("startup")
async def startup_event() -> None:
    initialize_system()

    # Setup routes after initialization
    setup_chat_routes(app, callback_handler)
    setup_document_routes(app, doc_processor, index)
    setup_autofill_routes(app)

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "index_loaded": index is not None,
            "agent_service_ready": agent_service._index is not None,
            "doc_processor_ready": doc_processor is not None,
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "wenshu.main:main", host=APIConfig.HOST, port=APIConfig.PORT, reload=True
    )
