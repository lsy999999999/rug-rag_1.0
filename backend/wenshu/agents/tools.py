import json
from typing import List, Optional

from llama_index.core import Settings
from llama_index.core.agent import ReActAgent
from llama_index.core.callbacks import CallbackManager
from llama_index.core.tools import FunctionTool

from .researcher import research_and_evaluate

# This dictionary will hold the original user query for the duration of a single chat interaction.
# In a production environment, this should be handled by a more robust state management system.
__temp_state_cache = {}


def create_researcher_tool(index) -> List[FunctionTool]:
    """
    Creates the 'researcher' tool for the agent.
    This tool is a wrapper around the multi-step research_and_evaluate function.
    """
    if not index:
        return []

    async def researcher(search_query: str) -> str:
        """
        Your primary tool for conducting research.
        - On the first turn, provide the user's full, original query to start the research.
        - On subsequent turns, use the suggestions from the previous step to refine your search.
        - The tool returns a JSON object detailing the findings and suggests next steps.
        """
        # Retrieve the original user query from the temporary cache
        user_query = __temp_state_cache.get("user_query", "")
        if not user_query:
            # This should not happen if the orchestrator sets it, but as a fallback:
            user_query = search_query
            print(
                "Warning: Original user query not found in cache. Using search_query as user_query."
            )

        # Await the async research function directly, as we are in an async context.
        result = await research_and_evaluate(user_query, search_query, index)

        # The agent expects a string observation, so we serialize the JSON result.
        return json.dumps(result, ensure_ascii=False)

    researcher_tool = FunctionTool.from_defaults(
        fn=researcher,
        name="researcher",
    )
    return [researcher_tool]


def create_agent(
    index, callback_manager: CallbackManager, user_query: str
) -> Optional[ReActAgent]:
    """Create and configure the ReAct agent with the iterative researcher tool."""

    # Store the user's original query in a temporary cache for the researcher tool to access.
    __temp_state_cache["user_query"] = user_query

    tools = create_researcher_tool(index)

    if not tools:
        return None

    system_prompt = """
You are a highly skilled research assistant. Your goal is to provide a comprehensive, well-supported answer to the user's query by conducting iterative research.

**Your ONLY tool is `researcher(search_query: str)`.**

**Your workflow is a strict, multi-step loop:**

1.  **START**: On your first turn, you MUST call the `researcher` tool using the user's original, full query as the `search_query`.

2.  **ANALYZE**: The tool will return a JSON object. You MUST carefully analyze its fields:
    - `is_sufficient`: A boolean. `true` means you have enough information. `false` means you need to dig deeper.
    - `summary_of_findings`: A text summary of what was found in the last step.
    - `suggested_next_queries`: A list of new, more specific queries to try if `is_sufficient` is `false`.

3.  **DECIDE & ITERATE**:
    - **If `is_sufficient` is `false`**: You MUST pick the best query from `suggested_next_queries` and call the `researcher` tool again with it. You must announce that you are continuing research based on the new findings.
    - **If `is_sufficient` is `true`**: Your research is complete.

4.  **SYNTHESIZE & ANSWER**: Once `is_sufficient` is `true`, you MUST formulate a final, comprehensive answer for the user. Base your answer on the `summary_of_findings` from the LAST tool call. Do not call any more tools.

You must continue this loop until you have sufficient information to provide a high-quality answer.
"""

    agent = ReActAgent.from_tools(
        tools=tools,
        llm=Settings.llm,
        system_prompt=system_prompt,
        verbose=True,
        callback_manager=callback_manager,
    )

    return agent


# Function to clear the state cache after a request is complete
def clear_state_cache():
    __temp_state_cache.clear()
