# diagram-picture-renamer — first version

This repository contains an initial version of a CLI tool that analyzes an image and returns a title and associated keywords.

Main points:
- Language: Python
- CLI: `typer`
- Image analysis: Pillow + (optional) OCR with `pytesseract`
- LLM integration: optional via OpenAI (if configured)

Installation (macOS, zsh):

This project uses `uv` to manage the environment and sync dependencies.

Prerequisites:
- Python 3.10+
- `uv` installed (for example via pip or pipx)

Dependency installation:

```bash
# install uv (if not already available)
pip install uv

# from the repository root: sync the environment and install dependencies
uv sync
```

Note: `uv sync` creates/syncs the working environment and will install the packages listed in `requirements.txt`.
After `uv sync` you can activate the created environment (if present) or run the desired Python command directly using the environment; for example, to use the CLI:

```bash
# if uv created a .venv directory you can activate it like this (optional)
source .venv/bin/activate
python -m src.main analyze path/to/image.png
```


Usage:

```bash
python -m src.main analyze path/to/image.png
```

Example output (JSON on stdout):

{
  "title": "Architecture_ServiceMesh_20251115",
  "keywords": ["service", "mesh", "diagram", "blue", "network"]
}

Notes:
- If `OPENAI_API_KEY` is set and `OPENAI_MODEL` is defined, the tool will try to use the LLM to improve title and keywords.
- In the absence of an LLM, a local logic based on OCR (if available) and dominant colors is used.
