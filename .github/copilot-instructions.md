# Copilot Instructions for diagram-picture-namer

## Project Overview

**diagram-picture-renamer** is an LLM-based tool that analyzes diagram images and generates meaningful, contextual names for them. This is an experimental lab project exploring AI-driven image understanding and naming conventions.

### Key Purpose
- Analyze diagram pictures content using LLM vision capabilities
- Generate descriptive, structured names based on diagram semantics
- Rename the image files accordingly when the orginal name is generic (e.g., DSC_1234.png)
- Support batch processing of multiple images

## Architecture & Components

### Technical Architecture
- **Language**: Python 3.10+
- **Dependecy Management**: Use uv env for isolating dependencies
- **LLM Integration**: Use Ollama API for local LLM calls (e.g., Claude Vision, GPT-4V)
- **Image Handling**: Use Pillow for image processing (resizing, format handling)
- **CLI Interface**: Use argparse or Typer for command-line interaction
- **Logging**: Use standard logging module for tracking processing steps and errors

### Version Control
- Use Git for version control
- Follow feature-branch workflow for development
- Write clear commit messages following Conventional Commits including type, scope, and description
- The commit messages after the first line should provide additional context if necessary using bullet points or paragraphs, with all the information needed to understand the change. But should not exceed 72 characters per line and 10 lines in total.

### High-Level Data Flow
1. **Image Input** → **LLM Vision Analysis** → **Name Generation** → **Output/Persistence**

### Core Design Patterns
- **Modular structure**: Separation of image handling, LLM integration, and naming logic
- **LLM-driven analysis**: Leverage vision capabilities (e.g., Claude Vision, GPT-4V) for semantic understanding
- **Stateless processing**: Each image processed independently; results can be cached
- **Configurable prompts**: Easy to update LLM prompts for different diagram types or naming conventions
- **Run off-line**: Designed to be executed as a CLI tool or integrated into larger pipelines using local LLM instances and without relying on cloud services

## Project-Specific Conventions

### Language & Style
- Follow PEP 8 for Python code style
- Use type hints for all functions and methods
- Use always and only english for code comments, documentation, and commit messages

### Naming Output Format
When implementing the naming engine:
- Use structured naming: `[DiagramType]_[MainPurpose]_[Timestamp]` (example: `Architecture_ServiceMesh_20251115`)
- Store metadata alongside images: diagram type, confidence score, LLM reasoning
- Support customizable naming templates

### Image Input Handling
- Support: PNG, JPG, SVG (if rasterized), WebP
- Resize large images to ~2000px max width (balance quality vs. token usage)
- Preserve original images; store results in separate output directory
- Analyze imege using SigCLIP or similar models for diagram understanding
- Use tesseract OCR for text extraction if diagrams contain significant text

### LLM Integration Points
- **Prompt engineering**: Keep prompts focused on extracting diagram type, purpose, and key elements
- **Token optimization**: Include image compression/resizing to reduce token consumption
- **Error handling**: Retry failed analyses; implement backoff for rate limits
- **Caching**: Store LLM responses to avoid re-processing identical images

## Integration Points & External Dependencies

### LLM Provider (e.g., Claude, OpenAI)
- Use vision models with image input capabilities
- Handle authentication via API keys in environment variables
- Respect rate limits; implement exponential backoff

### File System Operations
- Use async I/O for batch processing (non-blocking)
- Organize outputs by diagram type or processing date

### Logging & Monitoring
- Log each image processed with: input path, generated name, confidence score, LLM tokens used
- Track processing time per image and batch totals
- Alert on repeated LLM failures or API errors

## Project Structure

```diagram-picture-renamer/
|── .gitignore                 # Git ignore file
│── .github/copilot-instructions.md  # This file
│── README.md                  # Project overview and setup instructions
│── pyproject.toml             # Project metadata and build configuration
├── doc/
│   ├── architecture.md        # Detailed architecture documentation
│   ├── usage.md               # User guide and CLI instructions
├── src/
│   ├── main.py                # Entry point for CLI
│   ├── image_handler.py       # Image loading, resizing, format handling
│   ├── llm_integration.py     # LLM API calls and prompt management
│   ├── naming_engine.py       # Logic for generating names based on LLM output
│   ├── utils.py               # Helper functions (logging, config)
├── tests/
│   ├── *                      # Unit and integration tests  
├── examples/
│   ├── *                      # Sample diagram images for testing
├── tmp/                       # Temporary files during processing (ignored in git)
├── out/                       # Renamed images output directory (ignored in git)
```
