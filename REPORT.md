# ADTC 2026 — Coffee Leaf Disease Detector (Agriculture)

Technical report for the [Africa Deep Tech Challenge 2026](https://adtc-2026.devpost.com/) — **Agriculture** domain, [submission template](https://github.com/Africa-Deep-Tech-Foundation/adtc-2026-submission-template) layout.

**Team:** Joseph Walusimbi & Chelangat Specioza — Soroti University, Uganda  
**Repository:** [JosephWalusimbi-eng/Coffee-Leaf-Disease-Detector](https://github.com/JosephWalusimbi-eng/Coffee-Leaf-Disease-Detector)  
**Submission guide:** [`ADTC_SUBMISSION.md`](ADTC_SUBMISSION.md)

---

## Dual-model architecture (why not ONNX → GGUF conversion)

| Model | Format | Role | Runtime |
|-------|--------|------|---------|
| **Coffee leaf CNN** | ONNX (`coffee_model.onnx`) | Classify leaf images into 3 classes | ONNX Runtime |
| **Advisory LLM** | GGUF (`SmolLM2-360M-Instruct-Q4_K_M.gguf`) | English advisories, farmer chatbot, ADTC evaluation | llama.cpp |

**You cannot convert the ONNX classifier to GGUF.** GGUF + `llama.cpp` are for **language models** (text in → text out). Your classifier is a **CNN** (image in → 3 class scores). Different architecture, different runtime.

This matches other agriculture submissions (e.g. vision CNN + GGUF LLM for farmer advice). ADTC's [profiler](https://github.com/Africa-Deep-Tech-Foundation/adtc-profiler) benchmarks the **GGUF LLM**; the Flask app uses **ONNX** for leaf photos and **llama-cpp-python** for live advisories and chat.

### Downloads

```powershell
.\download_model.ps1        # GGUF LLM — required for ADTC metadata / profiler
.\download_classifier.ps1   # ONNX CNN — required for the web classifier
```

---

## 1. Problem definition and context

Coffee farmers in Uganda and East Africa lose yield when foliar diseases—especially **coffee leaf rust** and **Phoma**—spread before farmers recognize symptoms. Expert diagnosis is scarce in rural areas. Cloud LLMs are impractical due to API cost, unreliable connectivity, and power constraints—the same barriers described in the [ADTC 2026 challenge](https://adtc-2026.devpost.com/).

This system gives farmers and extension workers an **offline-capable** tool to photograph a leaf, classify disease type, receive **AI-generated advisories**, and ask follow-up questions through an **on-device chatbot** — all in **English or Kiswahili** on an **8 GB commodity laptop**.

**Target users:** Smallholder coffee farmers, agricultural students, and field extension agents in Uganda and East Africa.

---

## 2. Design Decisions

| Decision | Rationale |
|----------|-----------|
| **ONNX CNN classifier** | Fast CPU inference (~&lt;1 s), ~29 MB model fits 8 GB RAM laptops |
| **Three classes** | healthy leaves, Leaf rust, Phoma — aligned with local farmer needs |
| **224×224 RGB input** | Standard CNN input; resize + normalize in OpenCV |
| **ONNX Runtime** | Cross-platform, no GPU required, runs fully offline |
| **Flask web UI** | Familiar browser workflow; upload, webcam, chat panel |
| **GGUF + llama-cpp-python** | On-device English advisories and farmer chatbot |
| **Locale JSON files** | `locales/en.json`, `locales/sw.json` — UI + verified Kiswahili advisories |
| **Local CSS** | `app/static/css/app.css` — no CDN dependency |
| **Model in `model/`** | Matches ADTC download pattern; weights excluded from git |

**Alternatives considered:** Cloud APIs (rejected — connectivity); larger models (rejected — RAM budget); single-language UI (rejected — farmer accessibility).

---

## 3. Constraints (ADTC Standard Laptop alignment)

| Constraint | How we addressed it |
|------------|---------------------|
| **8 GB RAM** (ADTC profile) | ONNX classifier ~29 MB; GGUF LLM Q4_K_M ~248 MB; total app fits budget laptop |
| **Integrated GPU only** | CPU inference via ONNX Runtime + llama.cpp |
| **No cloud / connectivity** | All models, locales, and CSS local |
| **Power** | Low sustained CPU; no GPU draw |
| **Data** | Local image storage; no farmer data uploaded to cloud |
| **African context** | Ugandan coffee diseases; Kiswahili UI; Soroti University team |
| **Low technical literacy** | Simple upload/capture, one-button classification, chat panel |

### Participant laptop (development, profiling, and demos)

All local development, host profiler runs, and demo recordings were performed on:

| Component | Specification |
|-----------|---------------|
| **Model** | HP EliteBook |
| **CPU** | Intel Core i5, 2.20 GHz |
| **RAM** | 8 GB |
| **Storage** | 500 GB |
| **Graphics** | Integrated (no discrete GPU) |

This machine matches the ADTC **8 GB RAM** budget. Profiler host runs report `measured_on: participant_laptop` on this hardware.

### ADTC Standard Laptop (official challenge evaluation target)

Judges benchmark against this reference profile (our participant laptop aligns on RAM and integrated graphics):

| Component | Specification |
|-----------|---------------|
| CPU | Intel i5 10th–12th gen or AMD Ryzen 5 3000–5000 |
| RAM | 8 GB DDR4 |
| GPU | Integrated only |
| Storage | 256 GB SSD |
| OS | Ubuntu 22.04 LTS (reference) |

---

## 4. Tools used

| Tool | Why chosen |
|------|------------|
| **Flask** | Lightweight local web server for farmer UI |
| **ONNX Runtime** | Fast CPU inference for image CNN |
| **llama-cpp-python** | Live GGUF inference for English advisories and chatbot |
| **OpenCV + Pillow** | Image resize/normalize for classifier |
| **SQLite** | Local user accounts without cloud |
| **Locale JSON** | Offline UI + curated Kiswahili disease advisories |
| **adtc-profiler** | Pre-submission benchmark against ADTC pipeline |

---

## 5. Benchmarks (HP EliteBook participant laptop)

Profiler runs and app testing used an **HP EliteBook** — Intel Core i5 @ 2.20 GHz, **8 GB RAM**, **500 GB** storage, integrated graphics.

### ONNX classifier (leaf images)

| Metric | Value |
|--------|-------|
| Model file size | ~28.6 MB |
| Model load at startup | ~2–5 s |
| Single image inference | ~0.5–1 s |
| Peak RAM (app + ONNX) | ~500 MB–1 GB |
| Classes | healthy leaves, Leaf rust, Phoma |

### GGUF LLM (ADTC evaluation)

Benchmarked with [adtc-profiler](https://github.com/Africa-Deep-Tech-Foundation/adtc-profiler) v0.1.0 in **participant mode** (`--skip-accuracy`).

**Does more system RAM change the score?** No — ADTC scores **peak process memory (RSS)** during inference, not total installed RAM. A 360M Q4_K_M model uses ~375–394 MB peak RSS on our 8 GB HP EliteBook, well within the 7 GB budget.

**Constrained re-run (recommended):** Docker with `--memory=7.5g` enforces the ADTC RAM cap (OOM if the model exceeds it), uses CPU-only `llama.cpp` built without AVX (parity with commodity laptops), and runs on Linux inside the container.

```powershell
.\run_profiler.ps1 -Constrained   # 7.5 GB Docker cap — use for REPORT
.\run_profiler.ps1                # fast host check (optional)
```

Reports: [`submission_constrained.json`](submission_constrained.json) (constrained), [`submission.json`](submission.json) (host).

#### Constrained run — 21 June 2026 (Docker `memory=7.5g`, ADTC profiler image)

| Metric | Value | ADTC note |
|--------|-------|-----------|
| **Tokens/sec (generation)** | **2.82 TPS** | Conservative CPU-only build (no AVX); S_perf ≈ 18.8% vs 15 TPS ref |
| **First-token latency** | 94,963 ms | Same 512-token prompt; slower PP on generic CPU build |
| **Peak RSS** | **375 MB** (~0.37 GB) | **Passed 7.5 GB container limit** — fits 8 GB laptop |
| **Steady-state RSS** | 319 MB | |
| **CPU p99** | 65.2% | |
| **Thermal throttle** | No | |
| **Container RAM limit** | 7.5 GB enforced | No OOM — model is safe on ADTC profile |

| Environment field | Value |
|-------------------|-------|
| Host machine | HP EliteBook — Intel Core i5 @ 2.20 GHz, 8 GB RAM, 500 GB storage |
| CPU (profiler report) | Intel Core i5-8350U @ 1.70 GHz (base clock reported by adtc-profiler / Docker host) |
| RAM reported | 9.7 GB (Docker Desktop VM; **limit still enforced at 7.5 GB**) |
| OS | Debian GNU/Linux 13 (profiler image; reference audit OS: Ubuntu 22.04) |
| GPU | none (integrated) |

| Component | Formula | Constrained run |
|-----------|---------|-----------------|
| S_perf | `min(TPS ÷ 15, 1) × 100` | **~18.8** (2.82 TPS) |
| S_eff | `(7 − peak_gb) ÷ 7 × 100` | **~94.6** (0.37 GB peak) |
| P_thermal | −10 if throttled / >85°C | **0** |

#### Host run — 21 June 2026 (HP EliteBook, Windows — optional smoke test)

| Metric | Value |
|--------|-------|
| TPS | 17.44 (optimized win-cpu `llama-bench` with AVX) |
| Peak RSS | 394 MB |
| Host machine | HP EliteBook — Intel Core i5 @ 2.20 GHz, 8 GB RAM, 500 GB storage |
| OS | Windows 11 |

> **Why TPS differs:** The host run used optimized Windows binaries (AVX). The constrained Docker image builds `llama.cpp` with `GGML_AVX=OFF` to match low-end commodity laptops — throughput is lower but more representative of ADTC audit conditions. **Peak RAM is nearly identical** (~375 vs 394 MB), which is what matters for the 8 GB constraint.

| Scoring dimension | Weight | Our target |
|-------------------|--------|------------|
| S_acc (accuracy) | 50% | Strong agriculture + Kiswahili prompt answers |
| S_eff (RAM) | 20% | Stay well below 7 GB peak (**achieved: ~0.37 GB**) |
| S_perf (throughput) | 30% | Maximize TPS on 8 GB laptop |
| P_thermal | −10 if >85°C | Avoid throttling under load |

---

## 6. Repository layout

```
├── metadata.json              # ADTC metadata (GGUF path)
├── download_model.sh          # Downloads GGUF LLM
├── download_classifier.ps1    # Downloads ONNX classifier
├── run_profiler.ps1           # ADTC profiler self-check (Windows)
├── submission.json            # Profiler output (participant mode)
├── ADTC_SUBMISSION.md         # Full DevPost checklist
├── REPORT.md                  # This file
├── model/
│   ├── SmolLM2-360M-Instruct-Q4_K_M.gguf
│   └── coffee_model.onnx
└── app/                       # Flask web application
    ├── onnx_server.py
    ├── llm_advisor.py         # GGUF advisories + chatbot
    └── ...
```

---

## 7. Demo materials (for DevPost)

**Required by organizers:**

- [ ] Screenshots — login, classification, **chatbot**, Kiswahili UI, AI advisory  
- [ ] **Video (max 2 minutes)** — problem, demo, development journey  
- [ ] Upload to DevPost with public GitHub URL  

Suggested video outline:

1. Problem — coffee diseases in Uganda (15 s)  
2. Demo — upload leaf → classification → **AI advisory** → **chatbot follow-up** in English/Kiswahili (60 s)  
3. Technical — offline on HP EliteBook (8 GB RAM), dual model + chatbot (30 s)  
4. Team + Soroti University (15 s)  

---

## 8. Offline verification

After `pip install` and model downloads:

- No CDN or external API calls during classification, advisories, or chat
- Language switching uses local JSON dictionaries
- Styles served from `app/static/css/app.css`
- GGUF loaded on first advisory or chat request (then stays in memory)

---

## 9. Full system documentation

See `app/SYSTEM_REPORT.md` for architecture, APIs, chatbot, and PC specifications.  
See `TECHNICAL_REFERENCE.md` for Q&A preparation.

---

*Submit via [adtc-2026.devpost.com](https://adtc-2026.devpost.com/) before **August 26, 2026 @ 11:45pm PDT**. Replace `team_id` in `metadata.json`. See [`ADTC_SUBMISSION.md`](ADTC_SUBMISSION.md).*
