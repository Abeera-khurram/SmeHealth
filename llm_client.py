"""
Groq client wrapper - free tier, open-weight models.
Supports both plain text calls and vision calls (for reading sonography
machine screenshots).
"""
import os
import json
import base64
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

TEXT_MODEL = os.environ.get("TEXT_MODEL", "llama-3.3-70b-versatile")
VISION_MODEL = os.environ.get("VISION_MODEL", "llama-3.2-11b-vision-preview")

_client = None


def _get_client() -> Groq:
    """Lazily creates the Groq client so importing this module (or modules
    that depend on it) doesn't crash just because GROQ_API_KEY isn't set
    yet - the key is only required once an LLM call is actually made."""
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Copy .env.example to .env and add your "
                "free Groq API key from https://console.groq.com/keys"
            )
        _client = Groq(api_key=api_key)
    return _client


def call_llm(system_prompt: str, user_prompt: str, model: str = TEXT_MODEL, json_mode: bool = False) -> str:
    kwargs = {"response_format": {"type": "json_object"}} if json_mode else {}
    resp = _get_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=1024,
        **kwargs,
    )
    return resp.choices[0].message.content


def call_llm_json(system_prompt: str, user_prompt: str, model: str = TEXT_MODEL) -> dict:
    raw = call_llm(system_prompt, user_prompt, model, json_mode=True)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": "malformed_json", "raw": raw}


def call_vision(system_prompt: str, image_path: str, question: str) -> str:
    """Reads a sonography machine screenshot using Groq's free vision model."""
    with open(image_path, "rb") as f:
        b64_image = base64.b64encode(f.read()).decode("utf-8")

    resp = _get_client().chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_image}"}},
                ],
            },
        ],
        temperature=0.1,
        max_tokens=512,
    )
    return resp.choices[0].message.content
