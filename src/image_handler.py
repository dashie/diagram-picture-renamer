from PIL import Image
from io import BytesIO
import os
import math

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


def extract_text_with_ocr(img: Image.Image) -> str:
    if not _HAS_TESSERACT:
        return ""
    try:
        return pytesseract.image_to_string(img)
    except Exception:
        return ""


def get_dominant_colors(img: Image.Image, num_colors: int = 3):
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
    return [c[1] for c in colors_sorted[:num_colors]]
