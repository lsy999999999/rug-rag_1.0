from typing import List, Dict, Any

from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.prompts import PromptTemplate
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.program import LLMTextCompletionProgram
from pydantic import BaseModel, Field


# Pydantic model for structured output from the evaluation step
class ResearchState(BaseModel):
    """Data model for the state of the research process."""

    is_sufficient: bool = Field(
        ...,
        description="Whether the retrieved information is sufficient to comprehensively answer the user's original query.",
    )
    summary_of_findings: str = Field(
        ...,
        description="A concise summary of the key information found in the retrieved documents relevant to the query.",
    )
    suggested_next_queries: List[str] = Field(
        default_factory=list,
        description="If information is not sufficient, provide a list of 1-3 new, more specific search queries to try next.",
    )


# The prompt for the LLM program that evaluates the retrieved context
EVALUATION_PROMPT_TEMPLATE = """
As a research assistant, your task is to evaluate a set of retrieved document snippets to determine if they contain enough information to answer a user's original query.

**User's Original Query:**
{user_query}

**Retrieved Document Snippets:**
---------------------
{context_str}
---------------------

Based on the snippets, analyze the information and determine your next step. The goal is to gather enough information to provide a comprehensive, well-supported answer.

**Your output must be a JSON object with the following structure:**
- `is_sufficient`: boolean - Is the information sufficient to answer the query fully?
- `summary_of_findings`: string - A concise summary of what you've learned so far.
- `suggested_next_queries`: array of strings - If not sufficient, what are 1-3 *different* and *more specific* queries to try next? If sufficient, this should be an empty list.

{format_instructions}
"""


async def research_and_evaluate(
    user_query: str, search_query: str, index: VectorStoreIndex
) -> Dict[str, Any]:
    """
    Performs a single research step:
    1. Retrieves documents based on the search_query.
    2. Evaluates if the retrieved documents are sufficient to answer the user_query.
    3. Returns a structured state object including summaries and suggestions for the next steps.
    """
    print(
        f"🔬 Conducting research step. User Query: '{user_query}', Search Query: '{search_query}'"
    )

    # 1. Retrieve documents
    retriever = index.as_retriever(similarity_top_k=5)
    nodes = await retriever.aretrieve(search_query)

    if not nodes:
        return {
            "is_sufficient": False,
            "summary_of_findings": "No documents were found for the query. Please try a different query.",
            "suggested_next_queries": [],
            "retrieved_docs_preview": [],
        }

    context_str = "\n\n".join([n.get_content() for n in nodes])

    # Prepare the document previews to be sent to the frontend immediately
    retrieved_docs_preview = [
        {
            "file_name": node.metadata.get("file_name", "N/A"),
            "score": f"{node.get_score():.2f}",
            "content": node.get_text()[:150] + "...",
        }
        for node in nodes
    ]

    # 2. Evaluate sufficiency and suggest next steps
    program = LLMTextCompletionProgram.from_defaults(
        output_parser=PydanticOutputParser(output_cls=ResearchState),
        prompt=PromptTemplate(EVALUATION_PROMPT_TEMPLATE, prompt_type="program"),
        llm=Settings.llm,
        verbose=True,
    )

    response_obj: ResearchState = await program.acall(
        user_query=user_query, context_str=context_str
    )

    # 3. Combine evaluation results with document previews
    final_result = response_obj.model_dump()
    final_result["retrieved_docs_preview"] = retrieved_docs_preview

    print(f"🔍 Research step complete. Evaluation: {final_result}")

    return final_result
