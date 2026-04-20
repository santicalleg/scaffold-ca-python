# scaffold-ca-python

[![PyPI version](https://img.shields.io/pypi/v/scaffold-ca-python.svg)](https://pypi.org/project/scaffold-ca-python/)
[![Python](https://img.shields.io/pypi/pyversions/scaffold-ca-python.svg)](https://pypi.org/project/scaffold-ca-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is this?

`scaffold-ca-python` is a CLI tool that scaffolds production-ready Python projects that follow Clean Architecture. It helps teams start faster by generating the project structure, modules, adapters, entry points, helpers, and pipeline files needed to keep architectural boundaries explicit. It is designed for developers who want repeatable code generation instead of hand-creating the same project pieces over and over.

## Installation

Python 3.13 or newer is required.

Install with `pip`:

```bash
pip install scaffold-ca-python
```

Install with `uv`:

```bash
uv add scaffold-ca-python
```

## Quick Start

1. Create a new Clean Architecture project.

```bash
scaffold ca --name my-app
```

2. Move into the generated project directory.

```bash
cd my-app
```

3. Generate a domain model.

```bash
scaffold gm --name Order
```

4. Validate the project structure.

```bash
scaffold vs
```

## Commands & Examples

### scaffold ca

Scaffold a new Clean Architecture project.

```bash
scaffold ca --name my-project
```

```bash
scaffold ca --name my-project --dry-run
```

### scaffold gm

Scaffold a Pydantic v2 domain model and its test stub.

```bash
scaffold gm --name Order
```

```bash
scaffold gm --name Order --dry-run
```

### scaffold guc

Scaffold a use case in `domain/usecase/`.

```bash
scaffold guc --name CreateOrder
```

```bash
scaffold guc --name CreateOrder --dry-run
```

### scaffold gda

Scaffold a driven adapter such as an HTTP client, secrets adapter, or generic outbound adapter.

```bash
scaffold gda --type rest-consumer
```

```bash
scaffold gda --type generic --name MyAdapter --dry-run
```

### scaffold gep

Scaffold an entry-point adapter for REST APIs, A2A agents, MCP servers, or generic entry points.

```bash
scaffold gep --type restapi
```

```bash
scaffold gep --type mcp --with-resources --with-prompts --dry-run
```

### scaffold gh

Scaffold a helper utility module and its test stub.

```bash
scaffold gh --name JsonParser
```

```bash
scaffold gh --name JsonParser --dry-run
```

### scaffold gpipe

Scaffold a CI/CD pipeline configuration for GitHub Actions or Azure Pipelines.

```bash
scaffold gpipe --provider github
```

```bash
scaffold gpipe --provider azure --dry-run
```

### scaffold vs

Scan the project for Clean Architecture import violations.

```bash
scaffold vs
```

```bash
scaffold vs --dry-run
```

### scaffold dm

Delete a previously generated module and its mirrored test file.

```bash
scaffold dm --name Order
```

```bash
scaffold dm --name Order --dry-run
```

### scaffold up

Update project dependencies using `uv lock --upgrade` and `uv sync`.

```bash
scaffold up --dry-run
```

```bash
scaffold update-project --dry-run
```

## Technologies

| Tool / Library | Version | Role |
|----------------|---------|------|
| Python | >=3.13 | Runtime |
| uv | latest | Dependency management, build, and publish |
| Typer | >=0.16.0 | CLI framework |
| Rich | >=14.1.0 | Terminal output formatting |
| Jinja2 | >=3.1 | Template engine for code generation |
| Pydantic v2 | >=2.0 | Runtime validation of template context |
| hatchling | latest | Build backend |
| uv-dynamic-versioning | latest | PEP 440 versioning from git tags |
| ruff | latest | Linting and formatting |
| mypy | latest (strict) | Static type checking |
| pytest + pytest-cov | latest | Test execution and coverage gating |

## Current Features

- Generates full Clean Architecture project skeletons with `scaffold ca`.
- Generates domain models with `scaffold gm`.
- Generates domain use cases with `scaffold guc`.
- Generates driven adapters with `scaffold gda`.
- Generates entry points for REST API, agent, MCP, and generic modes with `scaffold gep`.
- Generates helper utilities with `scaffold gh`.
- Generates CI/CD pipeline files with `scaffold gpipe`.
- Validates import boundaries with `scaffold vs`.
- Deletes generated modules safely with `scaffold dm`.
- Updates project dependencies with `scaffold up`.
- Supports `--dry-run` previews across commands.
- Uses Jinja2 templates for all generated code.
- Validates template context with Pydantic v2.
- Formats terminal output with Rich.
- Enforces static checks with mypy strict and ruff.
- Maintains an 80%+ coverage gate with pytest-cov.

## Contributing

1. Fork the upstream repository on GitHub: https://github.com/santicalleg/scaffold-ca-python
2. Clone your fork.

```bash
git clone https://github.com/YOUR-USER/scaffold-ca-python.git
cd scaffold-ca-python
```

3. Set up the development environment.

```bash
uv sync
```

4. Create a feature branch.

```bash
git checkout -b your-branch-feature-name
```

5. Run the test suite.

```bash
uv run pytest
```

6. Check linting.

```bash
uv run ruff check src tests
```

7. Check types.

```bash
uv run mypy src
```

8. Commit your changes and open a pull request.

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for the full text.