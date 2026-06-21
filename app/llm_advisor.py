"""Offline GGUF advisor via llama.cpp (llama-cpp-python)."""

from __future__ import annotations

import html
import os
import re
from pathlib import Path

from i18n import get_advisory, get_class_label, normalize_lang

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
GGUF_PATH = PROJECT_ROOT / "model" / "SmolLM2-360M-Instruct-Q4_K_M.gguf"

_llm = None
_llm_error: str | None = None

CLASS_CONTEXT = {
    "healthy_leaves": "healthy coffee leaf",
    "leaf_rust": "coffee leaf rust (Hemileia vastatrix)",
    "phoma": "Phoma leaf spot on coffee",
}

COFFEE_FACTS_EN = (
    "Facts: Leaf rust = Hemileia vastatrix (orange-yellow powder on leaf undersides). "
    "Phoma = dark leaf spots and holes. Advise: remove infected leaves, improve airflow, "
    "avoid excess nitrogen for Phoma, use copper or systemic fungicides early when needed."
)

SWAHILI_FEW_SHOT = (
    "Example — User: Majani yana vumbi la manjano chini. "
    "Assistant: Hii inaweza kuwa ukungu wa majani. Ondoa majani yaliyoathirika, "
    "punguza msongamano wa mimea, na tumia dawa ya kuua kuvu mapema wakati wa mvua."
)


def gguf_available() -> bool:
    return GGUF_PATH.is_file()


def llm_status() -> dict:
    if not gguf_available():
        return {
            "available": False,
            "reason": f"GGUF not found at {GGUF_PATH}. Run download_model.ps1 from repo root.",
        }
    if _llm_error:
        return {"available": False, "reason": _llm_error}
    return {"available": True, "model": GGUF_PATH.name}


def _get_llm():
    global _llm, _llm_error
    if _llm is not None:
        return _llm
    if _llm_error:
        raise RuntimeError(_llm_error)
    if not gguf_available():
        _llm_error = f"GGUF model missing: {GGUF_PATH}"
        raise RuntimeError(_llm_error)
    try:
        from llama_cpp import Llama

        n_threads = min(4, os.cpu_count() or 4)
        _llm = Llama(
            model_path=str(GGUF_PATH),
            n_ctx=2048,
            n_threads=n_threads,
            n_gpu_layers=0,
            verbose=False,
        )
        return _llm
    except Exception as exc:
        _llm_error = str(exc)
        raise RuntimeError(_llm_error) from exc


def _lang_instruction(lang: str) -> str:
    if normalize_lang(lang) == "sw":
        return (
            "You MUST answer ONLY in Kiswahili for Ugandan smallholder farmers. "
            "Use short, simple sentences. Do NOT repeat or echo the user's question. "
            + SWAHILI_FEW_SHOT
        )
    return "Respond in clear, practical English for smallholder coffee farmers."


def _html_to_plain(html_text: str) -> str:
    text = html_text.replace("•", "-")
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\u2022", "-")
    text = re.sub(r"[^\x00-\x7F\u00A0-\u024F]+", "", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _infer_class_from_message(message: str) -> str | None:
    m = message.lower()
    if any(k in m for k in ("ukungu", "vumbi", "manjano", "machungwa", "rust", "orange")):
        return "leaf_rust"
    if any(k in m for k in ("phoma", "doa nyeusi", "doa", "nyeusi", "vidonda", "hole", "kauka")):
        return "phoma"
    if any(k in m for k in ("afya", "mzima", "healthy", "haiathirika")):
        return "healthy_leaves"
    return None


def _curated_plain_advisory(class_key: str, lang: str) -> str:
    return _html_to_plain(get_advisory(class_key, lang))


def _kiswahili_reply_poor(reply: str, user_message: str) -> bool:
    reply = reply.strip()
    if len(reply) < 35:
        return True
    words = reply.lower().split()
    if len(words) < 10:
        return True
    user_words = set(user_message.lower().split())
    overlap = sum(1 for w in words if w in user_words)
    if overlap / len(words) > 0.55:
        return True
    sw_markers = (
        "majani", "kahawa", "ugonjwa", "mkulima", "dawa", "mvua",
        "kuua", "kuvu", "kilimo", "mazao", "mimea", "tumia", "ondoa",
    )
    if not any(m in reply.lower() for m in sw_markers):
        return True
    return False


def _kiswahili_chat_fallback(
    user_message: str,
    classification: dict | None,
) -> str:
    class_key = classification.get("class_key") if classification else None
    if not class_key:
        class_key = _infer_class_from_message(user_message)

    if class_key:
        return _html_to_plain(get_advisory(class_key, "sw"))

    return (
        "Samahani, mfano mdogo wa AI una changamoto na Kiswahili. "
        "Jaribu kutambua majani kwanza, au tumia ushauri huu: "
        "Fuatilia majani kila wiki, ondoa yaliyoathirika, punguza msongamano wa mimea, "
        "na tumia dawa ya kuua kuvu mapema wakati wa msimu wa mvua."
    )


def _completion(messages: list[dict], max_tokens: int = 256, lang: str = "en") -> str:
    llm = _get_llm()
    temperature = 0.25 if normalize_lang(lang) == "sw" else 0.35
    response = llm.create_chat_completion(
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=0.9,
    )
    text = response["choices"][0]["message"]["content"]
    return (text or "").strip()


def _normalize_llm_text(text: str) -> str:
    """Strip HTML tags and normalize whitespace from LLM output."""
    text = text.strip()
    text = re.sub(r"</p>\s*", "\n\n", text, flags=re.I)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<p[^>]*>", "", text, flags=re.I)
    text = re.sub(r"</?li>", "\n", text, flags=re.I)
    text = re.sub(r"</?ul>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def text_to_html(text: str) -> str:
    """Plain LLM text -> safe HTML for the UI."""
    text = _normalize_llm_text(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    lines = text.splitlines()
    parts: list[str] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith(("- ", "* ", "• ")):
            parts.append(f"• {html.escape(line[2:].strip())}")
        elif re.match(r"^\d+[\).]\s+", line):
            parts.append(html.escape(line))
        else:
            parts.append(html.escape(line))
    return "<br>".join(parts) if parts else html.escape(text)


def generate_advisory(class_key: str, confidence: float, lang: str) -> tuple[str, str]:
    """
    Returns (html_advisory, source) where source is 'curated' or 'static'.
    Uses structured farmer advisories from locales (Symptoms + Countermeasures).
    """
    lang = normalize_lang(lang)
    advisory = get_advisory(class_key, lang)
    if advisory:
        return advisory, "curated"
    return get_advisory(class_key, "en") or "", "static"


def generate_chat_reply(
    user_message: str,
    lang: str,
    history: list[dict],
    classification: dict | None = None,
) -> tuple[str, str, str | None]:
    """Returns (reply_text, source, class_key_if_curated)."""
    lang = normalize_lang(lang)
    inferred_key = _infer_class_from_message(user_message)
    if not inferred_key and classification:
        inferred_key = classification.get("class_key")

    if inferred_key:
        return _curated_plain_advisory(inferred_key, lang), "curated", inferred_key

    system = (
        "You are CoffeeVision, an offline coffee agriculture assistant for farmers "
        "in Uganda and East Africa. Answer questions about coffee diseases, crop care, "
        "and farming. Keep answers under 150 words. Do not refer to the internet or cloud APIs. "
        + (COFFEE_FACTS_EN + " " if lang == "en" else "")
        + _lang_instruction(lang)
    )
    if classification:
        ck = classification.get("class_key", "")
        label = classification.get("class", "")
        system += (
            f"\nRecent leaf scan: {label} "
            f"({classification.get('confidence', 0) * 100:.1f}% confidence). "
            f"Prioritize advice for this disease ({ck})."
        )

    messages: list[dict] = [{"role": "system", "content": system}]
    for item in history[-8:]:
        role = item.get("role", "user")
        if role not in ("user", "assistant"):
            continue
        content = localize_chat_message(item, lang)
        if content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_message.strip()})

    try:
        text = _completion(messages, max_tokens=220, lang=lang)
        if lang == "sw" and _kiswahili_reply_poor(text, user_message):
            print("LLM Kiswahili reply low quality; using curated fallback.")
            fb = _kiswahili_chat_fallback(user_message, classification)
            fb_key = _infer_class_from_message(user_message)
            return fb, "static", fb_key
        return text, "llm", None
    except Exception as exc:
        print(f"LLM chat fallback: {exc}")
        return (
            (
                "The offline advisor is unavailable. Run download_model.ps1 and install "
                "llama-cpp-python, then restart the server."
                if lang == "en"
                else "Mshauri wa ndani haupatikani. Pakia modeli ya GGUF na llama-cpp-python, kisha washa upya seva."
            ),
            "static",
            None,
        )


def translate_chat_content(
    text: str,
    source_lang: str,
    target_lang: str,
) -> str:
    """Translate a single chat bubble to the target language."""
    source_lang = normalize_lang(source_lang)
    target_lang = normalize_lang(target_lang)
    text = text.strip()
    if not text or source_lang == target_lang:
        return text

    try:
        if target_lang == "sw":
            system = (
                "Translate this coffee-farming chat message into Kiswahili for Ugandan smallholders. "
                "Keep the same meaning and tone. Output ONLY the Kiswahili translation."
            )
        else:
            system = (
                "Translate this coffee-farming chat message into English. "
                "Keep the same meaning and tone. Output ONLY the English translation."
            )
        translated = _completion(
            [{"role": "system", "content": system}, {"role": "user", "content": text}],
            max_tokens=min(300, len(text.split()) * 3 + 60),
            lang=target_lang,
        )
        translated = translated.strip()
        if not translated:
            return text
        if target_lang == "sw" and _kiswahili_reply_poor(translated, text):
            inferred = _infer_class_from_message(text)
            if inferred:
                return _html_to_plain(get_advisory(inferred, "sw"))
        return translated
    except Exception as exc:
        print(f"Chat translation fallback: {exc}")
        return text


def localize_chat_message(msg: dict, target_lang: str) -> str:
    """Return message text in target_lang; cache translations on the message dict."""
    target_lang = normalize_lang(target_lang)
    translations = msg.get("translations") or {}
    if target_lang in translations:
        return translations[target_lang]

    class_key = msg.get("class_key")
    if class_key and msg.get("source") in ("curated", "static"):
        translated = _curated_plain_advisory(class_key, target_lang)
        translations[target_lang] = translated
        msg["translations"] = translations
        return translated

    source_lang = normalize_lang(msg.get("lang", "en"))
    source_text = (msg.get("content") or "").strip()
    if source_lang == target_lang:
        translated = source_text
    else:
        translated = translate_chat_content(source_text, source_lang, target_lang)

    translations[target_lang] = translated
    msg["translations"] = translations
    return translated


def localize_chat_history(history: list[dict], target_lang: str) -> list[dict]:
    """Build display-ready history in the requested language."""
    display: list[dict] = []
    last_user_key: str | None = None
    for msg in history:
        role = msg.get("role", "user")
        if role not in ("user", "assistant"):
            continue
        if role == "user":
            last_user_key = msg.get("class_key") or _infer_class_from_message(
                msg.get("content") or ""
            )
            if last_user_key and not msg.get("class_key"):
                msg["class_key"] = last_user_key
        if role == "assistant" and not msg.get("class_key") and last_user_key:
            msg["class_key"] = last_user_key
            msg["source"] = msg.get("source") or "curated"
            msg.pop("translations", None)
        content = localize_chat_message(msg, target_lang)
        if content:
            display.append({"role": role, "content": content})
    return display


def store_chat_message(
    history: list[dict],
    role: str,
    content: str,
    lang: str,
    class_key: str | None = None,
    source: str | None = None,
) -> None:
    lang = normalize_lang(lang)
    content = (content or "").strip()
    if not content or role not in ("user", "assistant"):
        return
    entry: dict = {
        "role": role,
        "content": content,
        "lang": lang,
        "translations": {lang: content},
    }
    if class_key:
        entry["class_key"] = class_key
    if source:
        entry["source"] = source
    history.append(entry)
