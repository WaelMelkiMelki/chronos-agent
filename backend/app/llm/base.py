"""Provider-agnostic LLM interface for the agent."""


from __future__ import annotations


from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Sequence
from typing import Any


from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool




class LLMProvider(ABC):
    """Uniform access to a chat model + tool binding."""


    name: str


    @abstractmethod
    def chat_model(self) -> BaseChatModel:
        """Return the underlying LangChain chat model."""


    def bind_tools(self, tools: Sequence[BaseTool]) -> BaseChatModel:
        return self.chat_model().bind_tools(list(tools))


    async def ainvoke(
        self,
        messages: list[BaseMessage],
        tools: Sequence[BaseTool] | None = None,
        **kwargs: Any,
    ) -> BaseMessage:
        model = self.bind_tools(tools) if tools else self.chat_model()
        return await model.ainvoke(messages, **kwargs)  # type: ignore[return-value]


    async def astream(
        self,
        messages: list[BaseMessage],
        tools: Sequence[BaseTool] | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[BaseMessage]:
        model = self.bind_tools(tools) if tools else self.chat_model()
        async for chunk in model.astream(messages, **kwargs):  # type: ignore[attr-defined]
            yield chunk  # type: ignore[misc]
