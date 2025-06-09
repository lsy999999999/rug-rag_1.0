from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai_like import OpenAILikeEmbedding
from llama_index.node_parser.docling import DoclingNodeParser
from llama_index.readers.docling import DoclingReader
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
import asyncio
import os
import dotenv

Settings.embed_model = OpenAILikeEmbedding(
    model_name="Qwen/Qwen3-Embedding-4B",
    api_base="http://localhost:8000/v1",
    api_key="fake",
    embed_batch_size=10,
)

dotenv.load_dotenv()

reader = DoclingReader(export_type=DoclingReader.ExportType.JSON)
file_extractor = {
    ".docx": reader,
    ".pptx": reader,
    ".pdf": reader,
}
node_parser = DoclingNodeParser(
    chunker=HybridChunker(tokenizer="Qwen/Qwen3-Embedding-4B", max_tokens=10240)
)

# Create a RAG tool using LlamaIndex
documents = SimpleDirectoryReader(
    "data", recursive=True, file_extractor=file_extractor
).load_data(show_progress=True)
index = VectorStoreIndex.from_documents(
    documents,
    transformations=[node_parser],
)
index.storage_context.persist("storage")

query_engine = index.as_query_engine()


async def search_documents(query: str) -> str:
    """Useful for answering natural language questions about Renmin University of China."""
    response = await query_engine.aquery(query)
    return str(response)


# Create an enhanced workflow with both tools
agent = FunctionAgent(
    tools=[search_documents],
    llm=OpenAI(
        model="deepseek-chat",
        api_key=os.getenv("OPENAI_API_KEY"),
        api_base=os.getenv("OPENAI_API_BASE"),
    ),
    system_prompt="""You are a helpful assistant that can search through documents to answer questions about Renmin University of China.""",
)


# Now we can ask questions about the documents or do calculations
async def main():
    response = await agent.run("中国人民大学在第五轮学科评估中的结果如何？")
    print(response)


# Run the agent
if __name__ == "__main__":
    asyncio.run(main())
