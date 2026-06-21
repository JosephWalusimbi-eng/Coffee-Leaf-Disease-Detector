# CoffeeVision — Technical Reference (Q&A Prep)

**Project:** CoffeeVision — AI-based Coffee leaf disease detector and Advisory system  
**Team:** Joseph Walusimbi & Chelangat Specioza — Soroti University, Uganda  
**Challenge:** ADTC 2026 — Agriculture domain, Laptop LLM Challenge  
**Repository layout:** ADTC 2026 submission template  
**Last updated:** June 2026 (structured locale advisories + natural GGUF chatbot)

Use this document to prepare for technical interviews, judge Q&A, and DevPost follow-ups.

---

## 1. Executive summary

CoffeeVision is an **offline, bilingual (English / Kiswahili)** web application for **smallholder coffee farmers** in Uganda and East Africa. It combines:

1. **ONNX CNN** — classifies coffee leaf photos into three classes in under ~1 second on CPU.
2. **GGUF LLM (SmolLM2-360M)** — powers the **Ask CoffeeVision** chatbot via **llama.cpp** (`llama-cpp-python`). **Get AI Advisory** uses curated locale JSON, not the LLM.
3. **Curated locale advisories** — structured Symptoms / Countermeasures (and healthy best practices) in `locales/en.json` and `locales/sw.json` for **Get AI Advisory**.

Everything runs on a commodity laptop (**HP EliteBook**, Intel i5 @ 2.20 GHz, 8 GB RAM, 500 GB storage) without internet after models are downloaded.

---

## 2. Problem and design goal

| Challenge | Our response |
|-----------|--------------|
| Leaf diseases (rust, Phoma) spread before farmers get expert help | Fast image classification from phone/webcam photo |
| Rural connectivity is poor | Fully offline inference (ONNX + GGUF) |
| Cloud LLMs are costly and impractical | On-device 360M-parameter GGUF model (~248 MB) |
| Farmers need local languages | UI + advisories in English and Kiswahili |
| 8 GB laptop RAM budget (ADTC) | Peak GGUF RSS ~375 MB; ONNX ~29 MB |

---

## 3. Why two models? (critical Q&A topic)

**You cannot replace the ONNX classifier with the GGUF model.**

| | ONNX CNN | GGUF LLM |
|---|----------|----------|
| **Input** | Image (224×224 RGB) | Text |
| **Output** | 3 class probabilities | Generated text |
| **Architecture** | Convolutional neural network | Transformer language model |
| **Runtime** | ONNX Runtime | llama.cpp |
| **Role in app** | “What disease is on this leaf?” | “What should the farmer do?” |
| **ADTC profiler** | Not benchmarked | **Benchmarked** (TPS, RAM) |

This **hybrid architecture** is intentional: vision for perception, language model for explanation and dialogue.

---

## 4. System architecture

```mermaid
flowchart TB
    subgraph Client["Browser (farmer)"]
        UI[Flask templates + JS]
    end

    subgraph Flask["app/onnx_server.py"]
        Auth[Session auth + SQLite]
        Predict[/predict API]
        Advisory[/api/advisory]
        Chat[/api/chat]
        I18N[i18n.py + locales]
    end

    subgraph Vision["Vision pipeline"]
        ONNX[coffee_model.onnx]
        ORT[ONNX Runtime CPU]
    end

    subgraph Language["Language pipeline"]
        LLM[llm_advisor.py]
        GGUF[SmolLM2-360M Q4_K_M.gguf]
        LCP[llama-cpp-python]
        Static[locales/en.json + sw.json]
    end

    UI -->|POST image| Predict
    UI -->|POST JSON| Advisory
    UI -->|POST JSON| Chat
    Predict --> ORT --> ONNX
    Advisory --> I18N
    Chat --> LLM
    LLM --> LCP --> GGUF
    I18N --> Static
    I18N --> UI
    Auth --> UI
```

### Request flow — classification

1. User uploads image or captures webcam frame (base64 → blob).
2. `POST /predict` saves `uploaded_<timestamp>.jpg`.
3. Image resized to **224×224**, normalized to `[0,1]` float32.
4. ONNX Runtime runs inference → `argmax` → class + confidence.
5. Result stored in `session['last_classification']`.
6. Copy saved to `classified_images/<class>/<class>_<timestamp>.jpg`.

### Request flow — advisory

1. User clicks **Get AI Advisory** → `POST /api/advisory`.
2. `generate_advisory()` returns structured HTML from `locales/en.json` or `locales/sw.json` (`source: curated`).
3. If the class is missing in the selected language → English locale fallback (`source: static`).
4. **No GGUF inference** on this path — instant, consistent Symptoms / Countermeasures format.

### Request flow — chat

1. User types message → `POST /api/chat`.
2. Last 8 messages from `session['chat_history']` (max 20 stored).
3. **English and Kiswahili** → GGUF chat completion with coffee context in system prompt; conversational tone (no rigid advisory template).
4. Disease keywords may hint the system prompt but do **not** return the structured locale advisory.
5. **Kiswahili** → quality heuristic; poor output → retry with a simpler Kiswahili prompt (still natural text, not locale template).
6. If GGUF is unavailable → short static unavailable message (`source: static`).

---

## 5. Technology stack

| Layer | Technology | Version / notes |
|-------|------------|-----------------|
| Web framework | Flask | ≥3.1 |
| CORS | flask-cors | API access from browser |
| Vision | ONNX Runtime | CPU inference |
| Image I/O | Pillow, OpenCV | Resize, load, save |
| Numerics | NumPy | Tensor prep |
| LLM | llama-cpp-python | Wraps llama.cpp |
| LLM weights | SmolLM2-360M-Instruct | GGUF Q4_K_M (~258 MB) |
| Auth | Werkzeug + SQLite | Hashed passwords |
| Frontend | Jinja2 templates, vanilla JS | No React build step |
| Styles | `app/static/css/app.css` | Local CSS, no CDN |
| i18n | JSON locale files | `en`, `sw` |

**Python:** 3.10+ recommended.

---

## 6. Models (detailed)

### 6.1 ONNX classifier — `model/coffee_model.onnx`

| Property | Value |
|----------|-------|
| File size | ~29 MB |
| Input | 1×224×224×3 RGB, float32, scale 0–1 |
| Output | 3-class logits/probabilities |
| Classes | `healthy leaves`, `Leaf rust`, `Phoma` |
| Internal keys | `healthy_leaves`, `leaf_rust`, `phoma` |
| Inference time | ~0.5–1 s per image (CPU) |
| Load time | ~2–5 s at server startup |

**Preprocessing (must match training):**

```python
image_np = cv2.resize(image_np, (224, 224))
image_np = image_np.astype(np.float32) / 255.0
image_np = np.expand_dims(image_np, axis=0)  # batch dim
```

### 6.2 GGUF LLM — `model/SmolLM2-360M-Instruct-Q4_K_M.gguf`

| Property | Value |
|----------|-------|
| Base model | SmolLM2-360M-Instruct |
| Quantization | Q4_K_M (4-bit) |
| Parameters | ~360M |
| File size | ~248–258 MB |
| Runtime (ADTC) | llama.cpp |
| Runtime (app) | llama-cpp-python (`n_gpu_layers=0`) |
| Context (`n_ctx`) | 2048 in app |
| Threads | min(4, cpu_count) |

**Generation settings (app):**

| Setting | English | Kiswahili |
|---------|---------|-----------|
| temperature | 0.35 | 0.25 |
| top_p | 0.9 | 0.9 |
| max_tokens (chat) | 220 | 220 |

---

## 7. Disease classes and mapping

| Model output label | `class_key` | English UI | Kiswahili UI |
|--------------------|-------------|------------|--------------|
| healthy leaves | `healthy_leaves` | healthy leaves | Majani yenye afya |
| Leaf rust | `leaf_rust` | Leaf rust | Ukungu wa Majani |
| Phoma | `phoma` | Phoma | Phoma |

**Scientific context (for Q&A):**

- **Leaf rust:** *Hemileia vastatrix* — orange-yellow powder on leaf undersides.
- **Phoma:** Phoma leaf spot — dark lesions, yellow halos, premature leaf drop.
- **Healthy:** no actionable disease; prevention/monitoring advice.

---

## 8. API reference

### 8.1 Public / semi-public

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/predict` | POST | No* | Classify image (`file` multipart) |

\*Home UI requires login; endpoint itself does not check session (can be called via curl).

**`/predict` response:**

```json
{
  "class_key": "leaf_rust",
  "class": "Leaf rust",
  "confidence": 0.95,
  "saved_path": "classified_images/Leaf_rust/Leaf_rust_123.jpg",
  "llm_available": true
}
```

### 8.2 Session-authenticated APIs

| Endpoint | Method | Body | Response |
|----------|--------|------|----------|
| `/api/llm-status` | GET | — | `{ "available": true, "model": "..." }` |
| `/api/advisory` | POST | `{ "class_key", "confidence" }` optional | `{ "advisory": "<html>", "source": "curated\|static", "class_key" }` |
| `/api/chat` | POST | `{ "message": "..." }` | `{ "reply": "...", "source": "llm\|static" }` |
| `/api/chat/clear` | POST | — | `{ "ok": true }` |

### 8.3 Web pages

| Route | Purpose |
|-------|---------|
| `/` | Home — classifier + chat (`test.html`) |
| `/login`, `/register` | User accounts |
| `/about`, `/team`, `/contact` | Info pages |
| `/set-language/<en\|sw>` | Switch UI language |
| `/logout` | Clear session |

---

## 9. Session state

| Session key | Content |
|-------------|---------|
| `user` | Logged-in username |
| `lang` | `en` or `sw` |
| `last_classification` | `{ class_key, class, confidence }` |
| `chat_history` | Up to 20 messages `[{ role, content }]` |

Chat uses last **8** messages as LLM context; advisory uses classification from session if body omits `class_key`.

---

## 10. Internationalization (i18n)

- **Module:** `app/i18n.py`
- **Locales:** `app/locales/en.json`, `app/locales/sw.json`
- **Sections:** `strings` (UI), `class_labels`, `advisories` (HTML countermeasures)
- **No cloud translation API** — all strings local.

**Kiswahili chat strategy:**

1. Primary path: GGUF conversational reply (same as English).
2. If output is garbled or echoing → retry with a simpler Kiswahili prompt (`_kiswahili_chat_fallback`).
3. Structured locale advisories are **only** used for **Get AI Advisory**, not chat.

SmolLM2-360M is **weak in Kiswahili**; the quality retry improves chat without dumping the full Symptoms/Countermeasures template into the chat panel.

---

## 11. LLM module — `app/llm_advisor.py`

| Function | Purpose |
|----------|---------|
| `gguf_available()` | Check GGUF file exists |
| `llm_status()` | Availability for UI/API |
| `generate_advisory()` | Post-classification structured advisory (locale HTML only) |
| `generate_chat_reply()` | Conversational Q&A (GGUF) |
| `translate_chat_content()` | Translate chat bubbles on language switch |
| `localize_chat_history()` | Display history in selected language |
| `_infer_class_from_message()` | Keyword → `class_key` for chat context hints |
| `_kiswahili_reply_poor()` | Heuristic quality gate for Kiswahili chat |
| `text_to_html()` | Sanitize LLM text for DOM |

**Lazy loading:** GGUF loads on first **chat** request (~10–30 s first time on CPU), then stays in memory. Advisories do not trigger GGUF load.

**Fallback chain (chat only):**

```
GGUF chat completion → (Kiswahili poor quality) → simpler Kiswahili retry
                    → (GGUF missing / error) → static unavailable message
```

---

## 12. Authentication and data

| Item | Detail |
|------|--------|
| Database | SQLite `app/users.db` |
| Table | `users(id, username, email, password)` |
| Passwords | Werkzeug `generate_password_hash` |
| Session | Flask cookie, `secret_key` in code |

**Stored locally:**

- User credentials (hashed)
- Uploaded/classified images in `app/classified_images/`
- No cloud upload of farmer images

**Security notes (honest for Q&A):**

- `secret_key` is hardcoded — acceptable for local demo, not production.
- No HTTPS by default — run behind reverse proxy for deployment.
- `/predict` lacks auth — intentional for API testing.

---

## 13. Repository structure

```
Coffee Leaf Disease Detector/
├── metadata.json              # ADTC submission metadata + test_prompts
├── download_model.ps1         # GGUF download (~248 MB)
├── download_classifier.ps1    # ONNX download (~29 MB)
├── run_profiler.ps1           # ADTC profiler (host or Docker)
├── REPORT.md                  # Judge technical report
├── ADTC_SUBMISSION.md         # Submission checklist
├── TECHNICAL_REFERENCE.md     # This document
├── submission.json            # Profiler output (host)
├── submission_constrained.json# Profiler output (7.5 GB Docker)
├── model/
│   ├── coffee_model.onnx
│   └── SmolLM2-360M-Instruct-Q4_K_M.gguf
└── app/
    ├── onnx_server.py         # Flask entry point
    ├── llm_advisor.py         # Locale advisories + GGUF chatbot
    ├── i18n.py
    ├── requirements.txt
    ├── users.db               # auto-created
    ├── classified_images/     # auto-created
    ├── locales/
    ├── templates/
    └── static/
```

**Entry point:** `cd app && python onnx_server.py` → http://localhost:5000

---

## 14. ADTC profiler (separate from Flask app)

The profiler does **not** run Flask. It reads `metadata.json`, loads the GGUF, and benchmarks via **standalone llama.cpp**.

```powershell
.\run_profiler.ps1 -Constrained   # Docker, 7.5 GB RAM cap (official profile)
.\run_profiler.ps1                # Host smoke test (faster TPS, not memory-limited)
```

### Participant laptop (development & profiling)

| Component | Specification |
|-----------|---------------|
| Model | HP EliteBook |
| CPU | Intel Core i5 @ 2.20 GHz |
| RAM | 8 GB |
| Storage | 500 GB |
| Graphics | Integrated |

Profiler auto-reports CPU as `i5-8350U @ 1.70 GHz` (base clock).

### Constrained profiler results (21 Jun 2026)

| Metric | Value |
|--------|-------|
| Tokens/sec (generation) | **2.82 TPS** |
| First-token latency | ~95 s (512-token prompt, cold) |
| Peak RSS | **375 MB** |
| Steady-state RSS | 319 MB |
| Container RAM limit | 7.5 GB — **no OOM** |
| CPU p99 | 65.2% |
| Thermal throttle | No |

### ADTC scoring (reference)

$$S_{\text{total}} = 0.50 \cdot S_{\text{acc}} + 0.30 \cdot S_{\text{perf}} + 0.20 \cdot S_{\text{eff}} - P_{\text{thermal}}$$

| Component | Weight | Our constrained run |
|-----------|--------|---------------------|
| S_perf | 30% | ~18.8% (2.82 / 15 TPS ref) |
| S_eff | 20% | ~94.6% (0.37 GB peak vs 7 GB budget) |
| S_acc | 50% | Judge panel + test prompts |

**Wiring GGUF into Flask did not change profiler workflow** — same GGUF file and `metadata.json`.

---

## 15. Performance summary

| Operation | Typical time (HP EliteBook, CPU) |
|-----------|----------------------------------|
| Server + ONNX load | 2–5 s |
| Image classification | 0.5–1 s |
| First GGUF load | 10–30 s (first chat only) |
| Get AI Advisory | Instant (locale JSON) |
| English chat reply (warm) | 3–15 s |
| Kiswahili chat reply (warm) | 3–20 s |

| Resource | Approximate |
|----------|-------------|
| ONNX model RAM | ~50–100 MB |
| GGUF model RAM | ~375 MB peak (profiler) |
| Full app RAM | ~500 MB–1 GB with both loaded |

---

## 16. Test prompts (ADTC / DevPost)

Defined in `metadata.json` (update DevPost to match):

**Prompt 1 (English):**
> My coffee leaves have orange-yellow powder on the underside and some leaves are falling off early. What disease is this and what should I do now so it doesn't spread to the rest of my farm?

**Prompt 2 (Kiswahili):**
> Mimi ni mkulima mdogo wa kahawa. Majani yangu yana doa nyeusi na yanakauka. Ni ugonjwa gani hii na nifanye nini haraka kabla haiharibu mazao yangu?

---

## 17. Known limitations (say these confidently)

1. **Three classes only** — not a general leaf detector; non-coffee images may misclassify.
2. **360M LLM** — small model; may hallucinate fungicide names in chat; Kiswahili chat uses quality retry, not structured locale dumps.
3. **CPU-only** — no GPU acceleration configured (`n_gpu_layers=0`).
4. **Single-user session chat** — history in Flask session, not a shared database.
5. **No model retraining pipeline** in repo — ONNX is a fixed exported model.
6. **Local demo security** — hardcoded secret key, no production hardening.

---

## 18. Anticipated technical Q&A

### “Why not one end-to-end model?”

CNNs excel at images; LLMs excel at text. Merging would require a large multimodal model that violates our RAM budget. Hybrid design keeps classification fast and advice flexible.

### “Why SmolLM2-360M and Q4_K_M?”

Fits 8 GB RAM (375 MB peak RSS), runs on CPU, supports instruct chat format, and meets ADTC GGUF + llama.cpp requirements.

### “How do you ensure offline operation?”

All models, locales, CSS, and SQLite are local. No CDN or external API calls during inference. Internet only needed once for `pip install` and model download.

### “How accurate is the classifier?”

Trained on three-class coffee leaf dataset (healthy, rust, Phoma). Report high confidence on clear test images; acknowledge limits on blurry/non-leaf photos. Exact accuracy metrics depend on your training evaluation (cite your training notebook/report if asked).

### “What if the GGUF is missing?”

Advisories fall back to static JSON. Chat returns an error message asking to install GGUF + llama-cpp-python. Classification still works (ONNX only).

### “Why does Kiswahili use static text sometimes?”

**Get AI Advisory** always uses expert-written locale HTML (EN/SW) for consistent Symptoms / Countermeasures. **Chat** uses the GGUF for natural replies; if Kiswahili output is garbled, we retry with a simpler prompt — we do not inject the full structured advisory into the chat panel.

### “Difference between profiler and app LLM path?”

| | Profiler | Flask app |
|---|----------|-----------|
| Runtime | llama.cpp CLI / Docker image | llama-cpp-python |
| Purpose | Benchmark TPS/RAM | Farmer chatbot (natural Q&A) |
| Same weights? | Yes — same `.gguf` file |

### “What is cross_disciplinary_pairing in metadata?”

ADTC field: agriculture domain is **load-bearing** — the solution is a real farming tool (disease ID + advisories), not a generic chatbot with agriculture branding.

### “How would you deploy to farmers?”

Options: local laptop in extension office, Raspberry Pi + ONNX only (lighter), or packaged executable. Current repo targets laptop demo. Would add HTTPS, proper secret management, and optional mobile wrapper for production.

### “What would you improve next?”

- Fine-tune SmolLM2 on agriculture Q&A (improve S_acc)
- Kiswahili fine-tune or dedicated Swahili small model
- Quantized ONNX or MobileNet for faster mobile inference
- Replace hardcoded secrets; add HTTPS
- Expand classes / dataset with Ugandan field samples

---

## 19. Quick command reference

```powershell
# Repo root
.\download_model.ps1
.\download_classifier.ps1
.\run_profiler.ps1 -Constrained

# App
cd app
pip install -r requirements.txt
python onnx_server.py

# Test classify (no login)
curl.exe -X POST -F "file=@classified_images\Leaf_rust\Leaf_rust_1782062509.jpg" http://localhost:5000/predict
```

---

## 20. Related documents

| Document | Purpose |
|----------|---------|
| `REPORT.md` | ADTC judge-facing technical report |
| `ADTC_SUBMISSION.md` | Submission checklist |
| `app/howtorun.md` | Setup and run instructions |
| `app/SYSTEM_REPORT.md` | Extended system documentation |
| `metadata.json` | Official ADTC metadata |

---

*Prepared for Joseph Walusimbi & Chelangat Specioza — CoffeeVision / ADTC 2026.*
