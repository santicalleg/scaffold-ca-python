# CLI Contract: generate-entry-point (gep)

**Feature**: 007-cli-usability-enhancements

## Command

```
scaffold-ca-python generate-entry-point [OPTIONS]
scaffold-ca-python gep [OPTIONS]
```

## Options

| Option | Type | Required | Default | Description |
|---|---|---|---|---|
| `--type` | string | Yes | — | Entry-point type (see Types table) |
| `--swagger` | string | No | — | Path to OpenAPI YAML/JSON (restapi only) |
| `--enable-kafka / --no-enable-kafka` | flag | No | `False` | Add async Kafka consumer stub **(agent type only)** |
| `--enable-mcp-client / --no-enable-mcp-client` | flag | No | `False` | Add MCP tool-call client stub **(agent type only)** |
| `--dry-run / --no-dry-run` | flag | No | `False` | Preview files without writing |
| `--help` | flag | No | — | Show message and exit |

## Types Table (shown in `--help` epilog)

| Type | Description |
|---|---|
| `restapi` | FastAPI-based HTTP entry point with uvicorn runner |
| `agent` | A2A agent (A2A SDK); supports `--enable-kafka`, `--enable-mcp-client` |
| `mcp` | MCP server entry point (MCP SDK) |
| `generic` | Plain Python entry point with no specific framework |

## No-args behaviour

`scaffold-ca-python gep` (no `--type`) → prints full gep help, exits **0**

## Epilog (rendered in `--help`)

```
Types:
  restapi   FastAPI-based HTTP entry point with uvicorn runner
  agent     A2A agent; supports --enable-kafka, --enable-mcp-client
  mcp       MCP server entry point (MCP SDK)
  generic   Plain Python entry point (no framework)

Notes:
  --enable-kafka and --enable-mcp-client are only valid with --type agent

Examples:
  scaffold gep --type restapi
  scaffold gep --type agent --enable-kafka
  scaffold gep --type mcp
  scaffold gep --type restapi --swagger openapi.yaml
```
