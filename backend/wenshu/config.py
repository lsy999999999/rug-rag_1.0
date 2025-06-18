import os

import dotenv
from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.core.callbacks import CallbackManager
from llama_index.embeddings.openai_like import OpenAILikeEmbedding
from llama_index.llms.google_genai import GoogleGenAI


def init_settings(callback_manager: CallbackManager):
    """Initialize LlamaIndex settings"""
    dotenv.load_dotenv()

    Settings.embed_model = OpenAILikeEmbedding(
        model_name="Qwen/Qwen3-Embedding-4B",
        api_base=os.getenv("EMBEDDING_API_BASE", "http://localhost:8000/v1"),
        api_key=os.getenv("EMBEDDING_API_KEY", "fake"),
        embed_batch_size=10,
    )

    Settings.llm = GoogleGenAI(
        model="gemini-2.5-flash-preview-05-20",
        # model="gemini-2.5-pro-preview-06-05",
        api_key=os.getenv("GOOGLE_API_KEY"),
    )

    Settings.callback_manager = callback_manager


def load_vector_index(persist_dir: str | None = None):
    """Load vector index from storage"""
    if persist_dir is None:
        persist_dir = os.getenv("STORAGE_DIR", "data/storage")

    try:
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = load_index_from_storage(storage_context)
        print("✅ Index loaded successfully!")
        return index
    except Exception as e:
        print(f"❌ Failed to load index: {e}")
        return None


# API Configuration
class APIConfig:
    TITLE = "中国人民大学信息学院「文枢」大模型"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8080"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    CORS_ORIGINS = ["*"]
    CORS_CREDENTIALS = True
    CORS_METHODS = ["*"]
    CORS_HEADERS = ["*"]

    # Data directories
    STORAGE_DIR = os.getenv("STORAGE_DIR", "data/storage")
    TEMP_UPLOAD_DIR = os.getenv("TEMP_UPLOAD_DIR", "data/temp_uploads")
    DOCUMENTS_DIR = os.getenv("DOCUMENTS_DIR", "data/documents")
    LOG_DIR = os.getenv("LOG_DIR", "data/logs")
