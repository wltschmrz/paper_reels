import base64
from openai import OpenAI


class OpenAILLM:
    def __init__(self, model, api_key, temperature=None, reasoning_effort=None):
        self.client = OpenAI(api_key=api_key, timeout=180, max_retries=0)
        self.model = model
        self.reasoning_effort = reasoning_effort

    def complete(self, system, user, images=None, max_tokens=8000):
        content = [{"type": "input_text", "text": user}]
        content += [
            {
                "type": "input_image",
                "image_url": "data:image/png;base64," + base64.b64encode(b).decode(),
            }
            for b in images or []
        ]
        r = self.client.responses.create(
            model=self.model,
            instructions=system,
            input=[{"role": "user", "content": content}],
            max_output_tokens=max_tokens,
            store=False,
            **({"reasoning": {"effort": self.reasoning_effort}} if self.reasoning_effort else {}),
        )
        cached = getattr(getattr(r.usage, "input_tokens_details", None), "cached_tokens", 0) or 0
        return r.output_text, {
            "input_tokens": r.usage.input_tokens - cached,
            "cache_read_tokens": cached,
            "cache_write_tokens": 0,
            "incomplete": r.status != "completed",
            "output_tokens": r.usage.output_tokens,
        }
