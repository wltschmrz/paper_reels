import numpy as np
import scipy.signal as ss
import sherpa_onnx

from .base import MODELS_DIR

DIR = MODELS_DIR / "sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17"


class SenseVoiceASR:
    def __init__(self, threads: int = 2):
        self.rec = {}
        self.threads = threads

    def _get(self, lang):
        if lang not in self.rec:
            self.rec[lang] = sherpa_onnx.OfflineRecognizer.from_sense_voice(
                model=str(DIR / "model.int8.onnx"), tokens=str(DIR / "tokens.txt"), language=lang, use_itn=False,
                num_threads=self.threads)
        return self.rec[lang]

    def transcribe(self, samples, sr, lang):
        x = ss.resample_poly(samples, 16000, sr).astype(np.float32) if sr != 16000 else samples.astype(np.float32)
        x = np.concatenate([np.zeros(8000, np.float32), x, np.zeros(16000, np.float32)])
        r = self._get(lang)
        s = r.create_stream()
        s.accept_waveform(16000, x)
        r.decode_stream(s)
        return s.result.text
