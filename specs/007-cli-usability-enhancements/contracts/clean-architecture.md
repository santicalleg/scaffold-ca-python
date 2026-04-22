# CLI Contract: clean-architecture (ca)

**Feature**: 007-cli-usability-enhancements  
**Replaces**: `generate-project`

## Command

```
scaffold-ca-python clean-architecture [OPTIONS]
scaffold-ca-python ca [OPTIONS]            # identical alias
```

## Options

| Option | Type | Required | Default | Description |
|---|---|---|---|---|
| `--name` | string | Yes | — | Project name (PascalCase or snake_case) |
| `--dry-run / --no-dry-run` | flag | No | `False` | Preview files without writing |
| `--help` | flag | No | — | Show this message and exit |

## Behaviour

- `scaffold-ca-python clean-architecture --name X` ≡ old `scaffold-ca-python generate-project --name X` (byte-for-byte same output)
- `scaffold-ca-python ca --name X` ≡ `scaffold-ca-python clean-architecture --name X`
- `scaffold-ca-python clean-architecture` (no args) → prints full help, exits **0**
- `scaffold-ca-python ca --help` output ≡ `scaffold-ca-python clean-architecture --help` output (identical)

## Deprecated tombstone

```
scaffold-ca-python generate-project [OPTIONS]
```

- Hidden from `--help` listings
- Exits **1** unconditionally
- Prints: `[red]Error:[/red] 'generate-project' has been renamed. Use 'clean-architecture' (alias: ca) instead.`

## Root help representation

```
clean-architecture   Scaffold a new CA project. Alias: ca
```
