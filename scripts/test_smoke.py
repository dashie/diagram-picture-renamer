from pathlib import Path
import tempfile
from PIL import Image, ImageDraw, ImageFont

from src.naming_engine import generate_name_and_keywords, build_final_filename


def create_test_image(text: str, path: Path):
    img = Image.new("RGB", (400, 200), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    d.text((10, 50), text, fill=(0, 0, 0), font=font)
    img.save(path)


with tempfile.TemporaryDirectory() as td:
    p = Path(td) / "test_diagram.png"
    create_test_image("Service Mesh Diagram", p)
    res = generate_name_and_keywords(str(p))
    print(res)
    new = build_final_filename(res.get('title'), res.get('keywords', []), p.suffix)
    print('final filename:', new)
