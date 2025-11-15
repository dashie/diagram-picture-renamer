"""Entry point CLI"""
from dotenv import load_dotenv
from pathlib import Path
import json
import typer


from src.naming_engine import generate_name_and_keywords, build_final_filename, is_filename_in_desired_format
import os

# Load environment variables from .env file
load_dotenv(override=True)

# Initialize Typer app
app = typer.Typer(rich_markup_mode="rich")


@app.command()
def analyze(
    image_path: Path,
    rename: bool = typer.Option(False, "--rename", "-r", help="Rename the file to the suggested name with keywords and timestamp"),
):
    """Analyze an image and optionally rename the file using the suggested name.

    When `--rename` is passed, the tool will rename the original file in-place.
    The new filename will be: <suggested_title> [kw1,kw2] - <timestamp><ext>
    """
    if not image_path.exists():
        raise typer.Exit(code=2)

    result = generate_name_and_keywords(str(image_path))

    # perform rename if requested
    if rename:
        # if the existing filename already matches the desired pattern, return an error
        if is_filename_in_desired_format(image_path.name):
            result["rename_error"] = "filename already matches the target format; not compatible for renaming"
            print(json.dumps(result, ensure_ascii=False))
            raise typer.Exit(code=4)

        try:
            suggested_title = result.get("title")
            keywords = result.get("keywords", [])
            original_suffix = image_path.suffix or ""
            new_name = build_final_filename(suggested_title, keywords, original_suffix)

            # ensure we don't overwrite existing files — add numeric suffix if needed
            parent = image_path.parent
            candidate = parent / new_name
            i = 1
            base, ext = os.path.splitext(new_name)
            while candidate.exists():
                candidate = parent / f"{base}_{i}{ext}"
                i += 1

            image_path.rename(candidate)
            result["renamed_to"] = str(candidate.name)
        except Exception as e:
            # include error info in JSON and exit non-zero
            result["rename_error"] = str(e)
            print(json.dumps(result, ensure_ascii=False))
            raise typer.Exit(code=3)

    print(json.dumps(result, ensure_ascii=False))


def main():
    app()

if __name__ == "__main__":
    main()
