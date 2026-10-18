import base64
import os

import anthropic


class AnthropicLLM:
    def __init__(self, model: str, api_key: str, temperature: float | None = None):
        self.client = anthropic.Anthropic(api_key=api_key, timeout=180, max_retries=2, default_headers={"anthropic-workspace-id": os.environ["ANTHROPIC_WORKSPACE_ID"]} if os.getenv("ANTHROPIC_WORKSPACE_ID") else None)
        self.model, self.temperature = model, temperature

    def complete(self, system, user, images=None, max_tokens=8000):
        content = [{"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                                "data": base64.b64encode(b).decode()}} for b in (images or [])]
        content.append({"type": "text", "text": user})
        r = self.client.messages.create(model=self.model, max_tokens=max_tokens,
                                        system=system, messages=[{"role": "user", "content": content}])
        if r.stop_reason == "max_tokens":
            raise RuntimeError("Claude response truncated; increase stage token budget")
        text = "".join(b.text for b in r.content if b.type == "text")
        return text, {"input_tokens": r.usage.input_tokens, "output_tokens": r.usage.output_tokens}
