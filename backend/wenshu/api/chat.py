import json

from fastapi import Form
from fastapi.responses import StreamingResponse
from llama_index.core.llms import ChatMessage, MessageRole

from ..services.agent_service import agent_service
from ..utils.streaming import stream_generator_with_steps


def setup_chat_routes(app, callback_handler):
    """Setup chat-related API routes"""

    @app.post("/chat")
    async def chat_endpoint(query: str = Form(...), chat_history: str = Form("[]")):
        """Main chat endpoint with streaming support"""
        # Create a new agent instance specifically for this query
        agent = agent_service.get_agent_for_query(query)
        if not agent:
            return {"error": "Agent could not be created. Please check server logs."}

        try:
            history_dicts = json.loads(chat_history)
            llama_chat_history = [
                ChatMessage(
                    role=(
                        MessageRole.USER
                        if msg.get("role") == "user"
                        else MessageRole.ASSISTANT
                    ),
                    content=msg.get("content"),
                )
                for msg in history_dicts
            ]
        except json.JSONDecodeError:
            llama_chat_history = []

        # The generator will now also handle cleaning up the state
        return StreamingResponse(
            stream_generator_with_steps(
                query=query,
                chat_history=llama_chat_history,
                agent=agent,
                callback_handler=callback_handler,
            ),
            media_type="text/event-stream",
        )
