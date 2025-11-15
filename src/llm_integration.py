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
    ollama_model = os.environ.get("OLLAMA_MODEL")
    ollama_host = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434/v1")
    if not api_key or not model or not _HAS_OPENAI:
        # If OpenAI is not configured, fall back to Ollama when available
        pass

    # Clean OCR text: process each line, keep only alphanumeric characters, remove empty lines
    import re
    lines = ocr_text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Keep only alphanumeric characters and common punctuation, trim whitespace
        cleaned_line = re.sub(r'[^a-zA-Z0-9\s\.,;:\-]', '', line).strip()
        # Only add non-empty lines
        if cleaned_line and len(cleaned_line) > 1:
            cleaned_lines.append(f"- {cleaned_line}")
    
    clean_ocr_text = "\n".join(cleaned_lines) if cleaned_lines else "No text detected"

    prompt = (
        "You are an assistant that reads information from the image and returns only JSON message.\n\n"
        f"OCR_TEXT:\n{clean_ocr_text}\n\n"
        f"COLORS:{colors}\n\n"
        "Return JSON object with this structure:\n" \
        "{\n  \"title\": \"concise title here\",\n  \"keywords\": [\"keyword1\", \"keyword2\", ...]\n}\n"
    )

    # Prefer Ollama (local) if configured and openai library is available
    if ollama_model and _HAS_OPENAI:
        try:
            # Point the OpenAI client at the Ollama host (OpenAI-compatible)
            client = openai.OpenAI(
                api_key = os.environ.get("OLLAMA_API_KEY", ""),
                base_url = ollama_host
            )

            # Enforce JSON-only output with a system message and request format
            messages = [
                {"role": "system", "content": "You must reply with valid JSON only. Do not include any explanatory text."},
                {"role": "user", "content": prompt},
            ]
            resp = client.chat.completions.create(
                model=ollama_model,
                messages=messages,
                max_tokens=300,
                temperature=0.0,
                stream=False,
                # pass format parameter to Ollama-compatible endpoint to request JSON
                response_format={ "type": "json_object" }
            )

            # Extract text from the OpenAI-style response object
            content = None
            try:
                content = resp.choices[0].message.content
            except Exception:
                # fallback if different shape (some clients use .text)
                try:
                    content = resp.choices[0].text
                except Exception:
                    content = None

            if content:
                import json
                try:
                    return json.loads(content)
                except Exception:
                    return None
        except Exception as e:
            # If Ollama via openai client fails, fall back to OpenAI path below
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
