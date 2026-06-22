# CoffeeVision — Models Guide

**Project:** CoffeeVision — AI-based Coffee leaf disease detector and Advisory system  
**Team:** Joseph Walusimbi & Chelangat Specioza — Soroti University, Uganda  
**Challenge:** ADTC 2026 — Agriculture domain  

This document explains the **two AI models** at the heart of CoffeeVision: what they are, what each one does, why we chose them, and how they fit together in an offline system for Ugandan coffee farmers.

If you are a judge, collaborator, or new developer reading this repository for the first time, start here.

---

## Table of contents

1. [The big picture](#1-the-big-picture)
2. [Model 1: The ONNX classifier (vision)](#2-model-1-the-onnx-classifier-vision)
3. [Model 2: The GGUF language model (text)](#3-model-2-the-gguf-language-model-text)
4. [How the two models work together](#4-how-the-two-models-work-together)
5. [What is *not* an AI model in this app](#5-what-is-not-an-ai-model-in-this-app)
6. [Why we chose these models](#6-why-we-chose-these-models)
7. [ADTC 2026 submission context](#7-adtc-2026-submission-context)
8. [Performance and hardware](#8-performance-and-hardware)
9. [Known limitations and future work](#9-known-limitations-and-future-work)
10. [Quick reference](#10-quick-reference)

---

## 1. The big picture

CoffeeVision helps **smallholder coffee farmers** in Uganda and East Africa detect leaf diseases early and get practical advice — **without internet**, on a normal **8 GB laptop**.

The app uses a **dual-model architecture**:

| Model | File | Job | Runtime |
|-------|------|-----|---------|
| **Vision classifier** | `model/coffee_model.onnx` | Look at a leaf photo → name the disease | ONNX Runtime (CPU) |
| **Language model (LLM)** | `model/SmolLM2-360M-Instruct-Q4_K_M.gguf` | Answer follow-up questions in natural language | llama.cpp via `llama-cpp-python` |

These are **different types of AI** solving **different problems**:

- The **ONNX model** sees images.
- The **LLM** reads and writes text.

You **cannot** replace one with the other. A language model cannot classify a coffee leaf photo. A CNN cannot hold a conversation. That is why both exist.

---

## 2. Model 1: The ONNX classifier (vision)

### What is ONNX?

**ONNX** (Open Neural Network Exchange) is an open format for storing trained machine learning models so they can run across platforms and runtimes.

In our project:

- The model was originally trained as a **convolutional neural network (CNN)** — specifically **DenseNet121** — for image classification.
- It was **exported** to the `.onnx` file format.
- At runtime, **ONNX Runtime** loads the file and runs inference on the CPU — no GPU required, no cloud required.

Think of ONNX as a **portable, offline-ready package** for the vision part of the app.

### What is `coffee_model.onnx`?

| Property | Value |
|----------|-------|
| **File** | `model/coffee_model.onnx` |
| **Size** | ~29 MB |
| **Architecture (training)** | DenseNet121 CNN |
| **Input** | One RGB image, resized to **224×224** pixels, normalized to 0–1 |
| **Output** | Scores for **3 classes** |
| **Inference time** | ~0.5–1 second per image (CPU) |
| **Download** | `download_classifier.sh` / `download_classifier.ps1` |

### What does it classify?

The model predicts one of three labels:

| Model output | Internal key | Meaning |
|--------------|--------------|---------|
| `healthy leaves` | `healthy_leaves` | Leaf appears healthy |
| `Leaf rust` | `leaf_rust` | Coffee leaf rust (*Hemileia vastatrix*) — often orange-yellow powder on undersides |
| `Phoma` | `phoma` | Phoma leaf spot — dark lesions, holes, premature drop |

### What can it do?

- Accept a photo from **upload** or **webcam capture**
- Return the **predicted class** and **confidence score** (e.g. Leaf rust, 91%)
- Run **fully offline** after the file is downloaded
- Work on **integrated GPU laptops** (CPU-only inference)

### What can it *not* do?

- Explain *why* a disease occurred or write treatment paragraphs (that is the LLM or curated advisories)
- Understand Kiswahili or English text input
- Detect diseases outside the three trained classes
- Guarantee accuracy on blurry, non-leaf, or out-of-distribution photos

### How it runs in the app

1. Farmer uploads or captures a leaf photo in the browser.
2. Flask receives the image at `POST /predict`.
3. OpenCV resizes the image to 224×224 and normalizes pixel values.
4. ONNX Runtime runs the model and picks the highest-scoring class.
5. The result is shown in the UI (in English or Kiswahili via locale files) and stored in the user session for later advisory/chat context.

**Code entry point:** `app/onnx_server.py` (loads ONNX at server startup)

---

## 3. Model 2: The GGUF language model (text)

### What is this model?

We use **SmolLM2-360M-Instruct**, a small **instruction-tuned language model** with roughly **360 million parameters**.

| Property | Value |
|----------|-------|
| **Base model** | SmolLM2-360M-Instruct |
| **Quantization** | **Q4_K_M** (4-bit GGUF) |
| **File** | `model/SmolLM2-360M-Instruct-Q4_K_M.gguf` |
| **Size** | ~248 MB |
| **Runtime (ADTC evaluation)** | **llama.cpp** |
| **Runtime (Flask app)** | **llama-cpp-python** (Python wrapper around llama.cpp) |
| **Download** | `download_model.sh` / `download_model.ps1` |
| **Source** | [bartowski/SmolLM2-360M-Instruct-GGUF](https://huggingface.co/bartowski/SmolLM2-360M-Instruct-GGUF) on Hugging Face |

### What is GGUF?

**GGUF** is a file format for storing quantized large language models so they can run efficiently on consumer hardware through **llama.cpp**.

**Quantization** means the model weights are compressed to use less memory. **Q4_K_M** is a 4-bit scheme that balances:

- **Small file size** (~248 MB)
- **Acceptable answer quality** for farmer Q&A
- **Safe RAM usage** on an 8 GB laptop

### What is llama.cpp?

**llama.cpp** is an open-source inference engine for running GGUF models on CPU (and optionally GPU). ADTC 2026 **requires** submissions to use llama.cpp — no other LLM runtime is accepted for official scoring.

In our app, `llama-cpp-python` loads the same `.gguf` file and exposes a Python API used by `app/llm_advisor.py`.

### What can the LLM do?

In CoffeeVision, the LLM powers the **“Ask CoffeeVision” chat panel**:

- Answer **follow-up questions** about coffee diseases, prevention, and farm practice
- Respond in **English** or **Kiswahili** (with quality checks and retry logic for Swahili)
- Use **conversation context** (last 8 messages) and the **last classification result** when available
- Run **fully offline** after the GGUF file is downloaded
- Translate chat messages when the user switches language mid-session

**Example farmer questions the LLM handles:**

- “What fungicide should I use for leaf rust?”
- “Majani yangu yana doa nyeusi — ni nini cha kufanya?”
- “How do I stop this spreading to the next row of trees?”

### What can the LLM *not* do?

- **Classify leaf images** — it never receives the photo; the ONNX model does that
- **Replace curated advisories** — the “Get AI Advisory” button uses expert-written JSON templates, not the LLM (by design, for consistency)
- **Browse the internet** or call cloud APIs — it only knows what is in its weights and what we put in the system prompt
- **Speak Kiswahili perfectly** — SmolLM2-360M is English-centric; we add heuristics and retries to improve Swahili chat quality

### How it runs in the app

1. Farmer types a message in the chat panel.
2. Flask receives it at `POST /api/chat`.
3. `llm_advisor.py` builds a system prompt with coffee disease facts and (if available) the last scan result.
4. The GGUF model is loaded **lazily on first chat request** (~258 MB in memory), then kept loaded.
5. Settings: CPU-only (`n_gpu_layers=0`), 2048-token context, up to 4 threads.

**Code entry point:** `app/llm_advisor.py`

---

## 4. How the two models work together

A typical farmer session looks like this:

```
┌─────────────────────────────────────────────────────────────────┐
│  1. UPLOAD / CAPTURE                                            │
│     Farmer takes or uploads a coffee leaf photo                 │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. CLASSIFY  (ONNX — coffee_model.onnx)                        │
│     → "Leaf rust, 91% confidence"                               │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. GET AI ADVISORY  (curated locales — NOT the LLM)            │
│     → Structured Symptoms + Countermeasures in EN or SW         │
│     → Instant, consistent, expert-written HTML                  │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. ASK COFFEEVISION  (GGUF — SmolLM2-360M)                     │
│     → Natural conversation, follow-up questions                 │
│     → Uses last classification as context                       │
└─────────────────────────────────────────────────────────────────┘
```

**Why split advisory and chat?**

| Path | Technology | Why |
|------|------------|-----|
| **Get AI Advisory** | `locales/en.json`, `locales/sw.json` | Reliable, structured, farmer-verified content every time |
| **Ask CoffeeVision chat** | SmolLM2 GGUF | Flexible natural language for questions we did not pre-write |

---

## 5. What is *not* an AI model in this app

These are important parts of CoffeeVision but **not** separate ML models:

| Component | Role |
|-----------|------|
| **`locales/en.json` and `locales/sw.json`** | UI strings + structured farmer advisories (Symptoms / Countermeasures) |
| **SQLite (`users.db`)** | Local user accounts — no cloud auth |
| **`app/static/css/app.css`** | Local styling — no CDN |
| **Flask web server** | Serves pages and connects browser to ONNX + LLM |

Everything above runs offline after initial setup (`pip install` + model downloads).

---

## 6. Why we chose these models

### Why SmolLM2-360M-Instruct at Q4_K_M?

We did not pick the “best” LLM on the market. We picked the one that **fits the real-world and ADTC constraints**.

| Requirement | How SmolLM2-360M Q4_K_M fits |
|-------------|------------------------------|
| **ADTC rules** | Must use **GGUF + llama.cpp** — this model is publicly available in that format |
| **8 GB RAM laptop** | Peak LLM memory ~**375 MB** in constrained profiler runs — safe alongside ONNX + Flask |
| **CPU-only** | Runs on integrated graphics laptops with `n_gpu_layers=0` |
| **Offline** | No API keys, no cloud calls at inference time |
| **Instruct-tuned** | Built for Q&A/chat-style prompts, matching our farmer chatbot |
| **Size vs quality** | Larger than template 135M examples, but far smaller than 1B/7B models that would risk OOM |

**Alternatives we rejected:**

| Alternative | Why rejected |
|-------------|--------------|
| **Cloud LLMs (OpenAI, etc.)** | Cost, connectivity, and privacy — impractical for rural Uganda |
| **Larger LLMs (1B+, 7B)** | Would exceed 8 GB RAM when combined with the CNN and web app — ADTC OOM = disqualification |
| **Lower quantization (Q2_K)** | Smaller file, but noticeably worse farmer-facing answers |
| **Higher quantization (Q8) / bigger models** | Better quality, but too much RAM |
| **One multimodal model for everything** | Would need a large vision-language model — violates our RAM budget |

**Known trade-off:** SmolLM2-360M is **weaker in Kiswahili** than in English. We compensate with Kiswahili quality checks, simpler retry prompts, and curated Swahili advisories for the structured advisory path.

### Why DenseNet121 exported as ONNX?

| Requirement | How the ONNX classifier fits |
|-------------|------------------------------|
| **Speed** | ~0.5–1 s per image on CPU — fast enough for field use |
| **Size** | ~29 MB — negligible compared to LLM RAM |
| **Offline** | ONNX Runtime runs locally with no GPU |
| **Task fit** | CNNs are the standard architecture for image classification |
| **Three local classes** | Matches Ugandan farmer needs: healthy, Leaf rust, Phoma |

**Why not convert ONNX to GGUF?**

GGUF and llama.cpp are for **language models** (text in → text out). Our classifier is a **CNN** (image in → class scores). Different architecture, different runtime. They must stay separate.

---

## 7. ADTC 2026 submission context

CoffeeVision is submitted to the **Africa Deep Tech Challenge 2026** (Agriculture domain). Here is how the models relate to official requirements.

### What ADTC evaluates

The **ADTC profiler** benchmarks only the **GGUF LLM** via llama.cpp:

- Tokens per second (throughput)
- Peak RAM (RSS)
- CPU / thermal behavior
- Quality on **2 test prompts** in `metadata.json` (+ 2 hidden organizer prompts)

The **ONNX classifier is not scored** by the profiler, but it is central to the **real farmer application**.

### Our LLM in `metadata.json`

```json
"model": {
  "name": "SmolLM2-360M-Instruct-Q4_K_M",
  "runtime": "llama.cpp",
  "quantization": "GGUF Q4_K_M",
  "parameters_estimate": "360M",
  "packaging": "binary_bundle"
},
"_runtime": {
  "model_path": "model/SmolLM2-360M-Instruct-Q4_K_M.gguf"
}
```

### Test prompts (image-workflow aligned)

Our two official test prompts describe the **real app pipeline** — upload → ONNX classification → advisory — not generic chatbot questions:

1. **English:** Farmer uploads photo → classifier returns Leaf rust at 91% → LLM lists countermeasures.
2. **Kiswahili:** Farmer uploads photo offline → classifier returns Phoma at 88% → LLM writes Swahili guidance.

These prompts are what judges and the profiler use to assess **LLM response quality** (50% of the leaderboard score).

### Submission compliance notes

| Item | Status |
|------|--------|
| `domain: agriculture` | Correct |
| `language_scope: ["en", "sw"]` | English + Kiswahili |
| `african_alpha_claim: true` | Valid with Kiswahili + Ugandan use case |
| `budget_laptop_claim: true` | Required; matches 8 GB target |
| Model weights in git | **Not committed** — downloaded via scripts |
| Offline inference | **No CDN or external APIs** during classification, advisories, or chat |
| `team_id` | Placeholder until ADTF assigns official ID — **must update before final submission** |

### Scoring formula (LLM only)

$$S_{\text{total}} = 0.50 \cdot S_{\text{acc}} + 0.30 \cdot S_{\text{perf}} + 0.20 \cdot S_{\text{eff}} - P_{\text{thermal}}$$

- **S_acc** — quality of prompt responses (your test prompts matter)
- **S_perf** — tokens/sec vs reference (~15 TPS)
- **S_eff** — RAM efficiency vs 7 GB budget
- **P_thermal** — penalty if CPU throttles or exceeds 85°C

**Disqualification risk:** out-of-memory (OOM) during evaluation. Our ~375 MB LLM peak RSS is well within limits.

---

## 8. Performance and hardware

Developed and tested on an **HP EliteBook** — Intel Core i5 @ 2.20 GHz, **8 GB RAM**, integrated graphics.

| Component | Metric |
|-----------|--------|
| **ONNX classifier** | ~0.5–1 s per image; ~29 MB file; app + ONNX ~500 MB–1 GB RAM |
| **GGUF LLM (constrained Docker profile)** | ~2.8 tokens/sec; ~375 MB peak RSS; no thermal throttling |
| **GGUF LLM (host smoke test)** | ~17.4 tokens/sec; ~394 MB peak RSS |

The constrained Docker run uses a conservative CPU-only llama.cpp build (no AVX) to mirror commodity audit laptops — slower TPS but representative RAM behavior.

---

## 9. Known limitations and future work

### ONNX classifier

- Only three classes — cannot detect every coffee disease
- Accuracy drops on poor photos (blur, shadows, non-leaf images)
- Requires separate download (`download_classifier.sh`) — app will not start without it

### SmolLM2 LLM

- May **hallucinate** fungicide names or details in chat — farmers should treat chat as guidance, not sole authority
- **Kiswahili quality** is weaker than English
- First chat request has a **load delay** while the GGUF is read into memory
- Constrained profiler **first-token latency** is very high (~95 s) on the audit Docker build — real app chat on host hardware is faster

### Planned improvements (documented in repo)

- Fine-tune SmolLM2 on agriculture Q&A and Kiswahili corpus (improve S_acc)
- Expand disease classes with more Ugandan field data
- Mobile deployment with ONNX-only mode for lighter devices

---

## 10. Quick reference

### Files on disk (not in git)

```
model/
├── coffee_model.onnx                          # ONNX CNN classifier (~29 MB)
└── SmolLM2-360M-Instruct-Q4_K_M.gguf          # GGUF LLM (~248 MB)
```

### Download commands (repo root)

```powershell
.\download_classifier.ps1   # ONNX classifier
.\download_model.ps1        # GGUF LLM (ADTC + chatbot)
```

```bash
bash download_classifier.sh
bash download_model.sh
```

### Which model powers what?

| Feature | Model / source |
|---------|----------------|
| Upload / webcam classify | **ONNX** (`coffee_model.onnx`) |
| Get AI Advisory button | **Locale JSON** (curated, not LLM) |
| Ask CoffeeVision chat | **GGUF LLM** (SmolLM2-360M) |
| ADTC profiler scoring | **GGUF LLM** only |
| UI language (EN / SW) | **Locale JSON** |

### Key source files

| File | Purpose |
|------|---------|
| `app/onnx_server.py` | Flask server, ONNX inference, API routes |
| `app/llm_advisor.py` | GGUF chat, Kiswahili handling, advisory helper |
| `app/locales/en.json`, `sw.json` | UI + structured advisories |
| `metadata.json` | ADTC submission metadata and test prompts |
| `REPORT.md` | Official ADTC technical report |
| `TECHNICAL_REFERENCE.md` | Extended Q&A for judges and interviews |

---

## Summary

CoffeeVision is built for **offline agriculture** on a **budget laptop**:

- **ONNX (DenseNet121)** answers: *“What disease is on this leaf?”*
- **SmolLM2-360M-Instruct (GGUF Q4_K_M via llama.cpp)** answers: *“What should I do next?”* in conversation
- **Curated locale files** deliver reliable structured advisories without depending on LLM quality

We chose each model for **fit to constraints** — RAM, CPU, connectivity, ADTC rules, and farmer needs — not for maximum model size or cloud capability.

For setup instructions, see [`app/howtorun.md`](app/howtorun.md).  
For judge Q&A prep, see [`TECHNICAL_REFERENCE.md`](../TECHNICAL_REFERENCE.md).  
For the official ADTC writeup, see [`REPORT.md`](REPORT.md).
