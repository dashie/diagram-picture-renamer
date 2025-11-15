import os
from typing import Optional, Dict, Any

try:
    import openai
    _HAS_OPENAI = True
except Exception:
    openai = None
    _HAS_OPENAI = False

try:
    import requests
    _HAS_REQUESTS = True
except Exception:
    requests = None
    _HAS_REQUESTS = False


def analyze_with_llm(image_path: str, ocr_text: str, colors) -> Optional[Dict[str, Any]]:
    """Optional: call OpenAI (if configured) to get title+keywords.

    Returns dict {"title": str, "keywords": [str]} or None if not available.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_MODEL")
    ollama_model = os.environ.get("OLLAMA_MODEL")
    ollama_host = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
    if not api_key or not model or not _HAS_OPENAI:
        # If OpenAI is not configured, fall back to Ollama when available
        pass

    prompt = (
        "You are an assistant that reads information from the image. "
        f"OCR_TEXT:{ocr_text}\n"
        f"COLORS:{colors}\n"
        "Generate a concise title and 5 comma-separated keywords in JSON with keys title and keywords (array)."
    )

    # Prefer Ollama (local) if configured
    if ollama_model and _HAS_REQUESTS:
        try:
            url = f"{ollama_host}/api/generate"
            payload = {"model": ollama_model, "prompt": prompt, "max_tokens": 300}
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                # Ollama responses can vary; try to extract text safely
                try:
                    j = resp.json()
                except Exception:
                    content = resp.text
                else:
                    if isinstance(j, dict) and "text" in j:
                        content = j.get("text")
                    elif isinstance(j, dict) and "results" in j:
                        # some Ollama responses include a list of result chunks
                        parts = []
                        for r in j.get("results", []):
                            if isinstance(r, dict):
                                parts.append(r.get("content", ""))
                            else:
                                parts.append(str(r))
                        content = "".join(parts)
                    else:
                        content = resp.text
                import json
                try:
                    return json.loads(content)
                except Exception:
                    return None
        except Exception:
            # If Ollama call fails, fall back to OpenAI path below
            pass

    # Fall back to OpenAI if available
    try:
        if api_key and model and _HAS_OPENAI:
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
