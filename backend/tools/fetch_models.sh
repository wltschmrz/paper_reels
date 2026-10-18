#!/usr/bin/env bash
set -euo pipefail
D="${SS_MODELS_DIR:-$HOME/.cache/scholarshorts/models}"
mkdir -p "$D" && cd "$D"
R=https://github.com/k2-fsa/sherpa-onnx/releases/download
[ -d sherpa-onnx-supertonic-3-tts-int8-2026-05-11 ] || { curl -fSL -O $R/tts-models/sherpa-onnx-supertonic-3-tts-int8-2026-05-11.tar.bz2; tar xf sherpa-onnx-supertonic-3-tts-int8-2026-05-11.tar.bz2; rm sherpa-onnx-supertonic-3-tts-int8-2026-05-11.tar.bz2; }
[ -d sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17 ] || { curl -fSL -O $R/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17.tar.bz2; tar xf sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17.tar.bz2; rm sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17.tar.bz2; }
echo "models in $D"
