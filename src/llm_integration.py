import os
from typing import Optional, Dict, Any

try:
    import openai    
    _HAS_OPENAI = True
except Exception:
    openai = None
    _HAS_OPENAI = False

def analyze_with_llm(image_path: str, ocr_text: str, verbose: bool = False) -> Optional[Dict[str, Any]]:
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

    system_prompt = (
        "You are an assistant that reads information from the image to suggest a proper filename.\n"
        "The user will provide OCR text extracted from the image.\n"
        "You must reply with valid JSON only. Do not include any explanatory text.\n"
        "Return a JSON object with this structure:\n"
        "{\n  \"title\": \"concise title here\",\n  \"keywords\": [\"keyword1\", \"keyword2\", ...]\n}\n"
        "The title should be concise (max 8 words), descriptive of the main subject of the image.\n"
        "Generally the best title can be found in the first few lines of the OCR text.\n"
        "If the first sentence is a good summary, make it better by shortening or rephrasing it, and use that as the title.\n"
        "Identify the keywords relevant to the content that represent subjects of study, and select only the 5 most relevant keywords if possible."
    )

    prompt = (
        "Return JSON object for these inputs:\n\n"
        f"OCR_TEXT:\n{ocr_text}\n\n"
    )

    if verbose:
        import sys
        print(f"[VERBOSE] LLM system_prompt:\n{system_prompt}", file=sys.stderr)
        print(f"[VERBOSE] LLM user_prompt:\n{prompt}", file=sys.stderr)

    # Prefer Ollama (local) if configured and openai library is available
    if ollama_model and _HAS_OPENAI:
        try:
            if verbose:
                import sys
                print(f"[VERBOSE] Using Ollama service at {ollama_host} with model {ollama_model}", file=sys.stderr)
            
            # Point the OpenAI client at the Ollama host (OpenAI-compatible)
            client = openai.OpenAI(
                api_key = os.environ.get("OLLAMA_API_KEY", ""),
                base_url = ollama_host
            )

            # Enforce JSON-only output with a system message and request format
            messages = [
                {"role": "system", "content": system_prompt},
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
                    result = json.loads(content)
                    if verbose:
                        import sys
                        print(f"[VERBOSE] LLM JSON result: {json.dumps(result, ensure_ascii=False)}", file=sys.stderr)
                    return result
                except Exception:
                    return None
        except Exception as e:
            # If Ollama via openai client fails, fall back to OpenAI path below
            pass

    # Fall back to OpenAI if available
    try:
        if api_key and model and _HAS_OPENAI:
            if verbose:
                import sys
                print(f"[VERBOSE] Using OpenAI service with model {model}", file=sys.stderr)
            
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
                result = json.loads(content)
                if verbose:
                    import sys
                    print(f"[VERBOSE] LLM JSON result: {json.dumps(result, ensure_ascii=False)}", file=sys.stderr)
                return result
            except Exception:
                # best-effort: look for title: and keywords:
                return None
    except Exception:
        return None
