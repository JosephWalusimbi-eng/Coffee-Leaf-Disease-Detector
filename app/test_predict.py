import os
import requests

samples = [
    ("Leaf_rust", "classified_images/Leaf_rust/Leaf_rust_1763489526.jpg"),
    ("Phoma", "classified_images/Phoma/Phoma_1763489794.jpg"),
    ("healthy_leaves", "classified_images/healthy_leaves/healthy_leaves_1763487358.jpg"),
]

print("Testing /predict endpoint...")
print("-" * 50)
for expected, path in samples:
    with open(path, "rb") as f:
        r = requests.post("http://localhost:5000/predict", files={"file": f})
    data = r.json()
    print(f"Expected: {expected:20} -> {data.get('class')}, confidence: {data.get('confidence'):.4f}")
