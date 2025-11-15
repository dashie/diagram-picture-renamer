"""Entry point CLI"""
from pathlib import Path
import json
import typer

from src.naming_engine import generate_name_and_keywords

app = typer.Typer()


@app.command()
def analyze(image_path: Path):
    """Analyze an image and generate a name and keywords for it."""
    if not image_path.exists():
        raise typer.Exit(code=2)

    result = generate_name_and_keywords(str(image_path))
    print(json.dumps(result, ensure_ascii=False))


def main():
    app()


if __name__ == "__main__":
    main()
