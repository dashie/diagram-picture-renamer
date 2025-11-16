import sys
from PIL import Image
from pathlib import Path

# Detect if we are on macOS with Vision framework available
try:
    from Vision import VNRecognizeTextRequest, VNImageRequestHandler
    from Foundation import NSData
    _HAS_APPLE_VISION = True
except Exception:
    _HAS_APPLE_VISION = False

# Detect if pytesseract is available
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


def save_preprocessed_image(img: Image.Image) -> None:
    try:
        # prepare output path in cwd
        cwd = Path.cwd()
        candidate = cwd / f"preprocessed.png"
        img.save(candidate)
    except Exception as e:
        pass


def preprocess_for_ocr(img: Image.Image, max_width: int = 2000) -> Image.Image:
    from PIL import ImageEnhance, ImageOps
    # 1. Convert to grayscale
    proc_img = img.convert("L")
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
    return proc_img


def extract_text_with_tesseract(image_path: str, verbose: bool = False, save_preprocessed_img: bool = False) -> str:
    """
    Extract text from an image using pytesseract OCR, with optional pre-processing to improve results on low-contrast text.
    Args:
        img: PIL.Image.Image
        verbose: bool
        preprocess: bool (default True) - apply grayscale, contrast, and binarization
    Returns:
        str: cleaned OCR text
    """
    
    if verbose:
        print(f"[VERBOSE] extract text using Tesseract", file=sys.stderr)

    if not _HAS_TESSERACT:
        return ""
    try:
        img = load_image(image_path)
        img = resize_image(img)

        preprocess = True  # set True by default, can be parameterized if needed
        proc_img = preprocess_for_ocr(img) if preprocess else img
        save_preprocessed_image(proc_img) if save_preprocessed_img else None

        ocr_text = pytesseract.image_to_string(proc_img)
        ocr_text = ocr_text.strip()
        return ocr_text
    except Exception:
        return ""


def extract_text_boxes(req):
    """
    Extract text boxes from a VNRecognizeTextRequest result.
    """

    out = []
    for r in req.results():
        cand = r.topCandidates_(1)
        if not cand:
            continue
        text = cand[0].string()
        box = r.boundingBox()  # CGRect ((x, y), (w, h))
        out.append((text, box))
    return out


def merge_text_boxes(results, y_tolerance=0.02, max_dist=0.05):
    """
    Merge text boxes into lines based on vertical and horizontal proximity.
    """

    # results = [(text, box), ...]
    rows = []

    for text, box in sorted(results, key=lambda x: x[1][0]):  # sort by x coordinate
        line_merged = False
        (bx, by), (bw, bh) = box
        
        for r in rows:
            # same row if y-coord close and x-coord close
            _, ((rx, ry), (rw, rh)) = r[-1]
            if abs(by - ry) < y_tolerance and (bx - (rx + rw)) < max_dist:
                r.append((text, box))
                line_merged = True
                break
        
        if not line_merged:
            rows.append([(text, box)])

    # merge texts in each row
    return [" ".join([t for t, _ in row]) for row in rows]


def extract_text_with_apple_vision(image_path: str, verbose: bool = False, save_preprocessed_img: bool = False) -> str:
    """
    Extract text from an image using macOS Vision framework OCR.
    """

    if verbose:
        print(f"[VERBOSE] extract text using Apple Vision", file=sys.stderr)

    if not _HAS_APPLE_VISION:
        return ""
    try:
        req = VNRecognizeTextRequest.alloc().init()
        req.setRecognitionLevel_(1)  # HIGH
        req.setUsesLanguageCorrection_(True)

        data = NSData.dataWithContentsOfFile_(image_path)
        handler = VNImageRequestHandler.alloc().initWithData_options_(data, None)
        handler.performRequests_error_([req], None)

        boxes = extract_text_boxes(req)
        lines = merge_text_boxes(boxes)
        return "\n".join(lines)
    except Exception:
        return ""


def extract_text_with_ocr(
        image_path: str, 
        force_tesseract: bool = False,
        verbose: bool = False, 
        save_preprocessed_img: bool = False) -> str:
    """
    Extract text from an image using OCR, trying macOS Vision first and falling back to Tesseract if needed.
    """
    
    import re

    ocr_text = ""    
    try:
        if force_tesseract:                        
            if verbose:
                print(f"[VERBOSE] force using Tesseract", file=sys.stderr)
            raise Exception("Forced Tesseract")
        ocr_text = extract_text_with_apple_vision(image_path, verbose=verbose, save_preprocessed_img=save_preprocessed_img)
    except Exception:
        ocr_text = extract_text_with_tesseract(image_path, verbose=verbose, save_preprocessed_img=save_preprocessed_img)

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
        print(f"[VERBOSE] OCR text extracted:\n{ocr_text}", file=sys.stderr)
        print(f"[VERBOSE] OCR text cleaned:\n{clean_ocr_text}", file=sys.stderr)

    return clean_ocr_text
