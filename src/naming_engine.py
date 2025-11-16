import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from src.image_handler import load_image, resize_image, extract_text_with_ocr
from src.llm_integration import analyze_with_llm


def generate_name_and_keywords(
        image_path: str, 
        force_tesseract: bool = False,
        verbose: bool = False, 
        save_preprocessed_img: bool = False
        ) -> Dict[str, Any]:
    """Generate a suggested name and keywords for the given image.
    Uses OCR and LLM analysis to extract title and keywords.
    Falls back to heuristics if LLM analysis fails."""

    p = Path(image_path)

    ocr_text = extract_text_with_ocr(image_path, force_tesseract=force_tesseract, verbose=verbose, save_preprocessed_img=save_preprocessed_img)

    # try LLM first
    llm = analyze_with_llm(image_path, ocr_text, verbose=verbose)
    if llm and isinstance(llm, dict) and llm.get("title"):
        return {"title": llm.get("title"), "keywords": llm.get("keywords", []), "filename": p.name}

    # fallback heuristics
    if verbose:
        print(f"[VERBOSE] LLM analysis failed or returned no title, falling back to heuristics", file=sys.stderr)

    title_base = None
    if ocr_text and ocr_text.strip():
        # take first long line
        lines = [l.strip() for l in ocr_text.splitlines() if l.strip()]
        if lines:
            title_base = lines[0][:80]

    if not title_base:
        # use filename without extension
        title_base = p.stem

    timestamp = datetime.now().strftime("%Y%m%d")
    title = f"{title_base} {timestamp}"

    # keywords: tokens from OCR and filename tokens
    keywords = set()
    for tok in re.split(r"\W+", title_base):
        if len(tok) > 2:
            keywords.add(tok.lower())
    keywords.add(p.suffix.replace('.', ''))

    keywords_str = ", ".join(sorted(keywords))
    # Inserisci le keyword nel nome del file, separandole con virgola e spazio
    filename_with_keywords = f"{title_base} [{keywords_str}] {timestamp}{p.suffix}"
    return {"title": title, "keywords": keywords_str, "filename": filename_with_keywords}


def _slugify(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[^0-9A-Za-z_-]+", " ", text)
    text = re.sub(r"  +", " ", text)
    return text.strip()


def build_final_filename(suggested_title: str, keywords: list, original_suffix: str) -> str:
    """Build a safe filename using the suggested title, keywords in square brackets,
    and a trailing timestamp separated by ' - '. Keeps the original file extension.

    Example: My_Diagram [service,mesh] - 20251115123045.png
    """
    # ensure inputs
    if not suggested_title:
        suggested_title = "image"

    # slugify title and keywords to keep filename-safe
    safe_title = _slugify(suggested_title)

    # sanitize keywords, preserve order, dedupe and take at most 5
    kw_list = []
    seen = set()
    for k in (keywords or []):
        if not isinstance(k, str):
            k = str(k)
        s = _slugify(k)
        if not s:
            continue
        if s in seen:
            continue
        seen.add(s)
        kw_list.append(s)
        if len(kw_list) >= 3:
            break

    keywords_part = ", ".join(kw_list) if kw_list else ""

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    if keywords_part:
        name_core = f"{safe_title} [{keywords_part}] - {timestamp}"
    else:
        name_core = f"{safe_title} - {timestamp}"

    # ensure extension begins with dot
    if original_suffix and not original_suffix.startswith('.'):
        original_suffix = f'.{original_suffix}'

    return f"{name_core}{original_suffix}"


def is_filename_in_desired_format(filename: str) -> bool:
    """Return True if the given filename already matches the desired pattern:
    <safe_title> [kw1,kw2] - YYYYMMDDHHMMSS.ext  OR  <safe_title> - YYYYMMDDHHMMSS.ext

    This uses a permissive regex to detect the pattern; it's intentionally lenient
    about the allowed characters in the title and keywords but requires the
    timestamp to be 14 digits (YYYYMMDDHHMMSS) and an extension.
    """
    name = Path(filename).name
    # regex: anything, optional ' [..keywords..]', space-dash-space, 14 digits, dot ext
    import re as _re

    pattern = r"^.+?(?: \[[^\]]+\])? - \d{14}\.[^\.]+$"
    return bool(_re.match(pattern, name))
