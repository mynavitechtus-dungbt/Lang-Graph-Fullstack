"""Resolve chat model id from MODEL_NAME (must match your OpenAI-compatible API)."""

import os

# Widely available on the OpenAI API; override via MODEL_NAME in .env
DEFAULT_MODEL_NAME = "gpt-4o-mini"


def get_model_name() -> str:
    raw = (os.getenv("MODEL_NAME") or "").strip()
    return raw if raw else DEFAULT_MODEL_NAME
