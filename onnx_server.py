import os
import sqlite3
import time

import cv2
import numpy as np
import onnxruntime as rt
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_cors import CORS
from PIL import Image
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"
CORS(app)

# Load ONNX model
MODEL_PATH = "coffee_model.onnx"
session_model = rt.InferenceSession(MODEL_PATH)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect("users.db")
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
@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login_page"))
    return render_template("test.html")


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return render_template("login.html", error="❌ User does not exist!")

        if not check_password_hash(row[0], password):
            return render_template("login.html", error="❌ Wrong password!")

        session["user"] = username
        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        if user:
            conn.close()
            return render_template(
                "register.html",
                error="❌ Username already exists!",
                username=username
            )

        # Hash password
        hashed_password = generate_password_hash(password)

        # Insert new user
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
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
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        save_dir = "classified_images"
        os.makedirs(save_dir, exist_ok=True)
        timestamp = int(time.time())
        uploaded_filename = f"uploaded_{timestamp}.jpg"
        uploaded_path = os.path.join(save_dir, uploaded_filename)
        file.save(uploaded_path)

        # Prepare image for model
        image = Image.open(uploaded_path)
        image_np = np.array(image)
        image_np = cv2.resize(image_np, (224, 224))
        image_np = image_np.astype(np.float32) / 255.0
        image_np = np.expand_dims(image_np, axis=0)

        # Run ONNX model
        input_name = session_model.get_inputs()[0].name
        result = session_model.run(None, {input_name: image_np})
        prediction = np.argmax(result[0])
        confidence = np.max(result[0])

        classes = ["healthy leaves", "Leaf rust", "Phoma"]
        predicted_class = classes[prediction]

        # Save classified image
        class_dir = os.path.join(save_dir, predicted_class.replace(" ", "_"))
        os.makedirs(class_dir, exist_ok=True)
        classified_filename = f"{predicted_class.replace(' ', '_')}_{timestamp}.jpg"
        classified_path = os.path.join(class_dir, classified_filename)
        Image.open(uploaded_path).save(classified_path)

        return jsonify({
            "class": predicted_class,
            "confidence": float(confidence),
            "saved_path": classified_path
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
