import numpy as np
import sherpa_onnx

from .base import MODELS_DIR

DIR = MODELS_DIR / "sherpa-onnx-supertonic-3-tts-int8-2026-05-11"


class SupertonicTTS:
    def __init__(self, sid: int = 9, num_steps: int = 16, threads: int = 2):
        d = str(DIR) + "/"
        cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
            supertonic=sherpa_onnx.OfflineTtsSupertonicModelConfig(
                duration_predictor=d + "duration_predictor.int8.onnx", text_encoder=d + "text_encoder.int8.onnx",
                vector_estimator=d + "vector_estimator.int8.onnx", vocoder=d + "vocoder.int8.onnx",
                tts_json=d + "tts.json", unicode_indexer=d + "unicode_indexer.bin", voice_style=d + "voice.bin"),
            num_threads=threads, provider="cpu"))
        self.tts = sherpa_onnx.OfflineTts(cfg)
        self.sid, self.num_steps = sid, num_steps

    def synth(self, text, lang):
        g = sherpa_onnx.GenerationConfig()
        g.sid, g.num_steps, g.speed = self.sid, self.num_steps, 1.0
        g.extra["lang"] = lang
        a = self.tts.generate(text, g)
        return np.asarray(a.samples, dtype=np.float32), a.sample_rate
