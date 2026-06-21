# Technical Report — CoffeeVision: Offline AI for Coffee Disease Detection

**Team ID:** Joseph Walusimbi
**Domain:** agriculture
**Model:** SmolLM2-360M-Instruct-Q4_K_M

---

## Problem

Coffee farmers in Uganda and East Africa experience significant crop losses due to delayed or inaccurate detection of leaf diseases such as coffee leaf rust and Phoma. Access to agricultural experts is limited, especially in rural areas, and internet connectivity is unreliable.

This system targets smallholder farmers and extension workers by providing an **offline-capable tool** to detect coffee leaf diseases from images and deliver treatment recommendations. Running locally on consumer hardware ensures accessibility, eliminates dependency on internet or APIs, and reduces costs in low-resource environments.

---

## Design Decisions

* **Base model:**

  * DenseNet121 (CNN) for coffee leaf disease classification
  * SmolLM2-360M-Instruct for advisory chatbot

* **Quantization:**

  * Q4_K_M used for the LLM to balance memory efficiency and response quality within 8GB RAM constraints

* **Architecture choice:**

  * Dual-model system: ONNX CNN for fast image classification (~1s inference) and GGUF LLM for interactive advisory

* **Alternatives considered:**

  * Larger LLMs rejected due to memory constraints
  * Cloud APIs rejected due to connectivity and cost
  * Lower quantization (Q2_K) reduced response quality significantly

---

## Constraints

* Target: **8 GB RAM**, integrated GPU, Ubuntu-compatible systems
* CPU-only inference (no GPU required)
* Fully offline operation (no cloud or API dependency)
* Designed for low-connectivity rural environments
* Multilingual support (English and Kiswahili) for accessibility

---

## Benchmarks

| Metric               | Value                                                |
| -------------------- | ---------------------------------------------------- |
| Machine              | HP EliteBook (Intel Core i5, 8GB RAM, 256GB storage) |
| RAM at peak          | ~500 MB – 1 GB (CNN + app), ~375 MB (LLM)            |
| Time to first token  | ~95 s                                                |
| Generation speed     | ~2.8 tokens/sec                                      |
| Image inference time | ~0.5 – 1 second                                      |
| Thermal throttling   | None observed                                        |

These are self-reported development benchmarks. Official scores are measured by the ADTC profiler on the standard evaluation machine.
