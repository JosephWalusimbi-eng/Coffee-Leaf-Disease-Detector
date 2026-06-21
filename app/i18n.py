import json
from pathlib import Path

LOCALES_DIR = Path(__file__).parent / "locales"
SUPPORTED_LANGS = ("en", "sw")
DEFAULT_LANG = "en"

CLASS_KEYS = ("healthy_leaves", "leaf_rust", "phoma")
MODEL_CLASS_TO_KEY = {
    "healthy leaves": "healthy_leaves",
    "Leaf rust": "leaf_rust",
    "Phoma": "phoma",
}

_locale_cache = {}


def normalize_lang(lang):
    if lang in SUPPORTED_LANGS:
        return lang
    return DEFAULT_LANG


def _load_locale(lang):
    lang = normalize_lang(lang)
    if lang not in _locale_cache:
        path = LOCALES_DIR / f"{lang}.json"
        with open(path, encoding="utf-8") as f:
            _locale_cache[lang] = json.load(f)
    return _locale_cache[lang]


def get_strings(lang):
    return _load_locale(lang)["strings"]


def get_class_label(class_key, lang):
    return _load_locale(lang)["class_labels"].get(class_key, class_key)


def get_advisory(class_key, lang):
    return _load_locale(lang)["advisories"].get(class_key, "")


def class_key_from_model_label(model_label):
    return MODEL_CLASS_TO_KEY.get(model_label, model_label.lower().replace(" ", "_"))
