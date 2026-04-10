# scaffold-ca-python Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-10

## Active Technologies
- Python 3.13 + Typer 0.16, Jinja2 3.1, Pydantic v2, Rich 14, uv (dep management) (008-fastapi-entrypoint-baseline)
- N/A — file I/O only via `FileWriter` / `TemplateRenderer` (008-fastapi-entrypoint-baseline)
- Python 3.13 + FastAPI ≥ 0.135.2, uvicorn[standard] ≥ 0.20, dependency-injector ≥ 4.49.0, pydantic-settings ≥ 2.13.1, Jinja2 ≥ 3.1, pydantic ≥ 2.0, typer ≥ 0.16, rich ≥ 14.1 (009-app-factory-split)
- N/A (code-generation tool; no database) (009-app-factory-split)

- Python 3.13 + Typer 0.16.0, Rich 14.1.0 (both already in `pyproject.toml`) (007-cli-usability-enhancements)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.13: Follow standard conventions

## Recent Changes
- 009-app-factory-split: Added Python 3.13 + FastAPI ≥ 0.135.2, uvicorn[standard] ≥ 0.20, dependency-injector ≥ 4.49.0, pydantic-settings ≥ 2.13.1, Jinja2 ≥ 3.1, pydantic ≥ 2.0, typer ≥ 0.16, rich ≥ 14.1
- 008-fastapi-entrypoint-baseline: Added Python 3.13 + Typer 0.16, Jinja2 3.1, Pydantic v2, Rich 14, uv (dep management)

- 007-cli-usability-enhancements: Added Python 3.13 + Typer 0.16.0, Rich 14.1.0 (both already in `pyproject.toml`)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
