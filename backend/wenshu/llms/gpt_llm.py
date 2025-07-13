# 文件路径: /backend/wenshu/llms/gpt_llm.py

import os
from typing import Any, AsyncGenerator, Generator, List, Optional, Sequence

from llama_index.core.base.llms.types import (
    ChatMessage, ChatResponse, ChatResponseGen, CompletionResponse,
    CompletionResponseGen, LLMMetadata
)
from llama_index.core.llms.custom import CustomLLM
from openai import OpenAI, AsyncOpenAI

class GPTCustomLLM(CustomLLM):
    """
    A custom LlamaIndex LLM wrapper for any OpenAI-compatible API,
    including the official GPT models.
    """
    model: str
    api_key: str
    api_base: Optional[str] = None # api_base can be optional

    _client: OpenAI
    _async_client: AsyncOpenAI

    # --- START: MODIFIED __init__ METHOD ---
    def __init__(
        self,
        model: str = "gpt-4-turbo", # Provide a default model
        api_key: Optional[str] = None,
        api_base: Optional[str] = None, # It's better to get this from env vars if not provided
    ) -> None:
        # Pydantic will automatically assign model, api_key, api_base to self
        # We call super().__init__() with these values to ensure they are properly set
        # in the Pydantic model before we use them.
        
        # Resolve values from environment variables if not provided directly
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        api_base = api_base or os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be provided either as an argument or as an environment variable.")

        # Pass resolved values to the Pydantic model's __init__
        super().__init__(model=model, api_key=api_key, api_base=api_base)

        # Now, initialize the clients using the values stored in self
        self._client = OpenAI(api_key=self.api_key, base_url=self.api_base)
        self._async_client = AsyncOpenAI(api_key=self.api_key, base_url=self.api_base)
    # --- END: MODIFIED __init__ METHOD ---
        
    @property
    def metadata(self) -> LLMMetadata:
        """Get LLM metadata."""
        # A more robust way to get context_window based on model
        context_window = 4096 
        if "gpt-4" in self.model:
            context_window = 8192
        if "16k" in self.model:
            context_window = 16384
        if "32k" in self.model:
            context_window = 32768
        
        return LLMMetadata(
            context_window=context_window,
            num_output=4096,
            is_chat_model=True,
            model_name=self.model,
        )

    def _to_openai_messages(self, messages: Sequence[ChatMessage]) -> List[dict]:
        return [
            {"role": msg.role.value, "content": msg.content} for msg in messages
        ]

    # --- Synchronous Methods ---
    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        openai_messages = self._to_openai_messages(messages)
        response = self._client.chat.completions.create(
            model=self.model, messages=openai_messages, **kwargs
        )
        return ChatResponse(
            message=ChatMessage(
                role=response.choices[0].message.role,
                content=response.choices[0].message.content,
            ),
            raw=response.model_dump(),
        )

    def stream_chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponseGen:
        openai_messages = self._to_openai_messages(messages)
        response_stream = self._client.chat.completions.create(
            model=self.model, messages=openai_messages, stream=True, **kwargs
        )
        def gen() -> Generator[ChatResponse, None, None]:
            content, role = "", "assistant"
            for chunk in response_stream:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta.role:
                        role = delta.role
                    if delta.content:
                        content += delta.content
                        yield ChatResponse(
                            message=ChatMessage(role=role, content=content),
                            delta=delta.content,
                            raw=chunk.model_dump(),
                        )
        return gen()

    # --- Asynchronous Methods ---
    async def achat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        openai_messages = self._to_openai_messages(messages)
        response = await self._async_client.chat.completions.create(
            model=self.model, messages=openai_messages, **kwargs
        )
        return ChatResponse(
            message=ChatMessage(
                role=response.choices[0].message.role,
                content=response.choices[0].message.content,
            ),
            raw=response.model_dump(),
        )

    async def astream_chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> AsyncGenerator[ChatResponse, None]:
        openai_messages = self._to_openai_messages(messages)
        response_stream = await self._async_client.chat.completions.create(
            model=self.model, messages=openai_messages, stream=True, **kwargs
        )
        async def gen() -> AsyncGenerator[ChatResponse, None]:
            content, role = "", "assistant"
            async for chunk in response_stream:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta.role:
                        role = delta.role
                    if delta.content:
                        content += delta.content
                        yield ChatResponse(
                            message=ChatMessage(role=role, content=content),
                            delta=delta.content,
                            raw=chunk.model_dump(),
                        )
        return gen()
        
    # --- Completion methods ---
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        response = self.chat([ChatMessage(role="user", content=prompt)], **kwargs)
        return CompletionResponse(text=response.message.content or "", raw=response.raw)

    def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
        stream = self.stream_chat([ChatMessage(role="user", content=prompt)], **kwargs)
        def gen() -> Generator[CompletionResponse, None, None]:
            for chunk in stream:
                yield CompletionResponse(text=chunk.message.content or "", delta=chunk.delta, raw=chunk.raw)
        return gen()

    async def acomplete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        response = await self.achat([ChatMessage(role="user", content=prompt)], **kwargs)
        return CompletionResponse(text=response.message.content or "", raw=response.raw)

    async def astream_complete(self, prompt: str, **kwargs: Any) -> AsyncGenerator[CompletionResponse, None]:
        stream = await self.astream_chat([ChatMessage(role="user", content=prompt)], **kwargs)
        async def gen() -> AsyncGenerator[CompletionResponse, None]:
            async for chunk in stream:
                yield CompletionResponse(text=chunk.message.content or "", delta=chunk.delta, raw=chunk.raw)
        return gen()