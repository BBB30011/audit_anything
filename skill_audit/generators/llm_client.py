"""Lightweight OpenAI-compatible LLM client using httpx."""

from __future__ import annotations

import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Invokes OpenAI-compatible chat completion APIs (OpenAI, DeepSeek, Qwen, Ollama, etc.)."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 45.0,
    ) -> None:
        self.api_key = (
            api_key
            or os.getenv("SKILLAUDIT_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or ""
        )
        self.base_url = (
            base_url
            or os.getenv("SKILLAUDIT_BASE_URL")
            or os.getenv("OPENAI_BASE_URL")
            or "https://api.openai.com/v1"
        ).rstrip("/")
        self.model = (
            model
            or os.getenv("SKILLAUDIT_MODEL")
            or os.getenv("OPENAI_MODEL")
            or "gpt-4o-mini"
        )
        self.timeout = timeout

    @property
    def is_available(self) -> bool:
        """Return True if an API key is configured or local Ollama endpoint is specified."""
        return bool(self.api_key) or "localhost" in self.base_url or "127.0.0.1" in self.base_url

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 2000,
    ) -> str:
        """Call chat completions endpoint and return string output."""
        if not self.is_available:
            raise RuntimeError("LLM is not configured. Set SKILLAUDIT_API_KEY or OPENAI_API_KEY.")

        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        url = f"{self.base_url}/chat/completions"
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return str(data["choices"][0]["message"]["content"])
