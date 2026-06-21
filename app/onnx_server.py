import os
import sqlite3
import time
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as rt
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_cors import CORS
from i18n import (
    class_key_from_model_label,
    get_advisory,
    get_class_label,
    get_strings,
    normalize_lang,
)
from PIL import Image
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"
CORS(app)

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
MODEL_PATH = str(PROJECT_ROOT / "model" / "coffee_model.onnx")
USERS_DB = str(APP_DIR / "users.db")
CLASSIFIED_DIR = str(APP_DIR / "classified_images")

# Load ONNX model
session_model = rt.InferenceSession(MODEL_PATH)

BRAND_NAME = "CoffeeVision"
BRAND_FULL = (
    "CoffeeVision: AI-based Coffee leaf disease detector and Advisory system"
)
FOOTER_TEXT = "© 2026 CoffeeVision"

def get_lang():
    return normalize_lang(session.get("lang"))


def set_lang(lang):
    session["lang"] = normalize_lang(lang)


@app.context_processor
def inject_i18n():
    lang = get_lang()
    return {
        "t": get_strings(lang),
        "lang": lang,
        "brand_name": BRAND_NAME,
        "brand_full": BRAND_FULL,
        "footer_text": FOOTER_TEXT,
    }


# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()


# --- ROUTES ---
@app.route("/set-language/<lang>")
def set_language(lang):
    set_lang(lang)
    next_url = request.args.get("next")
    if not next_url or not next_url.startswith("/"):
        next_url = url_for("login_page")
    return redirect(next_url)


@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login_page"))
    return render_template("test.html")


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        lang = request.form.get("lang")
        if lang:
            set_lang(lang)

        t = get_strings(get_lang())
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect(USERS_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return render_template("login.html", error=t["error_user_not_exist"])

        if not check_password_hash(row[0], password):
            return render_template("login.html", error=t["error_wrong_password"])

        session["user"] = username
        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        lang = request.form.get("lang")
        if lang:
            set_lang(lang)

        t = get_strings(get_lang())
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect(USERS_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        if user:
            conn.close()
            return render_template(
                "register.html",
                error=t["error_username_exists"],
                username=username,
            )

        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("login_page"))

    return render_template("register.html")


@app.route("/about")
def about():
    if "user" not in session:
        return redirect(url_for("login_page"))
    return render_template("about.html")


@app.route("/team")
def team():
    if "user" not in session:
        return redirect(url_for("login_page"))
    return render_template("team.html")


@app.route("/contact")
def contact():
    if "user" not in session:
        return redirect(url_for("login_page"))
    return render_template("contact.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login_page"))


# --- ONNX Prediction API ---
@app.route("/predict", methods=["POST"])
def predict():
    lang = get_lang()
    t = get_strings(lang)

    try:
        if "file" not in request.files:
            return jsonify({"error": t["error_no_file"]}), 400

        file = request.files["file"]

        save_dir = CLASSIFIED_DIR
        os.makedirs(save_dir, exist_ok=True)
        timestamp = int(time.time())
        uploaded_filename = f"uploaded_{timestamp}.jpg"
        uploaded_path = os.path.join(save_dir, uploaded_filename)
        file.save(uploaded_path)

        image = Image.open(uploaded_path)
        image_np = np.array(image)
        image_np = cv2.resize(image_np, (224, 224))
        image_np = image_np.astype(np.float32) / 255.0
        image_np = np.expand_dims(image_np, axis=0)

        input_name = session_model.get_inputs()[0].name
        result = session_model.run(None, {input_name: image_np})
        prediction = np.argmax(result[0])
        confidence = np.max(result[0])

        model_label = MODEL_CLASSES[prediction]
        class_key = class_key_from_model_label(model_label)
        translated_class = get_class_label(class_key, lang)
        advisory = get_advisory(class_key, lang)

        class_dir = os.path.join(save_dir, model_label.replace(" ", "_"))
        os.makedirs(class_dir, exist_ok=True)
        classified_filename = f"{model_label.replace(' ', '_')}_{timestamp}.jpg"
        classified_path = os.path.join(class_dir, classified_filename)
        Image.open(uploaded_path).save(classified_path)

        return jsonify({
            "class_key": class_key,
            "class": translated_class,
            "confidence": float(confidence),
            "advisory": advisory,
            "saved_path": classified_path,
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
