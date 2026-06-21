# System Report —  Coffee Leaf Disease Detector and Advisory System

**Document version:** 1.0  
**Date:** June 2026  
**Project folder:** `Coffee Leaf Disease Detector`  
**Developers:** Joseph Walusimbi & Chelangat Specioza — Electronics & Computer Engineers, Soroti University, Uganda

---

## 1. Executive Summary

This system is a **local web application** that helps coffee farmers and agricultural workers **detect and classify coffee leaf diseases** from photographs. Users upload or capture an image of a coffee leaf; a trained **deep learning model** (exported as ONNX) predicts whether the leaf is **healthy**, affected by **Leaf Rust**, or affected by **Phoma**. The application then displays the prediction confidence and **advisory countermeasures** for disease management.

The solution runs entirely on a **personal computer** using a **Flask** backend, **ONNX Runtime** for inference, and a **browser-based** user interface. No cloud service is required for classification once the software is installed.

---

## 2. System Purpose and Scope

### 2.1 Problem Addressed

Coffee production in Uganda and similar regions is threatened by foliar diseases such as **coffee leaf rust** (*Hemileia vastatrix*) and **Phoma**-related leaf spot diseases. Early visual identification is difficult for non-experts. This system automates image-based classification to support faster decision-making in the field or at a demonstration workstation.

### 2.2 In Scope

- User registration and login
- Image upload and webcam capture
- Three-class leaf classification
- Confidence scoring
- Disease advisory text (symptoms and countermeasures)
- Informational pages (About, Team, Contact)
- Local storage of uploaded and classified images
- REST API for prediction (`POST /predict`)

### 2.3 Out of Scope (Current Version)

- Real-time video/stream classification
- GPS mapping of diseased plants
- Multi-language UI
- Mobile native app (runs in browser only)
- Automated email from contact form
- GPU-accelerated inference (not configured by default)
- Production-grade deployment (HTTPS, WAF, rate limiting)

---

## 3. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User (Web Browser)                       │
│  Chrome / Edge / Firefox — HTML, JavaScript, Tailwind CSS       │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP (port 5000)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Flask Web Server (onnx_server.py)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ Auth routes  │  │ Page routes  │  │ POST /predict API      │ │
│  │ login/register│  │ home, about  │  │ image → classify      │ │
│  └──────┬───────┘  └──────────────┘  └───────────┬────────────┘ │
│         │                                         │             │
│         ▼                                         ▼             │
│  ┌──────────────┐                    ┌────────────────────────┐ │
│  │ SQLite       │                    │ Image pipeline         │ │
│  │ users.db     │                    │ PIL → OpenCV → NumPy   │ │
│  └──────────────┘                    └───────────┬────────────┘ │
│                                                  │             │
│                                                  ▼             │
│                                    ┌────────────────────────┐ │
│                                    │ ONNX Runtime           │ │
│                                    │ coffee_model.onnx      │ │
│                                    └────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Local filesystem: classified_images/, static/, templates/      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Technology Stack

| Layer | Technology | Role |
|-------|------------|------|
| **Runtime** | Python 3.10+ | Application language |
| **Web framework** | Flask 3.x | HTTP server, routing, sessions |
| **CORS** | flask-cors | Cross-origin API access |
| **ML inference** | ONNX Runtime 1.16+ | Load and run `coffee_model.onnx` |
| **Image processing** | OpenCV, Pillow, NumPy | Resize, normalize, save images |
| **Database** | SQLite (`users.db`) | User accounts |
| **Frontend** | HTML5, JavaScript, Tailwind CSS (CDN) | UI and client logic |
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

---

## 5. How the Application Works (Detailed)

### 5.1 Startup Sequence

1. Developer runs `python onnx_server.py` from the **project root** (`Coffee Leaf Disease Detector` folder).
2. Flask loads `coffee_model.onnx` into an ONNX Runtime `InferenceSession` at startup.
3. `init_db()` creates `users.db` and the `users` table if they do not exist.
4. Server listens on `0.0.0.0:5000` (accessible via `localhost` and LAN IP).

**Critical:** All relative paths (`coffee_model.onnx`, `users.db`, `classified_images/`) resolve from the **current working directory**. The server must be started from the project folder.

### 5.2 Authentication Flow

| Step | Action |
|------|--------|
| 1 | User visits `/` → redirected to `/login` if not authenticated |
| 2 | User registers at `/register` → username + hashed password stored in SQLite |
| 3 | User logs in at `/login` → session cookie set with `session["user"]` |
| 4 | Protected pages check session before rendering |
| 5 | `/logout` clears session |

Passwords are hashed with Werkzeug (`generate_password_hash` / `check_password_hash`). Plain-text passwords are not stored.

### 5.3 Image Classification Flow

```
User selects image or captures from webcam
        │
        ▼
Browser previews image (client-side)
        │
        ▼
User clicks "Classify Image"
        │
        ▼
JavaScript POSTs image blob to http://localhost:5000/predict
        │
        ▼
Server saves file → classified_images/uploaded_<timestamp>.jpg
        │
        ▼
PIL opens image → NumPy array
        │
        ▼
OpenCV resizes to 224 × 224 pixels
        │
        ▼
Pixel values normalized: float32, range [0.0, 1.0] (÷ 255)
        │
        ▼
Batch dimension added: shape (1, 224, 224, 3)
        │
        ▼
ONNX Runtime inference → output vector (3 class scores)
        │
        ▼
argmax → predicted class index
max    → confidence score
        │
        ▼
Image copied to classified_images/<class>/<class>_<timestamp>.jpg
        │
        ▼
JSON response: { class, confidence, saved_path }
        │
        ▼
Browser displays class + confidence %
        │
        ▼
Optional: "View Countermeasures" shows advisory text
```

### 5.4 Webcam Capture (Client-Side)

The Home page uses `navigator.mediaDevices.getUserMedia()` to access the camera. After ~2 seconds, a frame is drawn to a hidden `<canvas>` and shown as preview. The same classification pipeline is used afterward.

### 5.5 Advisory System

Countermeasures are **not generated by the model**. They are **pre-written HTML content** in `templates/test.html`, shown based on the predicted class:

| Class | Advisory content |
|-------|------------------|
| **healthy leaves** | Maintenance and monitoring guidance |
| **Leaf rust** | Symptoms + fungicide, pruning, spacing, resistant varieties |
| **Phoma** | Symptoms + fungicide, drainage, irrigation, resistant varieties |

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

- **Input:** RGB image, 224×224, normalized 0–1.
- **Output:** Three class scores (softmax-style logits or probabilities). The server uses `np.argmax` and `np.max` on the first output row.

### 6.3 Classification Classes

| Index | Class label | Folder name (saved images) |
|-------|-------------|----------------------------|
| 0 | healthy leaves | `healthy_leaves` |
| 1 | Leaf rust | `Leaf_rust` |
| 2 | Phoma | `Phoma` |

### 6.4 Model Architecture (Inferred)

The output layer name `dense_1` with a 3-unit vector suggests a **convolutional neural network (CNN)** with a fully connected final layer — typical for image classification. The 224×224 input matches common architectures (e.g. MobileNet, ResNet variants) used in agricultural disease detection.

### 6.5 Accuracy Notes

Test runs on sample images in `classified_images/` showed high confidence on known examples (e.g. ~99% Leaf rust, ~100% healthy). **Field accuracy** depends on image quality, lighting, leaf angle, and similarity to training data. The model should be validated on new local samples before relying on it for commercial decisions.

---

## 7. Application Pages and Routes

| Route | Method | Auth required | Description |
|-------|--------|---------------|-------------|
| `/` | GET | Yes | Home — classification UI |
| `/login` | GET, POST | No | Login page |
| `/register` | GET, POST | No | User registration |
| `/about` | GET | Yes | Project description |
| `/team` | GET | Yes | Developer profiles |
| `/contact` | GET | Yes | Email and phone contact info |
| `/logout` | GET | Yes | End session |
| `/predict` | POST | **No** | Image classification API |

### 7.1 Static Assets

- `static/images/` — backgrounds, team photos, UI images
- Served by Flask at `/static/...`

### 7.2 Templates

- `login.html` — branded login with system title
- `register.html` — account creation
- `test.html` — main classifier
- `about.html`, `team.html`, `contact.html` — informational pages

---

## 8. Data Storage

### 8.1 User Database (`users.db`)

SQLite table `users`:

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER | Primary key |
| `username` | TEXT | Unique |
| `email` | TEXT | Unique (column exists; registration does not currently set email) |
| `password` | TEXT | Hashed |

### 8.2 Classified Images (`classified_images/`)

Every successful prediction creates:

1. `uploaded_<timestamp>.jpg` — raw upload
2. `<class>/<class>_<timestamp>.jpg` — copy sorted by prediction

Over time this folder grows with usage. Periodic cleanup may be needed on long-running deployments.

---

## 9. API Reference

### `POST /predict`

**Request:** `multipart/form-data` with field `file` (image).

**Success response (200):**

```json
{
  "class": "Leaf rust",
  "confidence": 0.9999,
  "saved_path": "classified_images/Leaf_rust/Leaf_rust_1710000000.jpg"
}
```

**Error responses:**

| Status | Condition |
|--------|-----------|
| 400 | No file in request |
| 500 | Processing or model error |

**Note:** This endpoint does not require login. For production, consider authentication or API keys.

---

## 10. PC Specifications and Performance

### 10.1 Minimum Requirements (Functional)

Suitable for basic testing and occasional use. Inference may take 1–3 seconds per image.

| Component | Specification |
|-----------|---------------|
| **OS** | Windows 10/11, macOS 10.15+, or Linux (64-bit) |
| **CPU** | Dual-core x64, 1.6 GHz+ (e.g. Intel Core i3 / AMD equivalent) |
| **RAM** | 4 GB total system RAM |
| **Storage** | 2 GB free (Python, packages, model, images) |
| **Display** | 1366×768 or higher |
| **Network** | Not required after install (except Tailwind CDN on first page load) |
| **Camera** | Optional — for webcam capture feature |
| **Python** | 3.10 or newer |

### 10.2 Recommended Requirements (Smooth Daily Use)

Comfortable for farmers, students, or demo stations with responsive UI and fast classification.

| Component | Specification |
|-----------|---------------|
| **OS** | Windows 10/11 64-bit |
| **CPU** | Quad-core x64, 2.0 GHz+ (e.g. Intel Core i5 / Ryzen 5) |
| **RAM** | 8 GB |
| **Storage** | 5 GB free on SSD |
| **Display** | 1920×1080 |
| **Browser** | Latest Chrome or Edge |
| **Camera** | 720p+ webcam (optional) |

**Expected performance:** Model load ~2–5 s at startup; single inference typically **under 1 second** on CPU.

### 10.3 Optimal / Lab / Training Station

For frequent batch testing, development, or running alongside other apps.

| Component | Specification |
|-----------|---------------|
| **CPU** | 6+ cores (Intel i7 / Ryzen 7 or better) |
| **RAM** | 16 GB |
| **Storage** | SSD with 10+ GB free |
| **GPU** | Not used by default; optional `onnxruntime-gpu` could accelerate inference if configured |

### 10.4 Why These Specs?

| Factor | Impact |
|--------|--------|
| **Model size (~29 MB)** | Low disk and RAM footprint |
| **224×224 input** | Small tensor — CPU inference is practical |
| **Single-image batch** | No batch GPU needed |
| **Flask dev server** | Single-threaded; not for high concurrent load |
| **OpenCV + NumPy** | Modest CPU use per request |
| **Browser + Tailwind CDN** | Additional ~100–200 MB RAM in browser |

### 10.5 Concurrent Users

The built-in Flask development server (`debug=True`) is intended for **local/single-user or small demo** use. For multiple simultaneous users, deploy with **Gunicorn/waitress** behind a reverse proxy and expect linear CPU load per active classification request.

---

## 11. Software Installation Summary

```powershell
cd "D:\Coffee leaf Disease detector\coffee_classification\Coffee Leaf Disease Detector"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python onnx_server.py
```

Open: **http://localhost:5000**

See `howtorun.md` for full setup and troubleshooting.

---

## 12. Security Considerations

| Topic | Current state | Recommendation for production |
|-------|---------------|------------------------------|
| Session secret | Hardcoded `supersecretkey` | Set via environment variable |
| `/predict` auth | Open | Add login or API token |
| Password storage | Hashed (good) | Enforce password policy |
| HTTPS | Not enabled | Use TLS in production |
| Debug mode | `debug=True` | Disable in production |
| File uploads | Saved without validation | Limit size, validate MIME type |
| SQL injection | Parameterized queries (good) | Keep parameterized queries |

---

## 13. Limitations and Known Issues

1. **Working directory** — Server must run from project root; moving files breaks model loading.
2. **Three classes only** — No detection of other diseases or non-leaf objects (UI references "not a coffee leaf" but model does not output that class).
3. **Confidence display** — Shows raw max output value; interpret as model score, not calibrated probability unless model was trained with softmax probabilities.
4. **LAN access** — `0.0.0.0` exposes port 5000 on local network; firewall rules may be needed.
5. **Image quality** — Blurry, shaded, or multi-leaf photos may reduce accuracy.
6. **Offline Tailwind** — First UI load may look plain if CDN is unreachable.

---

## 14. Future Enhancement Opportunities

- GPU inference (`onnxruntime-gpu`)
- Model versioning and A/B testing
- User email field on registration
- Export classification history (CSV/PDF)
- Mobile-responsive field app (PWA)
- Additional disease classes and dataset retraining
- Docker container for one-click deployment
- Multilingual advisory content

---

## 15. Project Team

| Name | Role | Institution |
|------|------|-------------|
| **Joseph Walusimbi** | ML model, ONNX export, Flask backend | Soroti University, Uganda |
| **Chelangat Specioza** | Web UI, UX, authentication flows | Soroti University, Uganda |

**Contact:** mrjosephwalusimbi@gmail.com · +256 764 123306 · Soroti, Uganda

---

## 16. Document Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | June 2026 | Initial system report |

---

*This report describes the system as implemented in the `Coffee Leaf Disease Detector` project directory. For operational steps, refer to `howtorun.md`.*
