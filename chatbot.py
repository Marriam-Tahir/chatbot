"""Azure OpenAI chatbot backend for Nova."""

import os
from typing import Dict, Generator, List

from dotenv import load_dotenv
from openai import AzureOpenAI

# Loads .env locally. On Azure App Service the values come from
# Configuration > Application settings, so this is simply a no-op there.
load_dotenv()

DEFAULT_SYSTEM_PROMPT = (
    "You are Nova, a friendly and helpful AI assistant. "
    "Give clear, accurate and concise answers. "
    "If you are not sure about something, say so honestly."
)


class ConfigError(Exception):
    """Raised when required Azure OpenAI settings are missing."""


def get_config() -> Dict[str, str]:
    config = {
        "api_key": os.getenv("AZURE_OPENAI_API_KEY", "").strip(),
        "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", "").strip(),
        "deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip(),
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21").strip(),
    }
    missing = [
        name
        for name, value in {
            "AZURE_OPENAI_API_KEY": config["api_key"],
            "AZURE_OPENAI_ENDPOINT": config["endpoint"],
            "AZURE_OPENAI_DEPLOYMENT": config["deployment"],
        }.items()
        if not value
    ]
    if missing:
        raise ConfigError("Missing settings: " + ", ".join(missing))
    return config


def get_client() -> AzureOpenAI:
    cfg = get_config()
    return AzureOpenAI(
        api_key=cfg["api_key"],
        azure_endpoint=cfg["endpoint"],
        api_version=cfg["api_version"],
    )


def stream_reply(
    messages: List[Dict[str, str]],
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    temperature: float = 0.7,
    max_tokens: int = 800,
) -> Generator[str, None, None]:
    """Yield the assistant reply token by token."""
    cfg = get_config()
    client = get_client()

    full_messages = [{"role": "system", "content": system_prompt}] + messages

    stream = client.chat.completions.create(
        model=cfg["deployment"],  # this is the DEPLOYMENT name, not the model name
        messages=full_messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )

    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield delta.content
