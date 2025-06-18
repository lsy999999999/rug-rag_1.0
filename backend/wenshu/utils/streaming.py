import asyncio
import json
from typing import AsyncGenerator, List

from llama_index.core.llms import ChatMessage
from ..services.agent_service import agent_service


def create_sse_message(data: dict) -> str:
    """Create Server-Sent Events message format"""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


async def stream_generator_with_steps(
    query: str,
    chat_history: List[ChatMessage],
    agent,
    callback_handler,
) -> AsyncGenerator[str, None]:
    """
    Orchestrates the iterative Agentic RAG workflow.
    - Creates a dedicated agent for the query.
    - Streams tool calls and their structured results to the frontend.
    - Streams the final synthesized answer token-by-token.
    - Cleans up state after completion.
    """
    if not agent:
        yield create_sse_message({"type": "error", "data": "Agent not initialized"})
        return

    # Clear any pending queue items from previous runs
    while not callback_handler.step_queue.empty():
        await callback_handler.step_queue.get()

    try:
        response_task = asyncio.create_task(
            agent.astream_chat(query, chat_history=chat_history)
        )
        queue_task = asyncio.create_task(callback_handler.step_queue.get())
        pending_tasks = {response_task, queue_task}

        while pending_tasks:
            done, pending_tasks = await asyncio.wait(
                pending_tasks, return_when=asyncio.FIRST_COMPLETED
            )

            if queue_task in done:
                queue_item = queue_task.result()

                # Forward the raw tool step event (start/end) to the frontend
                yield create_sse_message(queue_item)

                # If the researcher tool finished, parse and send its structured result
                if (
                    queue_item.get("type") == "tool_call_end"
                    and queue_item.get("data", {}).get("tool_name") == "researcher"
                ):
                    try:
                        tool_output_str = queue_item.get("data", {}).get("result", "{}")
                        research_result = json.loads(tool_output_str)

                        # Send document previews immediately
                        if research_result.get("retrieved_docs_preview"):
                            yield create_sse_message(
                                {
                                    "type": "retrieved_documents",
                                    "data": research_result["retrieved_docs_preview"],
                                }
                            )

                        # Send the research state summary
                        yield create_sse_message(
                            {
                                "type": "research_step",
                                "data": {
                                    "summary": research_result.get(
                                        "summary_of_findings", ""
                                    ),
                                    "is_sufficient": research_result.get(
                                        "is_sufficient", False
                                    ),
                                    "suggested_queries": research_result.get(
                                        "suggested_next_queries", []
                                    ),
                                },
                            }
                        )
                    except json.JSONDecodeError:
                        print(
                            f"Warning: Could not parse JSON from researcher tool: {tool_output_str}"
                        )

                if not response_task.done():
                    queue_task = asyncio.create_task(callback_handler.step_queue.get())
                    pending_tasks.add(queue_task)

            if response_task in done:
                break

        if not queue_task.done():
            queue_task.cancel()

        final_response = response_task.result()

        # Stream the final synthesized answer token by token
        async for token in final_response.async_response_gen():
            yield create_sse_message({"type": "token", "data": token})

    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        print(f"❌ Streaming error: {e}\n{error_details}")
        yield create_sse_message(
            {"type": "error", "data": f"Error processing request: {e}"}
        )
    finally:
        # Crucial: clean up the state cache for this request
        agent_service.cleanup_after_request()
        print("✅ Streaming completed and state cleaned up.")
        yield create_sse_message({"type": "done", "data": "Stream finished."})
