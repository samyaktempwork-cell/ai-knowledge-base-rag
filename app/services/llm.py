import json
from app.core.config import settings
from app.services.prompts import ANSWER_SYSTEM

def _client():
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    from openai import OpenAI
    return OpenAI(api_key=settings.OPENAI_API_KEY)

def chat_text(user_prompt: str, system_prompt: str = ANSWER_SYSTEM) -> str:
    client = _client()
    resp = client.chat.completions.create(
        model=settings.CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return (resp.choices[0].message.content or "").strip()

def chat_json(user_prompt: str) -> dict:
    """
    Best-effort strict JSON output.
    If model wraps JSON with extra text, we extract the first {...} block.
    """
    text = chat_text(user_prompt)
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end+1])
        raise
