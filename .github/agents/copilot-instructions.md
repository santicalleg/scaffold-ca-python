# scaffold-ca-python Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-20

## Active Technologies
- Python 3.13 + Typer 0.16, Jinja2 3.1, Pydantic v2, Rich 14, uv (dep management) (008-fastapi-entrypoint-baseline)
- N/A — file I/O only via `FileWriter` / `TemplateRenderer` (008-fastapi-entrypoint-baseline)
- Python 3.13 + FastAPI ≥ 0.135.2, uvicorn[standard] ≥ 0.20, dependency-injector ≥ 4.49.0, pydantic-settings ≥ 2.13.1, Jinja2 ≥ 3.1, pydantic ≥ 2.0, typer ≥ 0.16, rich ≥ 14.1 (009-app-factory-split)
- N/A (code-generation tool; no database) (009-app-factory-split)
- Python 3.13 + yper, Rich (CLI); tomllib + tomli_w (TOML read/write); pytest + pytest-cov (testing); ruff (lint/format); mypy strict (types) (011-fix-restapi-cleanup)
- Local filesystem — `pyproject.toml` (TOML), `main.py` (plain file delete) (011-fix-restapi-cleanup)
- Python 3.13 + Jinja2 (template rendering), Pydantic v2 (generated schema model), FastAPI + Starlette (generated test client), pytest + pytest-cov (testing), ruff (lint/format), mypy strict (types), uv (package management) (012-fix-restapi-test-templates)
- Local filesystem — Jinja2 `.jinja2` template files (012-fix-restapi-test-templates)
- Python 3.13 + Typer (CLI), Rich (output formatting), Jinja2 (template rendering), Pydantic v2, pytest 9.0, pytest-cov, ruff, mypy strict, uv (package manager) (014-tests-in-src)
- Local filesystem — Path operations only (014-tests-in-src)
- Python 3.13 + Typer ≥ 0.16, Rich ≥ 14.1, Jinja2 ≥ 3.1, Pydantic v2, uv (015-factory-builder-refactor)
- File system only (pyproject.toml + generated project files) (015-factory-builder-refactor)
- Python 3.13+ + yper>=0.16.0, rich>=14.1.0; ruff (linter/formatter), mypy strict (type checker) (016-dedup-command-aliases)
- N/A — CLI tool, no database (016-dedup-command-aliases)
- Python 3.13+ + yper ≥ 0.16, pydantic ≥ 2.0, rich ≥ 14.1, jinja2 ≥ 3.1 (017-pep8-naming-validation)
- N/A (file generation only) (017-pep8-naming-validation)
- Python 3.13+ + Typer (CLI), Rich (output), Jinja2 (templates), Pydantic v2 (context models), `mcp>=1.0` (generated project dep), `starlette` (generated project dep), `uvicorn` (generated project dep), `dependency-injector` (generated project dep) (019-mcp-entry-point-restructure)
- N/A — file system writes only (019-mcp-entry-point-restructure)
- Python 3.13+ + hatchling (build backend), uv-dynamic-versioning (git-tag versioning, PEP 440), uv (build + publish) (020-pypi-publish-readme)
- N/A — pyproject.toml (TOML) and README.md (Markdown) edits only (020-pypi-publish-readme)

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
- 020-pypi-publish-readme: Added Python 3.13+ + hatchling (build backend), uv-dynamic-versioning (git-tag versioning, PEP 440), uv (build + publish)
- 019-mcp-entry-point-restructure: Added Python 3.13+ + Typer (CLI), Rich (output), Jinja2 (templates), Pydantic v2 (context models), `mcp>=1.0` (generated project dep), `starlette` (generated project dep), `uvicorn` (generated project dep), `dependency-injector` (generated project dep)
- 017-pep8-naming-validation: Added Python 3.13+ + yper ≥ 0.16, pydantic ≥ 2.0, rich ≥ 14.1, jinja2 ≥ 3.1


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
