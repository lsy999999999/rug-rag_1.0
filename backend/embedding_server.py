# 文件路径: /home/lsyedith/ruc-rag/backend/embedding_server.py

print("Starting FastEmbed OpenAI-compatible server...")
print("This may take a few minutes to download the model for the first time.")

try:
    from fastembed.embedding import DefaultEmbedding
    from fastembed.server import app

    # This tells FastEmbed which model to load and serve.
    # It MUST match the 'model_name' in your config.py
    app.model = DefaultEmbedding(model_name="Qwen/Qwen3-Embedding-4B")
    print(f"Model 'Qwen/Qwen3-Embedding-4B' is being loaded.")

    if __name__ == "__main__":
        import uvicorn
        # The server will run on port 8000, which matches your config.py
        uvicorn.run(app, host="0.0.0.0", port=8000)
        
except ImportError:
    print("\n--- ERROR ---")
    print("Required libraries are not installed.")
    print("Please run: uv pip install fastembed uvicorn")
except Exception as e:
    print(f"\n--- An unexpected error occurred ---")
    print(e)