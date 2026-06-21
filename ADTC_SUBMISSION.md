# ADTC 2026 — Official Submission Guide

Complete checklist aligned with [Africa Deep Tech Challenge 2026 on Devpost](https://adtc-2026.devpost.com/) and the [submission template](https://github.com/Africa-Deep-Tech-Foundation/adtc-2026-submission-template).

**Project:** AI-based Coffee Leaf Disease Detector and Advisory System  
**Domain:** Agriculture  
**Team:** Joseph Walusimbi & Chelangat Specioza — Soroti University, Uganda  
**Repository:** [JosephWalusimbi-eng/Coffee-Leaf-Disease-Detector](https://github.com/JosephWalusimbi-eng/Coffee-Leaf-Disease-Detector)

---

## Deadline & registration

| Item | Detail |
|------|--------|
| **Submission deadline** | **August 26, 2026 @ 11:45pm PDT** |
| **Register** | [adtc-2026.devpost.com](https://adtc-2026.devpost.com/) |
| **Team size** | 1–3 people |
| **Eligibility** | Above legal age of majority; specific countries/territories (see Devpost rules) |

### Get started (from organizers)

1. Register on DevPost for ADTC 2026  
2. Form or join a team (1–3) and pick your **problem domain** → we use **Agriculture**  
3. Clone / fork the [submission template](https://github.com/Africa-Deep-Tech-Foundation/adtc-2026-submission-template) layout  
4. Test locally with the [adtc-profiler](https://github.com/Africa-Deep-Tech-Foundation/adtc-profiler)  
5. Apply for up to **5 hours of GPU credits** (Udutech) to train/fine-tune your model  
6. Read rules and submission requirements; build and submit  

---

## What to build

An **end-to-end, on-device language model** that runs **without cloud dependencies** on the **ADTC Standard Laptop**, addressing one published domain.

### Our domain: Agriculture

> Crop, livestock, weather, and market advisory for farmers and extension officers.

Our solution: **offline coffee leaf disease detection** (ONNX CNN) plus **structured farmer advisories** (curated EN/SW locales) and an **offline chatbot** (GGUF LLM for natural conversation), targeting Ugandan smallholders.

### Participant laptop (our hardware)

Development, profiling, and demos were run on:

| Component | Specification |
|-----------|---------------|
| **Model** | HP EliteBook |
| **CPU** | Intel Core i5, 2.20 GHz |
| **RAM** | **8 GB** |
| **Storage** | **500 GB** |
| **Graphics** | Integrated only (no discrete GPU) |

Host profiler output shows `measured_on: participant_laptop` from this machine.

### ADTC Standard Laptop (official evaluation hardware)

Judges benchmark against this reference profile:

| Component | Specification |
|-----------|---------------|
| **CPU** | Intel Core i5 10th–12th gen OR AMD Ryzen 5 3000–5000 (x86-64) |
| **RAM** | **8 GB DDR4** |
| **Graphics** | Integrated only (Intel UHD / Iris Xe or AMD Radeon). **No discrete GPU.** |
| **Storage** | 256 GB SSD |
| **OS (reference)** | Ubuntu 22.04 LTS |
| **Price band** | ~$400–500 new / $150–250 refurbished |

Design target: **7 GB RAM budget** for the LLM (profiler uses 7 GB as limit).

---

## What to submit (Devpost)

### 1. Public GitHub repository

- Uses the approved ADTC 2026 report template structure  
- **Public** at submission time  
- **Do not commit** model weights (`model/*.gguf`, `model/*.onnx` — see `.gitignore`)

### 2. Repository files (required)

| File | Status | Action |
|------|--------|--------|
| `metadata.json` | ⚠️ | `team_id` **pending** — ADTF has not issued team IDs yet; keep placeholder until assigned (see below) |
| `download_model.sh` | ✅ | Downloads GGUF for llama.cpp |
| `download_classifier.ps1` | ✅ | Downloads ONNX classifier (our app) |
| `REPORT.md` | ✅ | Technical writeup — keep updated |
| `model/SmolLM2-360M-Instruct-Q4_K_M.gguf` | Download | Via `download_model.sh` — not in git |

### 3. Comprehensive project report (`REPORT.md`)

Must include (per Devpost):

- [x] Problem definition and context  
- [x] Identified constraints (power, data, compute, connectivity)  
- [x] Design alternatives and final decisions  
- [x] Tools used and why  
- [x] Performance tests and benchmarks  
- [ ] Screenshots or short videos showing the build in action  
- [ ] **Demo video (max 2 minutes)** — solution + development journey  

### 4. DevPost submission fields

- **Project title** — AI-based Coffee Leaf Disease Detector and Advisory System  
- **Description** — summary + link to repo  
- **Video URL** — ≤ 2 minutes (YouTube/Vimeo/etc.)  
- **Screenshots** — login, classification, **chatbot panel**, Kiswahili UI, AI advisory  
- **GitHub repo URL** — public link  

### 5. Semi-final / final (if selected)

- Updated repo, documentation, and video  

---

## Leaderboard scoring (how judges score)

$$S_{\text{total}} = 0.50 \cdot S_{\text{acc}} + 0.30 \cdot S_{\text{perf}} + 0.20 \cdot S_{\text{eff}} - P_{\text{thermal}}$$

| Component | Weight | Meaning |
|-----------|--------|---------|
| **S_acc** | 50% | Accuracy/quality of model responses (benchmarks + judge panel) |
| **S_perf** | 30% | Throughput — tokens/sec vs reference (TPS_REFERENCE ≈ 15) |
| **S_eff** | 20% | RAM efficiency — lower peak RAM below 7 GB scores higher |
| **P_thermal** | −10 pts | If CPU throttles or temp > 85°C |

**Disqualification:** Out-of-memory (OOM) or sandbox crash during evaluation.

**African Use Case Bonus:** Up to extra points for strong African applicability (`african_alpha_claim: true` in `metadata.json`).

### Judging criteria (summary)

1. **Model accuracy & quality** — prompts + documentation  
2. **Throughput performance** — relative to max TPS observed  
3. **Efficiency** — RAM vs 7 GB budget  
4. **African use case bonus** — real African problem fit  
5. **Hardware & thermal penalties** — >85°C or throttling  

---

## Local testing (before submit)

### Download models

```powershell
.\download_model.ps1        # GGUF LLM — ADTC evaluation
.\download_classifier.ps1   # ONNX — web classifier
```

### Run adtc-profiler

**ADTC Standard Laptop profile (7.5 GB RAM cap):**

```powershell
.\run_profiler.ps1 -Constrained
```

Uses Docker (`--memory=7.5g`) + official profiler image (CPU-only `llama.cpp`). Requires Docker Desktop.

**Fast host smoke test (not memory-limited):**

```powershell
.\run_profiler.ps1
```

**Latest constrained run (21 Jun 2026):** [`submission_constrained.json`](submission_constrained.json) — see [`REPORT.md`](REPORT.md) §5.

| Metric | Constrained (7.5 GB Docker) | Host (HP EliteBook, 8 GB RAM) |
|--------|----------------------------|--------------------------|
| TPS | 2.82 | 17.44 |
| Peak RSS | 375 MB | 394 MB |
| Fits 8 GB? | Yes (no OOM) | Yes (RSS only ~0.4 GB) |
| Throttled | No | No |

Valid run shows `"measured_on": "participant_laptop"`.

Profiler source: [Africa-Deep-Tech-Foundation/adtc-profiler](https://github.com/Africa-Deep-Tech-Foundation/adtc-profiler)

### Run full web app

```powershell
cd app
pip install -r requirements.txt
python onnx_server.py
```

Open http://localhost:5000

---

## Dual-model architecture (important)

| Model | File | ADTC profiler | Our app |
|-------|------|---------------|---------|
| **LLM (GGUF)** | `model/SmolLM2-360M-Instruct-Q4_K_M.gguf` | ✅ Evaluated | Offline farmer chatbot (natural Q&A) |
| **Locales** | `app/locales/en.json`, `sw.json` | Not evaluated | Structured post-classification advisories (EN/SW) |
| **CNN (ONNX)** | `model/coffee_model.onnx` | Not evaluated | Leaf photo classification |

The ONNX CNN **cannot** be converted to GGUF. ADTC requires **llama.cpp + GGUF** for scoring; our vision classifier stays ONNX.

---

## Prizes (overview)

| Prize | Amount |
|-------|--------|
| Grand Prize | $8,000 |
| Second Place | $4,000 |
| 3rd Place | $3,000 |
| Best African Use Case | $1,500 |
| Finalist stipends | GPU credits ($250 × up to 10) |
| Semifinalist stipends | GPU credits ($50 × up to 20) |

Total pool **$16,500+** — see [Devpost prizes](https://adtc-2026.devpost.com/).

---

## Team ID (`metadata.json`)

**Status:** ADTF/ADTC has **not yet issued** official `team_id` values to participants. Our `metadata.json` still uses the template placeholder:

```json
"team_id": "REPLACE_WITH_YOUR_ADTF_TEAM_ID"
```

This is **expected** until organizers publish IDs. Local profiler runs and development work fine with the placeholder.

**When you receive your team ID** (typically after Devpost registration confirmation or an email from ADTC organizers):

1. Replace `team_id` in `metadata.json`.
2. Re-run the profiler if you want submission JSON files to match: `.\run_profiler.ps1` or `.\run_profiler.ps1 -Constrained`.
3. Commit and push before the final Devpost deadline.

**If you still have no ID near the deadline:** contact ADTC via Devpost discussion / organizer email and ask for your assigned `team_id`. Do not invent a custom ID — judges may flag mismatched IDs during evaluation.

**Until then:** complete everything else on the checklist (repo, `REPORT.md`, profiler metrics, demo video, screenshots). Only the `team_id` field is blocked.

---

## Pre-submission checklist

### Registration & team

- [ ] Registered on [Devpost](https://adtc-2026.devpost.com/)
- [ ] Team formed (1–3 members) on Devpost
- [ ] Domain set to **Agriculture**

### Repository

- [ ] Repo is **public**
- [ ] `metadata.json` — real `team_id` from ADTF (**pending** — not issued yet; update when received)
- [ ] `metadata.json` — exactly **2 test prompts**
- [ ] `metadata.json` — `runtime: llama.cpp`, GGUF path correct
- [ ] `bash download_model.sh` works on clean clone
- [ ] `model/*.gguf` and `model/*.onnx` **not** in git
- [ ] `REPORT.md` complete

### Technical

- [x] `adtc-profiler` smoke test passes (see `submission.json`)
- [ ] Model runs **100% offline** during inference (no API calls)
- [x] Fits **8 GB RAM** laptop profile (394 MB peak RSS in profiler run)
- [x] Record profiler metrics for `REPORT.md` (TPS, peak RAM)

### DevPost deliverables

- [ ] GitHub URL submitted
- [ ] Screenshots uploaded
- [ ] **Demo video** (≤ 2 min) uploaded
- [ ] Project description written

### Optional

- [ ] Apply for Udutech GPU credits (training/fine-tuning)
- [ ] Fine-tune SmolLM2 on agriculture / Kiswahili corpus for better S_acc

---

## Support & links

| Resource | URL |
|----------|-----|
| DevPost challenge | https://adtc-2026.devpost.com/ |
| Submission template | https://github.com/Africa-Deep-Tech-Foundation/adtc-2026-submission-template |
| Profiler | https://github.com/Africa-Deep-Tech-Foundation/adtc-profiler |
| Rules | DevPost → Rules tab |
| Email | challenge@africadeeptech.org |

---

## Contact

- **Joseph Walusimbi** — mrjosephwalusimbi@gmail.com · +256 764 123306  
- **Chelangat Specioza** — speciozachelangat@gmail.com · +256 742 353064  

Soroti University, Uganda
