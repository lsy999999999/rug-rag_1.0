import os

import dotenv
from llama_index.core.callbacks import CallbackManager
from llama_index.embeddings.openai_like import OpenAILikeEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core import Settings, StorageContext, load_index_from_storage, VectorStoreIndex


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
    """
    Load vector index from storage.
    If storage does not exist or is empty, create a new empty index.
    """
    if persist_dir is None:
        persist_dir = os.getenv("STORAGE_DIR", "data/storage")

    # 确保存储目录存在
    os.makedirs(persist_dir, exist_ok=True)
    
    # 检查索引是否已存在 (通过检查关键文件)
    # LlamaIndex 默认会创建 docstore.json, vector_store.json 等文件
    if not os.path.exists(os.path.join(persist_dir, "docstore.json")):
        # 如果索引不存在，则创建一个新的空索引
        print(f"⚠️ Index not found in '{persist_dir}'. Creating a new empty index.")
        
        # 创建一个空的文档列表
        documents = []
        # 从空文档创建一个新的索引
        index = VectorStoreIndex.from_documents(documents)
        # 将这个新创建的空索引立即持久化，以便下次启动时可以加载
        index.storage_context.persist(persist_dir=persist_dir)
        
        print("✅ New empty index created and persisted.")
        return index
    else:
        # 如果索引已存在，则加载它
        try:
            print(f"✅ Found existing index in '{persist_dir}'. Loading...")
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
            index = load_index_from_storage(storage_context)
            print("✅ Index loaded successfully.")
            return index
        except Exception as e:
            # 如果加载失败（例如文件损坏），也创建一个新的
            print(f"❌ Failed to load existing index: {e}. Creating a new empty index as a fallback.")
            documents = []
            index = VectorStoreIndex.from_documents(documents)
            index.storage_context.persist(persist_dir=persist_dir)
            return index

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

#帮我解释一下现在ruc-rag这个文件夹里面的代码在干什么东西，详细说明