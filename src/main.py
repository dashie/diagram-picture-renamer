"""Entry point CLI"""
from dotenv import load_dotenv
from pathlib import Path
import json
import typer


from src.naming_engine import generate_name_and_keywords

# Load environment variables from .env file
load_dotenv(override=True)

# Initialize Typer app
app = typer.Typer(rich_markup_mode="rich")


@app.command()
def analyze(image_path: Path):
    """Analyze an image and print suggested title and keywords as JSON."""
    if not image_path.exists():
        raise typer.Exit(code=2)

    result = generate_name_and_keywords(str(image_path))
    print(json.dumps(result, ensure_ascii=False))


def main():
    app()

if __name__ == "__main__":
    main()
