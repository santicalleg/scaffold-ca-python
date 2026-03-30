# CLI Contract: generate-driven-adapter (gda)

**Feature**: 007-cli-usability-enhancements

## Command

```
scaffold-ca-python generate-driven-adapter [OPTIONS]
scaffold-ca-python gda [OPTIONS]
```

## Options

| Option | Type | Required | Default | Description |
|---|---|---|---|---|
| `--type` | string | Yes | — | Adapter type (see Types table) |
| `--name` | string | Conditional | — | Adapter name; **required when `--type generic`** |
| `--dry-run / --no-dry-run` | flag | No | `False` | Preview files without writing |
| `--help` | flag | No | — | Show message and exit |

## Types Table (shown in `--help` epilog)

| Type | Description |
|---|---|
| `rest-consumer` | HTTP client adapter using httpx |
| `secrets` | AWS Secrets Manager adapter using boto3 |
| `generic` | Plain adapter skeleton; **`--name` required** |

## No-args behaviour

`scaffold-ca-python gda` (no `--type`) → prints full gda help, exits **0**

## Epilog (rendered in `--help`)

```
Types:
  rest-consumer   HTTP client adapter (httpx)
  secrets         AWS Secrets Manager adapter (boto3)
  generic         Plain adapter skeleton (--name required)

Examples:
  scaffold gda --type rest-consumer
  scaffold gda --type secrets
  scaffold gda --type generic --name PaymentGateway
```
