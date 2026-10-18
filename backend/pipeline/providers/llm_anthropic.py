import base64
import os
import anthropic
from ..prompting import Block


def text_blocks(value):
    blocks = getattr(value, 'blocks', [Block(str(value), False)])
    return [dict(type='text', text=b.text, **({'cache_control': {'type': 'ephemeral'}} if b.cache else {})) for b in blocks if b.text]


class AnthropicLLM:
    def __init__(self, model, api_key, temperature=None):
        self.client = anthropic.Anthropic(api_key=api_key, timeout=600, max_retries=0,
            default_headers={'anthropic-workspace-id': os.environ['ANTHROPIC_WORKSPACE_ID']} if os.getenv('ANTHROPIC_WORKSPACE_ID') else None)
        self.model = model

    def complete(self, system, user, images=None, max_tokens=8000):
        sys = text_blocks(system)
        blocks = text_blocks(user)
        cached = [b for b in blocks if 'cache_control' in b]
        fresh = [b for b in blocks if 'cache_control' not in b]
        imgs = [{'type':'image','source':{'type':'base64','media_type':'image/png','data':base64.b64encode(b).decode()}} for b in images or []]
        content = cached + imgs + fresh
        if sum('cache_control' in b for b in sys + content) > 4:
            raise ValueError('Anthropic supports at most four cache breakpoints')
        with self.client.messages.stream(model=self.model,max_tokens=max_tokens,system=sys,messages=[{'role':'user','content':content}]) as stream:
            r = stream.get_final_message()
        u = r.usage
        return ''.join(b.text for b in r.content if b.type=='text'), {
            'input_tokens':u.input_tokens, 'output_tokens':u.output_tokens,
            'cache_write_tokens':getattr(u,'cache_creation_input_tokens',0) or 0,
            'cache_read_tokens':getattr(u,'cache_read_input_tokens',0) or 0,
            'incomplete':r.stop_reason=='max_tokens'}
