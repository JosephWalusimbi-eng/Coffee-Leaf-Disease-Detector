# System Report — AI-Based Coffee Leaf Disease Detector and Advisory System

**Document version:** 3.0  
**Date:** June 2026  
**Project folder:** `Coffee Leaf Disease Detector` (repo root)  
**Application:** `app/`  
**Developers:** Joseph Walusimbi & Chelangat Specioza — Electronics & Computer Engineers, Soroti University, Uganda

---

## 1. Executive Summary

This system is a **local, offline-capable web application** that helps coffee farmers and agricultural workers **detect and classify coffee leaf diseases** from photographs, receive **AI-generated farmer advisories**, and ask follow-up questions through an **on-device agriculture chatbot**.

Users upload or capture an image of a coffee leaf; a trained **deep learning model** (exported as ONNX) predicts whether the leaf is **healthy**, affected by **Leaf Rust**, or affected by **Phoma**. The app then offers **Get AI Advisory** (GGUF LLM in English; curated Kiswahili text) and **Ask CoffeeVision** — a chat panel for ongoing questions about diseases, treatment, and farming.

The solution runs on a **personal computer** using **Flask**, **ONNX Runtime** for image inference, **llama-cpp-python** for the language model, and a **browser-based** interface. After initial setup, the system operates **without internet**: models, translations, styles, and chat all run locally.

**Key capabilities (v3.0):**

- **Three-class leaf classification** with confidence scoring (ONNX)
- **AI farmer advisories** after classification (GGUF LLM + Kiswahili locales)
- **Offline agriculture chatbot** with session history (GGUF + curated Kiswahili fallbacks)
- Bilingual UI: **English** and **Kiswahili**
- Language selection at login; switch anytime while logged in
- Team, About, and Contact informational pages
- Fully local styling (no CDN dependencies)

---

## 2. System Purpose and Scope

### 2.1 Problem Addressed

Coffee production in Uganda and similar regions is threatened by foliar diseases such as **coffee leaf rust** (*Hemileia vastatrix*) and **Phoma**-related leaf spot diseases. Early visual identification is difficult for non-experts. This system automates image-based classification to support faster decision-making in the field or at a demonstration workstation.

### 2.2 In Scope

- User registration and login with language preference
- **English / Kiswahili** interface and disease advisories
- Image upload and webcam capture
- Three-class leaf classification with confidence scoring
- **AI-generated advisories** after classification (`/api/advisory`)
- **Offline farmer chatbot** for follow-up Q&A (`/api/chat`, `/api/chat/clear`)
- Disease advisory text in selected language (LLM + curated locales)
- Informational pages: **Home**, **About Us**, **Team**, **Contact Us**
- Local storage of uploaded and classified images
- REST APIs: `POST /predict`, `/api/advisory`, `/api/chat`, `/api/llm-status`
- **Offline operation** after setup (no runtime internet required)

### 2.3 Out of Scope (Current Version)

- Real-time video/stream classification
- GPS mapping of diseased plants
- Additional languages beyond English and Kiswahili
- Mobile native app (runs in browser only)
- Automated email from contact form
- GPU-accelerated inference (not configured by default)
- Production-grade deployment (HTTPS, WAF, rate limiting)

---

## 3. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     User (Web Browser)                          │
│  Classifier panel + Ask CoffeeVision chatbot (test.html)        │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP (port 5000)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Flask Web Server (onnx_server.py)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ Auth + i18n  │  │ Page routes  │  │ POST /predict          │ │
│  └──────┬───────┘  └──────────────┘  │ /api/advisory          │ │
│         │                            │ /api/chat              │ │
│         ▼                            └───────────┬────────────┘ │
│  ┌──────────────┐  ┌──────────────┐              │             │
│  │ SQLite       │  │ i18n.py      │              ▼             │
│  │ users.db     │  │ locales/*.json│  ┌────────────────────────┐ │
│  └──────────────┘  └──────────────┘  │ Image → ONNX Runtime   │ │
│                                        │ coffee_model.onnx      │ │
│                                        └────────────────────────┘ │
│                                                    │             │
│                                                    ▼             │
│                              ┌─────────────────────────────────┐ │
│                              │ llm_advisor.py                  │ │
│                              │ SmolLM2-360M GGUF (llama.cpp)   │ │
│                              │ advisories + chatbot            │ │
│                              └─────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  model/*.onnx, model/*.gguf, classified_images/, locales/       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Technology Stack

| Layer | Technology | Role |
|-------|------------|------|
| **Runtime** | Python 3.10+ | Application language |
| **Web framework** | Flask 3.x | HTTP server, routing, sessions |
| **CORS** | flask-cors | Cross-origin API access |
| **Internationalization** | `i18n.py` + `locales/*.json` | English/Kiswahili dictionaries |
| **ML inference (vision)** | ONNX Runtime 1.16+ | Load and run `coffee_model.onnx` |
| **ML inference (language)** | llama-cpp-python | GGUF advisories and chatbot |
| **LLM module** | `llm_advisor.py` | Prompting, fallbacks, Kiswahili routing |
| **Image processing** | OpenCV, Pillow, NumPy | Resize, normalize, save images |
| **Database** | SQLite (`users.db`) | User accounts |
| **Frontend** | HTML5, JavaScript, local CSS | UI and client logic |
| **Security** | Werkzeug password hashing | Stored password protection |
| **Model format** | ONNX | Portable trained neural network |

### 4.1 Dependencies (`requirements.txt`)

```
flask>=3.1.0
flask-cors>=6.0.0
opencv-python>=4.8.0
numpy>=1.24.0
onnxruntime>=1.16.0
pillow>=10.0.0
llama-cpp-python>=0.2.90
```

### 4.2 Project Structure

```
Coffee Leaf Disease Detector/          # Repo root
├── metadata.json
├── model/
│   ├── coffee_model.onnx
│   └── SmolLM2-360M-Instruct-Q4_K_M.gguf
└── app/                               # Run server from here
    ├── onnx_server.py
    ├── llm_advisor.py
    ├── i18n.py
    ├── locales/
    ├── templates/                     # test.html = classifier + chatbot
    ├── static/
    ├── requirements.txt
    └── howtorun.md
```

---

## 5. How the Application Works (Detailed)

### 5.1 Startup Sequence

1. Run `python onnx_server.py` from the **`app/`** folder.
2. Flask loads `../model/coffee_model.onnx` into an ONNX Runtime `InferenceSession`.
3. GGUF model loads lazily on first advisory or chat request (`llm_advisor.py`).
4. `init_db()` creates `users.db` if missing.
5. Server listens on `0.0.0.0:5000`.

**Critical:** Run from **`app/`** so paths resolve correctly. Models live in `../model/`.

### 5.2 Authentication Flow

| Step | Action |
|------|--------|
| 1 | User visits `/` → redirected to `/login` if not authenticated |
| 2 | User selects **English** or **Kiswahili** on login/register |
| 3 | User registers at `/register` → username + hashed password in SQLite |
| 4 | User logs in → `session["user"]` and `session["lang"]` set |
| 5 | Protected pages check session before rendering |
| 6 | `/logout` clears user session (language may persist in session) |

Passwords are hashed with Werkzeug. Plain-text passwords are not stored.

### 5.3 Internationalization (i18n)

| Component | Description |
|-----------|-------------|
| **Locale files** | `locales/en.json`, `locales/sw.json` |
| **Loader** | `i18n.py` reads JSON at runtime |
| **Session key** | `session["lang"]` → `en` or `sw` |
| **Switch route** | `/set-language/<lang>?next=<path>` |
| **Login/register** | `<select name="lang">` sets language on submit |
| **Navbar** | English \| Kiswahili links on all authenticated pages |

Each locale JSON file contains:

| Section | Purpose |
|---------|---------|
| `strings` | UI labels, menus, buttons, page text, errors |
| `class_labels` | Translated disease names for inference results |
| `advisories` | HTML countermeasure content per disease class |

**Offline:** All translation data is local. No cloud translation API is used.

### 5.4 Image Classification Flow

```
User selects image or captures from webcam
        │
        ▼
Browser previews image (client-side)
        │
        ▼
User clicks "Classify Image" / "Tambua Majani"
        │
        ▼
JavaScript POSTs image to /predict (same origin)
        │
        ▼
Server saves → classified_images/uploaded_<timestamp>.jpg
        │
        ▼
PIL → NumPy → OpenCV resize 224×224 → normalize ÷255
        │
        ▼
ONNX Runtime inference → 3-class output vector
        │
        ▼
argmax (class index) + max (confidence)
        │
        ▼
Map to class_key → translate label; store session[last_classification]
        │
        ▼
Save copy to classified_images/<class>/<class>_<timestamp>.jpg
        │
        ▼
JSON: { class_key, class, confidence, saved_path, llm_available }
        │
        ▼
Browser shows translated class + confidence %
        │
        ▼
User clicks "Get AI Advisory" → POST /api/advisory → GGUF or curated text
        │
        ▼
User asks questions in chat panel → POST /api/chat (session history, up to 20 msgs)
```

### 5.5 Webcam Capture

The Home page uses `navigator.mediaDevices.getUserMedia()`. After ~2 seconds, a frame is captured to a `<canvas>` and used for classification. Requires camera permission in the browser.

### 5.6 AI Advisory System (`/api/advisory`)

After classification, the user clicks **Get AI Advisory** / **Pata Ushauri wa AI**.

| Language | Source | Behaviour |
|----------|--------|-----------|
| **English** | GGUF LLM (`llm_advisor.generate_advisory`) | Dynamic advisory from classification result |
| **Kiswahili** | Curated `locales/sw.json` | Verified farmer text (360M model unreliable in Kiswahili) |
| **Fallback** | `locales/*.json` | If GGUF missing or LLM errors |

Response includes `source`: `llm`, `curated`, or `static`.

### 5.7 Offline Chatbot (`/api/chat`)

The **Ask CoffeeVision** panel on the home page provides a farmer chatbot:

| Feature | Detail |
|---------|--------|
| Endpoint | `POST /api/chat` with `{ "message": "..." }` |
| History | Up to 20 messages in `session['chat_history']`; last 8 used as LLM context |
| Clear | `POST /api/chat/clear` resets history |
| Classification context | Last scan injected into English LLM system prompt |
| **English** | GGUF generates replies (~150 words max) |
| **Kiswahili** | Disease-keyword messages → curated advisories; general queries → LLM with quality fallback |

Chat and advisories share the same GGUF file; first request loads the model (~10–30 s on CPU).

### 5.8 Curated locale advisories

Pre-written HTML in `locales/en.json` and `locales/sw.json` under `advisories`:

| Class key | English label | Kiswahili label (example) |
|-----------|---------------|---------------------------|
| `healthy_leaves` | healthy leaves | Majani yenye afya |
| `leaf_rust` | Leaf rust | Ukungu wa Majani (Leaf Rust) |
| `phoma` | Phoma | Phoma |

---

## 6. Machine Learning Model

### 6.1 Model File

| Property | Value |
|----------|-------|
| **File** | `../model/coffee_model.onnx` (from `app/`) |
| **Location** | `model/` at repo root |
| **Size** | ~28.6 MB |
| **Format** | ONNX |
| **Runtime** | ONNX Runtime (CPU by default) |

### 6.2 Model I/O Specification

| | Name | Shape | Type |
|---|------|-------|------|
| **Input** | `args_0` | `[batch, 224, 224, 3]` | `float32` |
| **Output** | `dense_1` | `[batch, 3]` | `float32` |

- **Input:** RGB image, 224×224, pixel values 0.0–1.0.
- **Output:** Three class scores; server uses `np.argmax` and `np.max`.

### 6.3 Classification Classes

| Index | Internal key | Model label | Image folder |
|-------|--------------|-------------|--------------|
| 0 | `healthy_leaves` | healthy leaves | `healthy_leaves` |
| 1 | `leaf_rust` | Leaf rust | `Leaf_rust` |
| 2 | `phoma` | Phoma | `Phoma` |

### 6.4 Accuracy Notes

Sample tests showed high confidence on known images (e.g. ~99% Leaf rust, ~100% healthy). **Field accuracy** depends on image quality, lighting, and training-data similarity. Validate on local samples before commercial use.

---

## 7. Application Pages and Routes

| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/` | GET | Yes | Home — classifier + **Ask CoffeeVision** chatbot |
| `/login` | GET, POST | No | Login with language selection |
| `/register` | GET, POST | No | Account creation with language selection |
| `/about` | GET | Yes | Project overview |
| `/team` | GET | Yes | Developer profiles (Joseph Walusimbi, Chelangat Specioza) |
| `/contact` | GET | Yes | Email and telephone contact details |
| `/logout` | GET | Yes | End session |
| `/set-language/<lang>` | GET | No | Set `en` or `sw`; redirect to `next` URL |
| `/predict` | POST | **No** | Image classification API |
| `/api/llm-status` | GET | Yes | GGUF / llama-cpp availability |
| `/api/advisory` | POST | Yes | AI farmer advisory (JSON body optional) |
| `/api/chat` | POST | Yes | Chatbot message |
| `/api/chat/clear` | POST | Yes | Clear chat history |

### 7.1 Login Page

Displays the system title:

**AI-based Coffee leaf disease detector and Advisory system**

(Kiswahili: *Mfumo wa Utambuzi wa Magonjwa ya Majani ya Kahawa na Ushauri unaotumia AI*)

### 7.2 Team Page

Profiles for:

| Name | Role | Institution |
|------|------|-------------|
| Joseph Walusimbi | Electronics & Computer Engineer | Soroti University, Uganda |
| Chelangat Specioza | Electronics & Computer Engineer | Soroti University, Uganda |

### 7.3 Contact Page

Static contact information (no email form):

- Email: mrjosephwalusimbi@gmail.com
- Tel: +256764123306

---

## 8. Data Storage

### 8.1 User Database (`users.db`)

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER | Primary key |
| `username` | TEXT | Unique |
| `email` | TEXT | Unique (column exists; not set on registration) |
| `password` | TEXT | Hashed |

### 8.2 Classified Images (`classified_images/`)

Each prediction creates:

1. `uploaded_<timestamp>.jpg` — original upload
2. `<class>/<class>_<timestamp>.jpg` — sorted copy by model label

### 8.3 Locale Files (`locales/`)

Human-editable JSON dictionaries for translators. Edit `sw.json` to update Kiswahili text without changing Python code.

---

## 9. API Reference

### `POST /predict`

**Request:** `multipart/form-data` with field `file` (image).

Uses `session["lang"]` for translated class label. Does **not** return advisory text (use `/api/advisory`).

**Success response (200):**

```json
{
  "class_key": "leaf_rust",
  "class": "Ukungu wa Majani (Leaf Rust)",
  "confidence": 0.9999,
  "saved_path": "classified_images/Leaf_rust/Leaf_rust_1710000000.jpg",
  "llm_available": true
}
```

### `POST /api/advisory` (auth required)

**Body (optional):** `{ "class_key": "leaf_rust", "confidence": 0.99 }` — defaults to `session['last_classification']`.

**Response:** `{ "advisory": "<html>", "source": "llm|curated|static", "class_key": "..." }`

### `POST /api/chat` (auth required)

**Body:** `{ "message": "How do I treat leaf rust?" }`

**Response:** `{ "reply": "...", "source": "llm|static" }`

### `GET /api/llm-status` (auth required)

Returns `{ "available": true, "model": "SmolLM2-360M-Instruct-Q4_K_M.gguf" }` or error reason.

### `POST /api/chat/clear` (auth required)

Clears `session['chat_history']`. Returns `{ "ok": true }`.

**Error responses:**

| Status | Condition |
|--------|-----------|
| 400 | No file in request |
| 500 | Processing or model error |

**Note:** Endpoint does not require login. Consider authentication for production.

### `GET /set-language/<lang>`

| Parameter | Values | Description |
|-----------|--------|-------------|
| `lang` | `en`, `sw` | Language code |
| `next` (query) | URL path | Redirect target after switch |

---

## 10. Offline Operation

| Component | Offline? | Location |
|-----------|----------|----------|
| Web UI text | Yes | `locales/en.json`, `locales/sw.json` |
| Language switching | Yes | Flask session + local JSON |
| Inference labels & advisories | Yes | `locales/*.json` + GGUF |
| Chatbot | Yes | `llm_advisor.py` + GGUF |
| Styles / layout | Yes | `static/css/app.css` |
| Images & backgrounds | Yes | `static/images/` |
| ML models | Yes | `model/coffee_model.onnx`, `model/*.gguf` |
| User accounts | Yes | `users.db` |

**Internet required only for:** initial `pip install -r requirements.txt`.

The application does **not** use external CDNs, cloud APIs, or online translation services at runtime.

---

## 11. PC Specifications and Performance

### 11.1 Minimum Requirements

| Component | Specification |
|-----------|---------------|
| **OS** | Windows 10/11, macOS 10.15+, or Linux (64-bit) |
| **CPU** | Dual-core x64, 1.6 GHz+ |
| **RAM** | 4 GB |
| **Storage** | 2 GB free |
| **Network** | Not required after install |
| **Python** | 3.10+ |

Inference: ~1–3 seconds per image.

### 11.2 Recommended Requirements (participant laptop)

Validated on the team's **HP EliteBook** used for development and ADTC profiler runs:

| Component | Specification |
|-----------|---------------|
| **Model** | HP EliteBook |
| **OS** | Windows 10/11 64-bit |
| **CPU** | Intel Core i5, 2.20 GHz |
| **RAM** | 8 GB |
| **Storage** | 500 GB (≥ 5 GB free for models and dependencies) |
| **Browser** | Chrome or Edge (latest) |

Model load: ~2–5 s ONNX at startup; GGUF ~10–30 s on first advisory/chat; inference typically **under 1 second** per image on CPU.

### 11.3 Optimal / Lab Station

| Component | Specification |
|-----------|---------------|
| **CPU** | 6+ cores |
| **RAM** | 16 GB |
| **Storage** | SSD, 10+ GB free |
| **GPU** | Optional (`onnxruntime-gpu` not configured by default) |

### 11.4 Concurrent Users

Flask development server (`debug=True`) suits **single-user or small demo** use. For multiple users, deploy with Gunicorn/waitress behind a reverse proxy.

---

## 11. Software Installation

```powershell
cd "Coffee Leaf Disease Detector"
.\download_model.ps1
cd app
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python onnx_server.py
```

Open: **http://localhost:5000**

See `howtorun.md` for detailed setup and troubleshooting.

---

## 13. Security Considerations

| Topic | Current state | Production recommendation |
|-------|---------------|---------------------------|
| Session secret | Hardcoded `supersecretkey` | Environment variable |
| `/predict` auth | Open | Login or API token |
| Password storage | Hashed | Password policy |
| HTTPS | Not enabled | TLS certificate |
| Debug mode | `debug=True` | Disable in production |
| File uploads | No size/MIME validation | Add validation |
| SQL injection | Parameterized queries | Keep parameterized queries |

---

## 14. Limitations and Known Issues

1. **Working directory** — Server must run from **`app/`** folder.
2. **Three classes only** — No other diseases or non-leaf rejection class in the model.
3. **Confidence score** — Raw model output max value; not necessarily calibrated probability.
4. **LAN exposure** — `0.0.0.0:5000` reachable on local network; configure firewall if needed.
5. **Image quality** — Blurry, shaded, or multi-leaf photos may reduce accuracy.
6. **Two languages only** — English and Kiswahili; additional languages require new locale JSON files.
7. **Contact page** — Static email/phone only; no in-app message sending.
8. **Chat history** — Stored in Flask session (single browser session; not a shared database).
9. **Kiswahili LLM** — Chat and advisories use curated locale text where the small model is unreliable.
10. **English LLM** — May occasionally hallucinate fungicide names; farmers should verify with extension officers.

---

## 15. Future Enhancement Opportunities

- GPU inference (`onnxruntime-gpu`)
- Additional languages (new `locales/*.json` files)
- Fine-tune SmolLM2 on agriculture Q&A (improve chatbot accuracy)
- Kiswahili fine-tune or dedicated Swahili small model
- Model versioning and retraining pipeline
- User email on registration
- Classification history export (CSV/PDF)
- Progressive Web App (PWA) for mobile field use
- Docker deployment package
- HTTPS and production WSGI server configuration

---

## 16. Project Team

| Name | Role | Institution | Contact |
|------|------|-------------|---------|
| **Joseph Walusimbi** | ML model, ONNX export, Flask backend | Soroti University, Uganda | mrjosephwalusimbi@gmail.com · +256 764 123306 |
| **Chelangat Specioza** | Web UI, UX, i18n, authentication | Soroti University, Uganda | speciozachelangat@gmail.com · +256 742 353064 |

---

## 17. Document Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | June 2026 | Initial system report |
| 2.0 | June 2026 | Bilingual EN/SW support, offline locales & CSS, Team page, updated API, full offline operation, project structure |
| 3.0 | June 2026 | GGUF integration: AI advisories, offline farmer chatbot, `llm_advisor.py`, LLM API routes, hybrid Kiswahili strategy |

---

*This report describes the system as implemented in the `Coffee Leaf Disease Detector` project directory. For operational steps, refer to `howtorun.md`.*
