# How to Run — Coffee Leaf Disease Detector

This guide walks you through running the system locally on your PC (Windows, macOS, or Linux).

---

## Repository layout (ADTC structure)

```
Coffee Leaf Disease Detector/
├── download_model.ps1      # Windows — run from repo root first
├── download_model.sh       # Linux/macOS — run from repo root first
├── model/coffee_model.onnx # Created by download script (not in git)
└── app/                    # Run all commands below from here
    ├── onnx_server.py
    ├── requirements.txt
    └── ...
```

---

## What This System Does

The app is a Flask web application (**CoffeeVision**) that:

1. Lets users **register and log in** (English or Kiswahili)
2. Accepts a **coffee leaf image** (upload or webcam capture)
3. Classifies the image into one of three classes using an ONNX model:
   - **healthy leaves**
   - **Leaf rust**
   - **Phoma**
4. Shows the **confidence score**
5. Provides **AI-generated farmer advisories** (GGUF in English; curated Kiswahili)
6. Includes an **offline chatbot** (**Ask CoffeeVision**) for follow-up questions
7. Saves uploaded and classified images under `classified_images/`

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| **Python** | 3.10 or newer (3.10+ recommended) |
| **Internet** | Needed only for first-time `pip install` and model downloads |
| **Web browser** | Chrome, Edge, or Firefox |
| **Disk space** | ~800 MB for Python packages + ONNX + GGUF models |

### Check Python

Open a terminal (PowerShell on Windows) and run:

```powershell
python --version
```

If `python` is not found, install Python from [https://www.python.org/downloads/](https://www.python.org/downloads/) and enable **“Add Python to PATH”** during setup.

---

## Project Structure (Key Files)

```
Coffee Leaf Disease Detector/
├── metadata.json           # ADTC submission metadata
├── download_model.sh       # Downloads model to model/
├── REPORT.md               # Technical report for judges
├── model/
│   ├── coffee_model.onnx   # Trained ONNX classifier (required)
│   └── SmolLM2-360M-Instruct-Q4_K_M.gguf  # Offline advisor (required for AI chat/advisory)
└── app/
    ├── onnx_server.py      # Main Flask server (start this)
    ├── llm_advisor.py      # GGUF / llama.cpp integration
    ├── requirements.txt
    ├── users.db            # Auto-created on first run
    ├── classified_images/  # Auto-created
    ├── locales/            # en.json, sw.json
    ├── templates/
    └── static/
```

**Important:** Run `download_model.ps1` and `download_classifier.ps1` from the **repo root** before starting the server. You need both `model/coffee_model.onnx` (classifier) and `model/SmolLM2-360M-Instruct-Q4_K_M.gguf` (offline advisor).

---

## Step-by-Step Setup

### 1. Open the repository root

```powershell
cd "D:\Coffee leaf Disease detector\coffee_classification\Coffee Leaf Disease Detector"
```

### 2. Download the model

```powershell
.\download_model.ps1        # GGUF — ADTC
.\download_classifier.ps1     # ONNX — classifier app
```

### 3. Go to the app folder

```powershell
cd app
```

### 4. (Recommended) Create a virtual environment

Isolates dependencies from other Python projects on your machine.

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 5. Install dependencies

```powershell
pip install -r requirements.txt
```

This installs:

- **Flask** — web server
- **flask-cors** — cross-origin support for the API
- **opencv-python** — image resizing
- **numpy** — numerical operations
- **onnxruntime** — ONNX model inference
- **Pillow** — image loading and saving
- **llama-cpp-python** — on-device GGUF inference for advisories and chat

`llama-cpp-python` may take several minutes to install on Windows (it compiles native code). If install fails, try:

```powershell
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

### 6. Verify the model files

From the **repo root**:

```powershell
dir model\coffee_model.onnx
dir model\SmolLM2-360M-Instruct-Q4_K_M.gguf
```

---

## Running the Server

From the **app** folder (with virtual environment activated if you created one):

```powershell
python onnx_server.py
```

You should see output similar to:

```
 * Running on http://0.0.0.0:5000
 * Running on http://127.0.0.1:5000
```

The server runs on **port 5000** with debug mode enabled.

### Stop the server

Press `Ctrl + C` in the terminal.

---

## Using the Web Application

### 1. Open the app in your browser

Go to:

```
http://localhost:5000
```

You will be redirected to the login page.

### 2. Register a new account

1. Open **http://localhost:5000/register**
2. Enter a username and password
3. Click Register
4. You will be redirected to the login page

### 3. Log in

1. Enter your username and password
2. After login, you are taken to the **Home** page (classification UI)

### 4. Classify a coffee leaf image

**Option A — Upload an image**

1. Click **Choose Image**
2. Select a coffee leaf photo from your PC
3. Click **Classify Image**
4. View the predicted class and confidence percentage
5. Click **View Countermeasures** for an AI-generated farmer advisory (loads the GGUF model on first use; may take 10–30 seconds on CPU)
6. Use the **Ask CoffeeVision** chat panel for follow-up questions (same offline model)

**Note:** If the GGUF file is missing or `llama-cpp-python` is not installed, advisories fall back to saved text in `locales/`. Chat will show an unavailable message.

**Option B — Webcam capture**

1. Click **Take Photo**
2. Allow camera access when prompted
3. Wait ~2 seconds for the capture
4. Click **Classify Image**

### 5. Other pages

| Page | URL |
|------|-----|
| Home (classifier) | http://localhost:5000/ |
| About | http://localhost:5000/about |
| Contact | http://localhost:5000/contact |
| Logout | http://localhost:5000/logout |

---

## Testing the API Directly (Optional)

The `/predict` endpoint does **not** require login. You can test it with a sample image:

**PowerShell:**

```powershell
curl.exe -X POST -F "file=@app\classified_images\Leaf_rust\Leaf_rust_1763489526.jpg" http://localhost:5000/predict
```

**Or use the included test script** (if present):

```powershell
python test_predict.py
```

**Example JSON response:**

```json
{
  "class_key": "leaf_rust",
  "class": "Leaf rust",
  "confidence": 0.9999,
  "saved_path": "classified_images/Leaf_rust/Leaf_rust_1234567890.jpg",
  "llm_available": true
}
```

### LLM APIs (login required)

After logging in in the browser (session cookie), you can call:

| Endpoint | Method | Body | Purpose |
|----------|--------|------|---------|
| `/api/llm-status` | GET | — | Check if GGUF + llama-cpp-python are ready |
| `/api/advisory` | POST | `{"class_key":"leaf_rust","confidence":0.99}` | Generate farmer advisory HTML |
| `/api/chat` | POST | `{"message":"How do I treat leaf rust?"}` | Chat reply (uses session history) |
| `/api/chat/clear` | POST | — | Clear chat history |

Advisory and chat use `model/SmolLM2-360M-Instruct-Q4_K_M.gguf` via `llm_advisor.py`. First call loads the model into memory (~258 MB).

---

## Where Images Are Saved

Every prediction saves two copies:

| Location | Description |
|----------|-------------|
| `classified_images/uploaded_<timestamp>.jpg` | Original upload |
| `classified_images/<class>/<class>_<timestamp>.jpg` | Copy sorted by predicted class |

Folders are created automatically (`healthy_leaves`, `Leaf_rust`, `Phoma`).

---

## Troubleshooting

### `ModuleNotFoundError` (e.g. No module named 'flask')

Install dependencies:

```powershell
pip install -r requirements.txt
```

Ensure your virtual environment is activated if you use one.

### Server fails on startup — model not found

Error relates to `model/coffee_model.onnx`. Run `download_classifier.ps1` from the repo root.

### Advisories show "Using saved advisory" or chat says unavailable

1. Run `download_model.ps1` from repo root (GGUF file ~248 MB).
2. Install `llama-cpp-python` (see Step 5 — may take several minutes on Windows).
3. Restart `python onnx_server.py`. First advisory/chat request loads the model (slow on CPU).

### `llama-cpp-python` install fails on Windows

Try the prebuilt CPU wheel:

```powershell
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

### `python` command not found

Use `py` on Windows:

```powershell
py -m pip install -r requirements.txt
py onnx_server.py
```

### Cannot activate venv on Windows (execution policy)

Run once in PowerShell:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again:

```powershell
.\venv\Scripts\Activate.ps1
```

### Browser shows “Classifying…” then an error

- Confirm the server is still running in the terminal
- Confirm you are using **http://localhost:5000** (not another port)
- Check the terminal for error messages

### Camera not working

- Grant camera permission in your browser
- Use **Choose Image** instead if no webcam is available

### Port 5000 already in use

Another program is using port 5000. Either stop that program or edit the last line of `onnx_server.py`:

```python
app.run(host="0.0.0.0", port=5001, debug=True)
```

Then open **http://localhost:5001** and update `API_URL` in `templates/test.html` if needed.

---

## Quick Reference — Full Run Procedure

```powershell
# 1. Repo root — download model
cd "D:\Coffee leaf Disease detector\coffee_classification\Coffee Leaf Disease Detector"
.\download_model.ps1

# 2. App folder
cd app
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python onnx_server.py

# 3. Browser → http://localhost:5000
```

---

## Notes

- **User data** is stored in `users.db` (SQLite). Passwords are hashed; do not commit production secrets.
- **Debug mode** is enabled in `onnx_server.py` for local development. Disable `debug=True` before deploying to production.
- Styles are served from `app/static/css/app.css`; no separate frontend build step is required.
