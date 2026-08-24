from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
import httpx
import json


class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]


class ToolResult(BaseModel):
    name: str
    result: Any
    error: Optional[str] = None


class LLMMessage(BaseModel):
    role: str
    content: str
    tool_calls: Optional[List[ToolCall]] = None


class LLMResponse(BaseModel):
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    usage: Optional[Dict[str, int]] = None


class LLMProvider(ABC):
    @abstractmethod
    async def complete(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> LLMResponse:
        pass

    @abstractmethod
    async def close(self):
        pass


class MockProvider(LLMProvider):
    def __init__(self, responses: Optional[List[LLMResponse]] = None):
        self.responses = responses or []
        self.call_count = 0

    async def complete(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> LLMResponse:
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
        else:
            response = LLMResponse(
                content='{"status": "unresolved", "classification": "unknown_transaction", "confidence": 0.1, "explanation": "Mock provider: no more predefined responses", "evidence": [], "recommended_action": null}'
            )
        self.call_count += 1
        return response

    async def close(self):
        pass


class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1:8b", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def complete(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> LLMResponse:
        ollama_messages = [{"role": m.role, "content": m.content} for m in messages]
        
        payload = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": False,
            "options": {"temperature": 0.1},
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice or "auto"
        
        if response_format and response_format.get("type") == "json_object":
            payload["format"] = "json"

        response = await self.client.post(f"{self.base_url}/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        
        content = data.get("message", {}).get("content", "")
        tool_calls = data.get("message", {}).get("tool_calls")
        
        return LLMResponse(content=content, tool_calls=tool_calls)

    async def close(self):
        await self.client.aclose()


class GroqProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant", timeout: int = 30):
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(
            base_url="https://api.groq.com/openai/v1",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )

    async def complete(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> LLMResponse:
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": 0.1,
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice or "auto"
        
        if response_format and response_format.get("type") == "json_object":
            payload["response_format"] = {"type": "json_object"}

        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        
        choice = data["choices"][0]
        content = choice["message"].get("content", "")
        tool_calls = choice["message"].get("tool_calls")
        
        return LLMResponse(content=content, tool_calls=tool_calls, usage=data.get("usage"))

    async def close(self):
        await self.client.aclose()


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, base_url: str, api_key: str, model: str = "gpt-4o-mini", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )

    async def complete(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> LLMResponse:
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": 0.1,
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice or "auto"
        
        if response_format and response_format.get("type") == "json_object":
            payload["response_format"] = {"type": "json_object"}

        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        
        choice = data["choices"][0]
        content = choice["message"].get("content", "")
        tool_calls = choice["message"].get("tool_calls")
        
        return LLMResponse(content=content, tool_calls=tool_calls, usage=data.get("usage"))

    async def close(self):
        await self.client.aclose()


def get_provider(provider_type: str = "mock", **kwargs) -> LLMProvider:
    if provider_type == "mock":
        return MockProvider()
    elif provider_type == "ollama":
        return OllamaProvider(**kwargs)
    elif provider_type == "groq":
        return GroqProvider(**kwargs)
    elif provider_type == "openai_compatible":
        return OpenAICompatibleProvider(**kwargs)
    else:
        raise ValueError(f"Unknown provider: {provider_type}")