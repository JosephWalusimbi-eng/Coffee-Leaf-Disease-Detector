# CoffeeVision — ADTC 2026 Submission

**CoffeeVision: AI-based Coffee leaf disease detector and Advisory system**

Offline bilingual (English / Kiswahili) web app for **coffee leaf disease detection**, **AI farmer advisories**, and an **offline agriculture chatbot**.

| Capability | Technology |
|------------|------------|
| **Leaf classification** | ONNX CNN — healthy leaves, Leaf rust, Phoma |
| **AI advisories** | GGUF LLM (English) + curated Kiswahili content |
| **Farmer chatbot** | On-device chat — follow-up questions about diseases, treatment, and farming |

Developed by **Joseph Walusimbi** and **Chelangat Specioza**, Electronics & Computer Engineers, Soroti University, Uganda.

Developed and benchmarked on an **HP EliteBook** (Intel Core i5 @ 2.20 GHz, 8 GB RAM, 500 GB storage).

This repository follows the [ADTC 2026 submission template](https://github.com/Africa-Deep-Tech-Foundation/adtc-2026-submission-template) for the **agriculture** domain on the [Laptop LLM Challenge](https://adtc-2026.devpost.com/).

**Full submission guide:** [`ADTC_SUBMISSION.md`](ADTC_SUBMISSION.md)  
**Technical Q&A reference:** [`TECHNICAL_REFERENCE.md`](TECHNICAL_REFERENCE.md)

**Deadline:** August 26, 2026 @ 11:45pm PDT

---

## Quick start

### 1. Download models (from repo root)

```powershell
.\download_model.ps1        # GGUF LLM (~248 MB) — advisories, chat, ADTC profiler
.\download_classifier.ps1   # ONNX classifier (~29 MB) — leaf images
```

### 2. Install and run

```powershell
cd app
pip install -r requirements.txt
python onnx_server.py
```

Open **http://localhost:5000**

### 3. Use CoffeeVision

1. Register / log in (English or Kiswahili)
2. Upload or capture a coffee leaf photo → **Classify**
3. Click **Get AI Advisory** for disease-specific guidance
4. Use **Ask CoffeeVision** chat for follow-up questions (same offline stack)

See [`app/howtorun.md`](app/howtorun.md) for full instructions.

---

## Repository structure

```
├── metadata.json
├── TECHNICAL_REFERENCE.md   # Q&A prep — architecture, APIs, chatbot
├── download_model.ps1 / download_classifier.ps1
├── REPORT.md
├── ADTC_SUBMISSION.md
├── model/                     # weights downloaded — not in git
│   ├── coffee_model.onnx
│   └── SmolLM2-360M-Instruct-Q4_K_M.gguf
└── app/                       # Flask web application (CoffeeVision)
    ├── onnx_server.py         # Main server
    ├── llm_advisor.py         # GGUF advisories + chatbot
    └── ...
```

---

## License

See `LICENSE` in this repository.
