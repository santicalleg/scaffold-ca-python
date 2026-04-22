# Quickstart: CLI Usability Enhancements

**Feature**: 007-cli-usability-enhancements  
**Date**: 2026-03-30

## What changes

This feature makes three usability improvements to the `scaffold-ca-python` CLI:

1. **Rename**: `generate-project` → `clean-architecture` (alias `ca` unchanged)
2. **Richer help**: `gep`, `gda`, `gpipe` show types tables and examples in `--help`
3. **No-args → help**: root + all subcommands exit 0 with help when invoked without arguments

## Using the new command name

```bash
# Before (deprecated — now exits 1 with a migration hint)
scaffold-ca-python generate-project --name OrderService

# After
scaffold-ca-python clean-architecture --name OrderService
scaffold ca --name OrderService  # short alias unchanged
```

## Discovering types from help

```bash
scaffold-ca-python gep --help   # shows restapi / agent / mcp / generic table + examples
scaffold-ca-python gda --help   # shows rest-consumer / secrets / generic table + examples
scaffold-ca-python gpipe --help # shows github / azure provider table + examples
```

## No-args guidance

```bash
scaffold-ca-python          # prints root help, exits 0
scaffold-ca-python gm       # prints gm help (--name required), exits 0
scaffold-ca-python gep      # prints gep help (--type required), exits 0
scaffold-ca-python gpipe    # prints gpipe help (--provider required), exits 0
```

## Development workflow

All changes are in `src/scaffold_ca_python/`:

| File | Change |
|---|---|
| `cli.py` | Add `rich_markup_mode="rich"`, remove `no_args_is_help=True` on root, add `@app.callback` |
| `commands/generate_project.py` | Rename primary command to `clean-architecture`; add `generate-project` tombstone |
| `commands/generate_entry_point.py` | Add types epilog; update `_KAFKA_HELP`, `_MCP_CLIENT_HELP`; add `ctx` param |
| `commands/generate_driven_adapter.py` | Add types epilog; add `ctx` param |
| `commands/generate_pipeline.py` | Add providers epilog; add `ctx` param |
| `commands/generate_model.py` | Add `ctx` param + no-args guard |
| `commands/generate_use_case.py` | Add `ctx` param + no-args guard |
| `commands/generate_helper.py` | Add `ctx` param + no-args guard |
| `commands/delete_module.py` | Add `ctx` param + no-args guard |
| `commands/validate_structure.py` | Add `ctx` param + no-args guard |

Tests are in `tests/commands/` — one test file per command, plus `tests/commands/test_cli.py` (new) for root-level no-args and alias-parity tests.
