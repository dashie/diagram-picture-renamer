"""Entry point CLI"""
from dotenv import load_dotenv
from pathlib import Path
import json
import typer
import sys


from src.naming_engine import generate_name_and_keywords, build_final_filename, is_filename_in_desired_format
import os

# Load environment variables from .env file
load_dotenv(override=True)

# Initialize Typer app
app = typer.Typer(rich_markup_mode="rich")


@app.command()
def analyze(
    image_path: Path,
    force: bool = typer.Option(False, "--force", "-f", help="Force the renaming even if the filename seems already in the desired format"),
    rename: bool = typer.Option(False, "--rename", "-r", help="Rename the file to the suggested name with keywords and timestamp"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Print detailed information about processing steps"),
):
    """Analyze an image and optionally rename the file using the suggested name.

    When `--rename` is passed, the tool will rename the original file in-place.
    The new filename will be: <suggested_title> [kw1,kw2] - <timestamp><ext>
    """
    if not image_path.exists():
        raise typer.Exit(code=2)

    if verbose:
        print(f"[VERBOSE] Input file: {image_path.absolute()}", file=sys.stderr)

    result = generate_name_and_keywords(str(image_path), verbose=verbose)

    if verbose:
        print(f"[VERBOSE] Suggested title: {result.get('title')}", file=sys.stderr)
        print(f"[VERBOSE] Keywords: {result.get('keywords')}", file=sys.stderr)

    # perform rename if requested
    if force or rename:
        # if the existing filename already matches the desired pattern, return an error
        if not force and is_filename_in_desired_format(image_path.name):
            result["rename_error"] = "filename already matches the target format; not compatible for renaming"
            output = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) if verbose else json.dumps(result, ensure_ascii=False)
            print(output)
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
            output = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) if verbose else json.dumps(result, ensure_ascii=False)
            print(output)
            raise typer.Exit(code=3)

    output = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) if verbose else json.dumps(result, ensure_ascii=False)
    print(output)


def main():
    app()

if __name__ == "__main__":
    main()
