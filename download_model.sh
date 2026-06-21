#!/usr/bin/env bash
# ADTC 2026 — download GGUF LLM for agriculture advisory (llama.cpp).
# Idempotent. Output must match _runtime.model_path in metadata.json.
#
# NOTE: The coffee leaf CNN classifier (ONNX) is NOT convertible to GGUF.
# Run download_classifier.sh for model/coffee_model.onnx.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL_DIR="$HERE/model"
MODEL_FILE="$MODEL_DIR/SmolLM2-360M-Instruct-Q4_K_M.gguf"

MODEL_URL="${MODEL_URL:-https://huggingface.co/bartowski/SmolLM2-360M-Instruct-GGUF/resolve/main/SmolLM2-360M-Instruct-Q4_K_M.gguf}"

mkdir -p "$MODEL_DIR"

if [[ -f "$MODEL_FILE" ]]; then
  echo "GGUF model already present at $MODEL_FILE — skipping download"
  exit 0
fi

echo "Downloading $MODEL_URL → $MODEL_FILE (~248 MB)…"

if command -v curl > /dev/null 2>&1; then
  curl -L --fail --progress-bar -o "$MODEL_FILE.partial" "$MODEL_URL"
elif command -v wget > /dev/null 2>&1; then
  wget --show-progress -O "$MODEL_FILE.partial" "$MODEL_URL"
else
  echo "error: neither curl nor wget found" >&2
  exit 1
fi

mv "$MODEL_FILE.partial" "$MODEL_FILE"
echo "done: $MODEL_FILE"
