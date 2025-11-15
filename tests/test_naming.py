import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from src.naming_engine import generate_name_and_keywords


def create_test_image(text: str, path: Path):
    img = Image.new("RGB", (400, 200), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    d.text((10, 50), text, fill=(0, 0, 0), font=font)
    img.save(path)


def test_generate_name_and_keywords(tmp_path):
    p = tmp_path / "test_diagram.png"
    create_test_image("Service Mesh Diagram", p)
    res = generate_name_and_keywords(str(p))
    assert isinstance(res, dict)
    assert "title" in res and res["title"]
    assert "keywords" in res and isinstance(res["keywords"], list)
