# System Report — AI-Based Coffee Leaf Disease Detector and Advisory System

**Document version:** 2.0  
**Date:** June 2026  
**Project folder:** `Coffee Leaf Disease Detector` (repo root)  
**Application:** `app/`  
**Developers:** Joseph Walusimbi & Chelangat Specioza — Electronics & Computer Engineers, Soroti University, Uganda

---

## 1. Executive Summary

This system is a **local, offline-capable web application** that helps coffee farmers and agricultural workers **detect and classify coffee leaf diseases** from photographs. Users upload or capture an image of a coffee leaf; a trained **deep learning model** (exported as ONNX) predicts whether the leaf is **healthy**, affected by **Leaf Rust**, or affected by **Phoma**. The application displays the prediction confidence and **advisory countermeasures** in the user's chosen language.

The solution runs on a **personal computer** using a **Flask** backend, **ONNX Runtime** for inference, and a **browser-based** interface. After initial Python package installation, the system operates **without internet**: translations, styles, model, and images are all stored locally.

**Key capabilities (v2.0):**

- Bilingual UI and advisories: **English** and **Kiswahili**
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
- Disease advisory text (symptoms and countermeasures) in selected language
- Informational pages: **Home**, **About Us**, **Team**, **Contact Us**
- Local storage of uploaded and classified images
- REST API for prediction (`POST /predict`)
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
│  HTML, JavaScript, local CSS (static/css/app.css)               │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP (port 5000, localhost / LAN)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Flask Web Server (onnx_server.py)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ Auth + i18n  │  │ Page routes  │  │ POST /predict API      │ │
│  │ session[lang]│  │ home, about  │  │ image → classify       │ │
│  └──────┬───────┘  │ team, contact│  └───────────┬────────────┘ │
│         │          └──────────────┘              │             │
│         ▼                                        ▼             │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ SQLite       │  │ i18n.py      │  │ Image pipeline         │ │
│  │ users.db     │  │ locales/*.json│  │ PIL → OpenCV → NumPy  │ │
│  └──────────────┘  └──────────────┘  └───────────┬────────────┘ │
│                                                    │             │
│                                                    ▼             │
│                                    ┌────────────────────────┐   │
│                                    │ ONNX Runtime           │   │
│                                    │ coffee_model.onnx      │   │
│                                    └────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  classified_images/, static/, templates/, locales/              │
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
| **ML inference** | ONNX Runtime 1.16+ | Load and run `coffee_model.onnx` |
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
```

### 4.2 Project Structure

```
Coffee Leaf Disease Detector/          # Repo root (ADTC layout)
├── metadata.json
├── download_model.sh
├── REPORT.md
├── model/
│   └── coffee_model.onnx
└── app/
    ├── onnx_server.py
    ├── i18n.py
    ├── locales/
    ├── templates/
    ├── static/
    ├── requirements.txt
    └── howtorun.md
```

---

## 5. How the Application Works (Detailed)

### 5.1 Startup Sequence

1. Run `python onnx_server.py` from the **`Coffee Leaf Disease Detector`** folder (project root).
2. Flask loads `coffee_model.onnx` into an ONNX Runtime `InferenceSession`.
3. `init_db()` creates `users.db` if missing.
4. Server listens on `0.0.0.0:5000`.

**Critical:** Relative paths (`coffee_model.onnx`, `users.db`, `locales/`, `classified_images/`) resolve from the **current working directory**. Always start the server from the project root.

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
Map to class_key → translate label + advisory from locales/
        │
        ▼
Save copy to classified_images/<class>/<class>_<timestamp>.jpg
        │
        ▼
JSON: { class_key, class, confidence, advisory, saved_path }
        │
        ▼
Browser shows translated class + confidence %
        │
        ▼
"View Countermeasures" displays server-provided advisory HTML
```

### 5.5 Webcam Capture

The Home page uses `navigator.mediaDevices.getUserMedia()`. After ~2 seconds, a frame is captured to a `<canvas>` and used for classification. Requires camera permission in the browser.

### 5.6 Advisory System

Countermeasures are **not generated by the ML model**. They are **pre-written HTML** in `locales/en.json` and `locales/sw.json` under `advisories`, returned by `/predict` based on `session["lang"]`:

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
| **File** | `coffee_model.onnx` |
| **Location** | Project root (same folder as `onnx_server.py`) |
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
| `/` | GET | Yes | Home — image upload, capture, classification |
| `/login` | GET, POST | No | Login with language selection |
| `/register` | GET, POST | No | Account creation with language selection |
| `/about` | GET | Yes | Project overview |
| `/team` | GET | Yes | Developer profiles (Joseph Walusimbi, Chelangat Specioza) |
| `/contact` | GET | Yes | Email and telephone contact details |
| `/logout` | GET | Yes | End session |
| `/set-language/<lang>` | GET | No | Set `en` or `sw`; redirect to `next` URL |
| `/predict` | POST | **No** | Image classification API |

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

Uses `session["lang"]` for translated output. Defaults to English if no session.

**Success response (200):**

```json
{
  "class_key": "leaf_rust",
  "class": "Ukungu wa Majani (Leaf Rust)",
  "confidence": 0.9999,
  "advisory": "<b>☕ Ukungu wa Majani Umetambuliwa!</b><br>...",
  "saved_path": "classified_images/Leaf_rust/Leaf_rust_1710000000.jpg"
}
```

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
| Inference labels & advisories | Yes | `locales/*.json` |
| Styles / layout | Yes | `static/css/app.css` |
| Images & backgrounds | Yes | `static/images/` |
| ML model | Yes | `coffee_model.onnx` |
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

### 11.2 Recommended Requirements

| Component | Specification |
|-----------|---------------|
| **OS** | Windows 10/11 64-bit |
| **CPU** | Quad-core 2.0 GHz+ (Intel i5 / Ryzen 5) |
| **RAM** | 8 GB |
| **Storage** | 5 GB free on SSD |
| **Browser** | Chrome or Edge (latest) |

Model load: ~2–5 s at startup; inference typically **under 1 second** on CPU.

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

1. **Working directory** — Server must run from project root folder.
2. **Three classes only** — No other diseases or non-leaf rejection class in the model.
3. **Confidence score** — Raw model output max value; not necessarily calibrated probability.
4. **LAN exposure** — `0.0.0.0:5000` reachable on local network; configure firewall if needed.
5. **Image quality** — Blurry, shaded, or multi-leaf photos may reduce accuracy.
6. **Two languages only** — English and Kiswahili; additional languages require new locale JSON files.
7. **Contact page** — Static email/phone only; no in-app message sending.

---

## 15. Future Enhancement Opportunities

- GPU inference (`onnxruntime-gpu`)
- Additional languages (new `locales/*.json` files)
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

---

*This report describes the system as implemented in the `Coffee Leaf Disease Detector` project directory. For operational steps, refer to `howtorun.md`.*
