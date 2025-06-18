import asyncio
from typing import Any, Optional

from llama_index.core.callbacks.base_handler import BaseCallbackHandler
from llama_index.core.callbacks.schema import EventPayload, CBEventType


class StreamingCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for capturing Agent intermediate steps, including thoughts."""

    def __init__(self):
        # We listen to specific events and ignore the rest to reduce noise.
        super().__init__(
            event_starts_to_ignore=[
                CBEventType.LLM,
                CBEventType.EMBEDDING,
                CBEventType.NODE_PARSING,
                CBEventType.QUERY,
                CBEventType.RETRIEVE,
                CBEventType.SYNTHESIZE,
                CBEventType.TREE,
            ],
            event_ends_to_ignore=[
                CBEventType.LLM,
                CBEventType.EMBEDDING,
                CBEventType.NODE_PARSING,
                CBEventType.QUERY,
                CBEventType.RETRIEVE,
                CBEventType.SYNTHESIZE,
                CBEventType.TREE,
            ],
        )
        self.step_queue = asyncio.Queue()
        self.tool_name: str = ""

    def _push_to_queue(self, event_data: dict):
        """Helper to push event data to the queue."""
        asyncio.create_task(self.step_queue.put(event_data))

    def on_event_start(
        self,
        event_type: CBEventType,
        payload: Optional[dict[str, Any]] = None,
        event_id: str = "",
        parent_id: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Handle event starts, specifically for function calls."""
        if event_type == CBEventType.FUNCTION_CALL and payload:
            tool_metadata = payload.get(EventPayload.TOOL)
            self.tool_name = getattr(tool_metadata, "name", "Unknown")
            arguments = payload.get(EventPayload.FUNCTION_CALL, {})
            self._push_to_queue(
                {
                    "type": "tool_call_start",
                    "data": {"tool_name": self.tool_name, "arguments": arguments},
                }
            )
        return event_id

    def on_event_end(
        self,
        event_type: CBEventType,
        payload: Optional[dict[str, Any]] = None,
        event_id: str = "",
        **kwargs: Any,
    ) -> None:
        """Handle event ends for agent steps (to get thoughts) and function calls (to get results)."""
        if event_type == CBEventType.AGENT_STEP and payload:
            # The key for the agent step payload is the value of the enum member itself.
            agent_step = payload.get(CBEventType.AGENT_STEP.value)
            if agent_step and hasattr(agent_step, "thought") and agent_step.thought:
                self._push_to_queue(
                    {"type": "thought", "data": agent_step.thought.strip()}
                )

        elif event_type == CBEventType.FUNCTION_CALL and payload:
            function_call_response = payload.get(EventPayload.FUNCTION_OUTPUT)
            response_str = str(function_call_response or "")
            self._push_to_queue(
                {
                    "type": "tool_call_end",
                    "data": {
                        "tool_name": self.tool_name,
                        "result": response_str,
                    },
                }
            )
            self.tool_name = ""  # Reset after use

    # The methods below are required by the base class but not used in this implementation.
    def start_trace(self, trace_id: Optional[str] = None) -> None:
        pass

    def end_trace(
        self,
        trace_id: Optional[str] = None,
        trace_map: Optional[dict[str, list[str]]] = None,
    ) -> None:
        pass
