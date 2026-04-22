# Data Model: CLI Usability Enhancements

**Feature**: 007-cli-usability-enhancements  
**Date**: 2026-03-30

## Summary

No new data entities are introduced by this feature. All changes are to CLI registration metadata (command names, help strings, option defaults). The `_generate_project_impl`, `_generate_entry_point_impl`, `_generate_driven_adapter_impl`, and `_generate_pipeline_impl` functions are unchanged in their logic.

## Changed CLI Registrations

### Command rename: `generate-project` → `clean-architecture`

| Field | Before | After |
|---|---|---|
| Primary command name | `generate-project` | `clean-architecture` |
| Hidden alias | `ca` (hidden) | `ca` (hidden, unchanged) |
| Deprecated tombstone | — | `generate-project` (hidden, deprecated, exits 1) |
| `short_help` on primary | "Scaffold a new Clean Architecture Python project." | "Scaffold a new CA project. Alias: ca" |

### Root app callback

| Field | Before | After |
|---|---|---|
| `no_args_is_help` on root `Typer()` | `True` | Removed |
| `@app.callback` | None | Added with `invoke_without_command=True`; shows help + exits 0 |
| `rich_markup_mode` on root `Typer()` | Not set | `"rich"` |

### Per-command signature changes (US3: no-args → help + exit 0)

Each command that has at least one required option gains:
1. `ctx: typer.Context` as first parameter
2. Required options become `Optional[<type>] = None`
3. Early-exit guard at top of function body

| Command | Affected option(s) |
|---|---|
| `gm` / `generate-model` | `--name` |
| `guc` / `generate-use-case` | `--name` |
| `gep` / `generate-entry-point` | `--type` |
| `gda` / `generate-driven-adapter` | `--type` |
| `gpipe` / `generate-pipeline` | `--provider` |
| `ghelper` / `generate-helper` | `--name` |
| `gdm` / `delete-module` | `--name` |
| `vs` / `validate-structure` | _(no required options — already exits ok; add ctx guard for consistency)_ |
| `up` / `update-project` | _(no required options — no change needed)_ |

### Help text additions (US2: types table + epilog)

| Command | Added to epilog |
|---|---|
| `gep` | Types table (restapi, agent, mcp, generic) + agent-only flag notes + Examples |
| `gda` | Types table (rest-consumer, secrets, generic) + generic --name required note + Examples |
| `gpipe` | Providers table (github, azure) + Examples |

### Updated `_*_HELP` strings

| File | Constant | Change |
|---|---|---|
| `generate_entry_point.py` | `_KAFKA_HELP` | Append "(agent type only)" |
| `generate_entry_point.py` | `_MCP_CLIENT_HELP` | Append "(agent type only)" |
| `generate_entry_point.py` | `_TYPE_HELP` | Expand to multi-line description |
| `generate_driven_adapter.py` | `_TYPE_HELP` (new) | Add module-level type help constant |
| `generate_pipeline.py` | `_PROVIDER_HELP` (new) | Add module-level provider help constant |
