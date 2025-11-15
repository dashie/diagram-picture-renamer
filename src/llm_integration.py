import os
from typing import Optional, Dict, Any

try:
    import openai
    _HAS_OPENAI = True
except Exception:
    openai = None
    _HAS_OPENAI = False


def analyze_with_llm(image_path: str, ocr_text: str, colors) -> Optional[Dict[str, Any]]:
    """Optional: call OpenAI (if configured) to get title+keywords.

    Returns dict {"title": str, "keywords": [str]} or None if not available.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_MODEL")
    if not api_key or not model or not _HAS_OPENAI:
        return None

    prompt = (
        "Sei un assistente che legge informazioni sull'immagine. "
        f"OCR_TEXT:{ocr_text}\n"
        f"COLORS:{colors}\n"
        "Genera un titolo sintetico e 5 keywords separate da virgola in JSON con chiavi title e keywords (array)."
    )

    try:
        openai.api_key = api_key
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
        content = resp.choices[0].message.content
        # attempt to parse JSON from content
        import json
        try:
            return json.loads(content)
        except Exception:
            # best-effort: look for title: and keywords:
            return None
    except Exception:
        return None
