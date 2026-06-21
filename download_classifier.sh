#!/usr/bin/env bash
# Download ONNX coffee leaf classifier (separate from ADTC GGUF LLM).
# Output: model/coffee_model.onnx

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL_DIR="$HERE/model"
MODEL_FILE="$MODEL_DIR/coffee_model.onnx"

MODEL_URL="${CLASSIFIER_URL:-https://github.com/JosephWalusimbi-eng/Coffee-Leaf-Disease-Detector/releases/download/v1.0.0/coffee_model.onnx}"

mkdir -p "$MODEL_DIR"

if [[ -f "$MODEL_FILE" ]]; then
  echo "Classifier already present at $MODEL_FILE — skipping"
  exit 0
fi

for LEGACY in "$HERE/coffee_model.onnx" "$HERE/app/coffee_model.onnx"; do
  if [[ -f "$LEGACY" ]]; then
    cp "$LEGACY" "$MODEL_FILE"
    echo "Copied classifier from $LEGACY"
    exit 0
  fi
done

echo "Downloading classifier $MODEL_URL → $MODEL_FILE (~29 MB)…"

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
