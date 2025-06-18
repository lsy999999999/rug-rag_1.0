from typing import Optional

from fastapi import HTTPException
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.agent import ReActAgent
from llama_index.core.callbacks import CallbackManager

from ..agents.tools import create_agent, clear_state_cache
from ..config import APIConfig


class AgentService:
    """A singleton service to manage the lifecycle of the ReActAgent."""

    _index = None
    _callback_manager: Optional[CallbackManager] = None

    @classmethod
    def initialize(cls, index, callback_manager: CallbackManager):
        """Initializes the service with necessary components at startup."""
        print("Initializing AgentService...")
        cls._index = index
        cls._callback_manager = callback_manager
        print("AgentService initialized successfully.")

    @classmethod
    def get_agent_for_query(cls, user_query: str) -> Optional[ReActAgent]:
        """
        Creates a new agent instance for a specific user query.
        This ensures that each research process has its own context.
        """
        if cls._index is None or cls._callback_manager is None:
            print("Error: AgentService not initialized. Call initialize() first.")
            return None

        print(f"Creating a new agent instance for query: '{user_query}'")
        agent = create_agent(
            index=cls._index,
            callback_manager=cls._callback_manager,
            user_query=user_query,
        )
        if agent:
            print("Agent instance created successfully.")
        else:
            print("Agent instance creation failed.")
        return agent

    @classmethod
    def cleanup_after_request(cls):
        """Cleans up any state after a request is completed."""
        print("Cleaning up state cache after request.")
        clear_state_cache()

    @classmethod
    def reload_agent(cls):
        """
        Reloads the index from the persisted storage.

        This is a critical step after adding new documents. It ensures
        that any new agent created will have access to the latest data.
        """
        if cls._callback_manager is None:
            # This check ensures the service was initialized before trying to reload.
            raise HTTPException(
                status_code=500,
                detail="AgentService cannot be reloaded as it was not initialized.",
            )

        print("--- Reloading AgentService with updated index from storage ---")
        try:
            # 1. Point to the directory where the index was persisted.
            storage_context = StorageContext.from_defaults(
                persist_dir=APIConfig.STORAGE_DIR
            )

            # 2. Load the index from the storage context.
            # This loads the entire index, including the newly added documents.
            reloaded_index = load_index_from_storage(storage_context)

            # 3. Replace the service's old index with the newly reloaded one.
            cls._index = reloaded_index
            print(
                "AgentService reloaded successfully. It will now use the updated index."
            )

        except Exception as e:
            # If loading fails, the agent will continue using the old (stale) index.
            # Raising an exception makes the API call fail, alerting the developer.
            print(f"FATAL: Failed to reload the index from storage. Error: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to reload knowledge base: {str(e)}"
            ) from e


# Create a single instance of the service to be used across the application
agent_service = AgentService()
