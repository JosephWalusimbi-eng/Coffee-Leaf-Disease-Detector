# How to Run — Coffee Leaf Disease Detector

This guide walks you through running the Coffee Leaf Disease Detection and Classification system on your local PC (Windows, macOS, or Linux).

---

## What This System Does

The app is a Flask web application that:

1. Lets users **register and log in**
2. Accepts a **coffee leaf image** (upload or webcam capture)
3. Classifies the image into one of three classes using an ONNX model:
   - **healthy leaves**
   - **Leaf rust**
   - **Phoma**
4. Shows the **confidence score** and **countermeasures** for detected diseases
5. Saves uploaded and classified images under `classified_images/`

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| **Python** | 3.10 or newer (3.10+ recommended) |
| **Internet** | Needed only for first-time `pip install` and Tailwind CDN in the browser |
| **Web browser** | Chrome, Edge, or Firefox |
| **Disk space** | ~500 MB for Python packages + model file |

### Check Python

Open a terminal (PowerShell on Windows) and run:

```powershell
python --version
```

If `python` is not found, install Python from [https://www.python.org/downloads/](https://www.python.org/downloads/) and enable **“Add Python to PATH”** during setup.

---

## Project Structure (Key Files)

```
coffee_classification/
├── onnx_server.py          # Main Flask server (start this)
├── coffee_model.onnx       # Trained ONNX model (required)
├── requirements.txt        # Python dependencies
├── users.db                # User database (auto-created on first run)
├── classified_images/      # Saved uploads and predictions (auto-created)
├── templates/              # HTML pages (login, home, about, contact)
└── static/images/          # Background and UI images
```

**Important:** `coffee_model.onnx` must be in the project root. The server will fail to start if this file is missing.

---

## Step-by-Step Setup

### 1. Open the project folder

```powershell
cd "D:\Coffee leaf Disease detector\coffee_classification"
```

Adjust the path if your project is located elsewhere.

### 2. (Recommended) Create a virtual environment

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

### 3. Install dependencies

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

### 4. Verify the model file

Confirm `coffee_model.onnx` exists in the project root:

```powershell
dir coffee_model.onnx
```

---

## Running the Server

From the project root (with virtual environment activated if you created one):

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
5. Click **View Countermeasures** for disease-specific advice

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
curl.exe -X POST -F "file=@classified_images\Leaf_rust\Leaf_rust_1763489526.jpg" http://localhost:5000/predict
```

**Or use the included test script** (if present):

```powershell
python test_predict.py
```

**Example JSON response:**

```json
{
  "class": "Leaf rust",
  "confidence": 0.9999,
  "saved_path": "classified_images/Leaf_rust/Leaf_rust_1234567890.jpg"
}
```

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

Error relates to `coffee_model.onnx`. Ensure the file is in the project root next to `onnx_server.py`.

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
# 1. Go to project folder
cd "D:\Coffee leaf Disease detector\coffee_classification"

# 2. Create and activate virtual environment (optional)
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start server
python onnx_server.py

# 5. Open browser → http://localhost:5000
# 6. Register → Login → Upload image → Classify
```

---

## Notes

- **User data** is stored in `users.db` (SQLite). Passwords are hashed; do not commit production secrets.
- **Debug mode** is enabled in `onnx_server.py` for local development. Disable `debug=True` before deploying to production.
- The frontend loads Tailwind CSS from a CDN; no separate frontend build step is required.
