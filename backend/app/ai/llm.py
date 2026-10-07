import hashlib
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

# --- Where things live ---
BACKEND_DIR = Path(__file__).resolve().parents[2]
CACHE_DIR = Path(__file__).resolve().parents[3] / "data" / "cache"

load_dotenv(BACKEND_DIR / ".env")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def _get_client():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to backend/.env")
    return genai.Client(api_key=key)


def _cache_path(system, prompt):
    raw = MODEL + "||" + system + "||" + prompt
    name = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{name}.json"


def ask_json(prompt, system=""):
    """Send a prompt to the AI and return the answer as a Python dict/list."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _cache_path(system, prompt)

    # 1. Already asked before? Return the saved answer.
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))

    # 2. Otherwise, ask the AI.
    client = _get_client()
    response = None
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system or None,
                    response_mime_type="application/json",
                ),
            )
            break
        except Exception as e:
            msg = str(e)
            if "PerDay" in msg:
                raise RuntimeError(
                    "Daily free quota used up for this model. "
                    "Switch GEMINI_MODEL or use another key."
                ) from e
            temporary = "503" in msg or "429" in msg or "UNAVAILABLE" in msg
            if temporary and attempt < 4:
                wait = 2 ** attempt * 3   # waits 3, 6, 12, 24 seconds
                print(f"AI busy, retrying in {wait}s... ({attempt + 1}/5)")
                time.sleep(wait)
            else:
                raise

    # 3. Clean up and convert the text into real data.
    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    data = json.loads(text)

    # 4. Save it so we never pay for this question again.
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


if __name__ == "__main__":
    result = ask_json(
        "Return JSON with keys 'word' and 'language' for the word 'namaste'.",
        system="You answer only with JSON.",
    )
    print(result)