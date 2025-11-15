from PIL import Image

try:
    import pytesseract
    _HAS_TESSERACT = True
except Exception:
    pytesseract = None
    _HAS_TESSERACT = False


def load_image(path: str) -> Image.Image:
    return Image.open(path).convert("RGB")


def resize_image(img: Image.Image, max_width: int = 2000) -> Image.Image:
    w, h = img.size
    if w <= max_width:
        return img
    ratio = max_width / float(w)
    return img.resize((max_width, int(h * ratio)), Image.LANCZOS)


def extract_text_with_ocr(img: Image.Image, verbose: bool = False) -> str:
    """
    Extract text from an image using pytesseract OCR, with optional pre-processing to improve results on low-contrast text.
    Args:
        img: PIL.Image.Image
        verbose: bool
        preprocess: bool (default True) - apply grayscale, contrast, and binarization
    Returns:
        str: cleaned OCR text
    """
    preprocess = True  # set True by default, can be parameterized if needed
    if not _HAS_TESSERACT:
        return ""
    try:
        import re
        from PIL import ImageEnhance, ImageOps
        proc_img = img
        if preprocess:
            # 1. Convert to grayscale
            proc_img = proc_img.convert("L")
            # 2. Enhance contrast
            enhancer = ImageEnhance.Contrast(proc_img)
            proc_img = enhancer.enhance(2.0)  # 2.0 is a good default, can be tuned
            # 3. Adaptive threshold (binarization)
            # Use PIL's point method for simple thresholding
            # Or use ImageOps.autocontrast for further normalization
            proc_img = ImageOps.autocontrast(proc_img)
            # Try both adaptive and fixed threshold
            threshold = 180  # can be tuned
            proc_img = proc_img.point(lambda x: 255 if x > threshold else 0, mode='1')
        ocr_text = pytesseract.image_to_string(proc_img)
        ocr_text = ocr_text.strip()

        # Clean OCR text: process each line, keep only alphanumeric characters, remove empty lines
        lines = ocr_text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Keep only alphanumeric characters and common punctuation, trim whitespace
            cleaned_line = re.sub(r'[^a-zA-Z0-9\s\.,;:\-]', '', line).strip()
            cleaned_line = re.sub(r'\s+', ' ', cleaned_line)
            # Only add non-empty lines
            if cleaned_line and len(cleaned_line) > 1:
                cleaned_lines.append(f"- {cleaned_line}")
        clean_ocr_text = "\n".join(cleaned_lines) if cleaned_lines else "No text detected"
        if verbose:
            import sys
            print(f"[VERBOSE] OCR text extracted:\n{ocr_text}", file=sys.stderr)
            print(f"[VERBOSE] OCR text cleaned:\n{clean_ocr_text}", file=sys.stderr)
        return clean_ocr_text
    except Exception:
        return ""


def get_dominant_colors(img: Image.Image, num_colors: int = 3, verbose: bool = False):
    # small thumbnail to speed quantize
    thumb = img.copy()
    thumb.thumbnail((200, 200))
    # quantize to reduce palette
    palette = thumb.convert('P', palette=Image.ADAPTIVE, colors=num_colors)
    palette_rgb = palette.convert('RGB')
    # count colors
    colors = palette_rgb.getcolors(200*200)
    if not colors:
        return []
    # colors: list of (count, (r,g,b))
    colors_sorted = sorted(colors, key=lambda c: -c[0])
    result = [c[1] for c in colors_sorted[:num_colors]]
    if verbose:
        import sys
        print(f"[VERBOSE] Dominant colors extracted: {result}", file=sys.stderr)
    return result
