# CoffeeVision — ADTC 2026 Submission

**CoffeeVision: AI-based Coffee leaf disease detector and Advisory system**

Offline bilingual (English / Kiswahili) web app for classifying coffee leaf diseases: **healthy leaves**, **Leaf rust**, and **Phoma**.

Developed by **Joseph Walusimbi** and **Chelangat Specioza**, Electronics & Computer Engineers, Soroti University, Uganda.

This repository follows the [ADTC 2026 submission template](https://github.com/Africa-Deep-Tech-Foundation/adtc-2026-submission-template) for the **agriculture** domain on the [Laptop LLM Challenge](https://adtc-2026.devpost.com/).

**Full submission guide:** [`ADTC_SUBMISSION.md`](ADTC_SUBMISSION.md)

**Deadline:** August 26, 2026 @ 11:45pm PDT

---

## Quick start

### 1. Download models (from repo root)

```powershell
.\download_model.ps1        # GGUF LLM (~248 MB) — ADTC / llama.cpp
.\download_classifier.ps1   # ONNX classifier (~29 MB) — leaf images
```

### 2. Install and run

```powershell
cd app
pip install -r requirements.txt
python onnx_server.py
```

Open **http://localhost:5000**

See [`app/howtorun.md`](app/howtorun.md) for full instructions.

---

## Repository structure

```
├── metadata.json
├── download_model.sh / download_classifier.ps1
├── REPORT.md
├── ADTC_SUBMISSION.md
├── model/          # weights downloaded — not in git
└── app/            # Flask web application (CoffeeVision)
```

---

## License

See `LICENSE` in this repository.
