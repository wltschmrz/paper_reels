import os
from pathlib import Path
from typing import Protocol

import numpy as np

MODELS_DIR = Path(os.environ.get("SS_MODELS_DIR", Path.home() / ".cache" / "scholarshorts" / "models"))


class TTS(Protocol):
    def synth(self, text: str, lang: str) -> tuple[np.ndarray, int]: ...


class ASR(Protocol):
    def transcribe(self, samples: np.ndarray, sr: int, lang: str) -> str: ...


class LLM(Protocol):
    def complete(self, system: str, user: str, images: list[bytes] | None = None, max_tokens: int = 8000) -> tuple[str, dict]: ...


def get_tts(choice):
    if choice.provider == "supertonic_local":
        from .tts_supertonic import SupertonicTTS
        return SupertonicTTS(**choice.params)
    raise ValueError(f"unknown tts provider {choice.provider}")


def get_asr(choice):
    if choice.provider == "sensevoice_local":
        from .asr_sensevoice import SenseVoiceASR
        return SenseVoiceASR(**choice.params)
    raise ValueError(f"unknown asr provider {choice.provider}")


def get_llm(choice, api_key: str):
    if choice.provider == "openai":
        from .llm_openai import OpenAILLM
        return OpenAILLM(choice.model, api_key, **choice.params)
    if choice.provider == "anthropic":
        from .llm_anthropic import AnthropicLLM
        return AnthropicLLM(choice.model, api_key, **choice.params)
    raise ValueError(f"unknown llm provider {choice.provider}")
