import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def resolved(name, default):
    p = Path(os.getenv(name, default))
    return p if p.is_absolute() else (ROOT / p).resolve()


DATA = resolved("SS_DATA_DIR", "data")
MODELS = resolved("SS_MODELS_DIR", "models")
os.environ["SS_MODELS_DIR"] = str(MODELS)
API_TOKEN = os.getenv("SS_API_TOKEN", "")
LLM_STAGES = ("understand", "storyboard", "visual_code", "visual_qa", "judge")


def keys():
    return {
        "openai": os.getenv("OPENAI_API_KEY", ""),
        "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
    }


def model_choices():
    return [
        {"provider": "openai", "model": os.getenv("SS_OPENAI_MODEL", "gpt-6-astra")},
        {
            "provider": "anthropic",
            "model": os.getenv("SS_ANTHROPIC_MODEL", "claude-opus-5-5"),
        },
        {
            "provider": "anthropic",
            "model": os.getenv("SS_ANTHROPIC_REVIEW_MODEL", "claude-sonnet-5-5"),
        },
    ]
