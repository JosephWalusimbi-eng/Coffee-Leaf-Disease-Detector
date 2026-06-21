"""Quick verification of English and Kiswahili chat replies."""
from llm_advisor import generate_chat_reply, llm_status

PROMPTS = {
    "en": (
        "My coffee leaves have orange-yellow powder on the underside and some leaves "
        "are falling off early. What disease is this and what should I do now so it "
        "doesn't spread to the rest of my farm?"
    ),
    "sw": (
        "Mimi ni mkulima mdogo wa kahawa. Majani yangu yana doa nyeusi na yanakauka. "
        "Ni ugonjwa gani hii na nifanye nini haraka kabla haiharibu mazao yangu?"
    ),
}

CLASSIFICATION = {
    "class_key": "leaf_rust",
    "class": "Leaf rust",
    "confidence": 0.95,
}


def score_reply(lang: str, reply: str) -> list[str]:
    issues = []
    if len(reply.strip()) < 40:
        issues.append("too short")
    if len(reply) > 1200:
        issues.append("very long")

  # English checks
    if lang == "en":
        if reply.count(" ") < 15:
            issues.append("may be too brief for a farmer advisory")
        sw_markers = ["majani", "kahawa", "ugonjwa", "mkulima", "dawa", "mvua"]
        if any(m in reply.lower() for m in sw_markers) and "kiswahili" not in reply.lower():
            issues.append("reply may be in wrong language (Kiswahili detected in EN test)")

    if lang == "sw":
        sw_markers = [
            "majani", "kahawa", "ugonjwa", "mkulima", "dawa", "mvua",
            "kuua", "kuvu", "kilimo", "mazao", "hifadhi",
        ]
        if not any(m in reply.lower() for m in sw_markers):
            issues.append("reply may not be in Kiswahili (few Swahili keywords)")
        en_only_phrases = ["you should spray", "fungicide immediately", "remove infected"]
        if any(p in reply.lower() for p in en_only_phrases):
            issues.append("reply looks mostly English")

    off_topic = ["bitcoin", "python code", "openai", "chatgpt", "google"]
    if any(t in reply.lower() for t in off_topic):
        issues.append("off-topic content")

    return issues


def main():
    status = llm_status()
    print("LLM status:", status)
    if not status.get("available"):
        print("SKIP: GGUF not available")
        return 1

    for lang, prompt in PROMPTS.items():
        print("\n" + "=" * 72)
        print(f"LANGUAGE: {lang}")
        print(f"PROMPT: {prompt[:100]}...")
        print("-" * 72)

        reply, source = generate_chat_reply(
            prompt, lang, [], CLASSIFICATION if lang == "en" else None
        )
        issues = score_reply(lang, reply)
        print(f"SOURCE: {source}")
        print(f"LENGTH: {len(reply)} chars, ~{len(reply.split())} words")
        print("REPLY:")
        print(reply)
        if issues:
            print("ISSUES:", ", ".join(issues))
        else:
            print("QUALITY: passed heuristic check")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
