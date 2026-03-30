# CLI Contract: generate-pipeline (gpipe)

**Feature**: 007-cli-usability-enhancements

## Command

```
scaffold-ca-python generate-pipeline [OPTIONS]
scaffold-ca-python gpipe [OPTIONS]
```

## Options

| Option | Type | Required | Default | Description |
|---|---|---|---|---|
| `--provider` | string | **Yes** | — | CI/CD provider (see Providers table) |
| `--dry-run / --no-dry-run` | flag | No | `False` | Preview files without writing |
| `--help` | flag | No | — | Show message and exit |

## Providers Table (shown in `--help` epilog)

| Provider | Description |
|---|---|
| `github` | GitHub Actions workflow (`.github/workflows/ci.yml`) |
| `azure` | Azure Pipelines config (`azure-pipelines.yml`) |

## No-args behaviour

`scaffold-ca-python gpipe` (no `--provider`) → prints full gpipe help, exits **0**

## Epilog (rendered in `--help`)

```
Providers (--provider is required):
  github   GitHub Actions workflow (.github/workflows/ci.yml)
  azure    Azure Pipelines config (azure-pipelines.yml)

Examples:
  scaffold gpipe --provider github
  scaffold gpipe --provider azure
```
