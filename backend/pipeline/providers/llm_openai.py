import base64
from openai import OpenAI


class OpenAILLM:
    def __init__(self, model, api_key, temperature=None):
        self.client = OpenAI(api_key=api_key, timeout=180, max_retries=2)
        self.model = model

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
        )
        if r.status != "completed":
            raise RuntimeError(
                "OpenAI response incomplete; increase stage token budget"
            )
        return r.output_text, {
            "input_tokens": r.usage.input_tokens,
            "output_tokens": r.usage.output_tokens,
        }
