# Data Model: Deduplicate Command + Alias Function Bodies

**Feature**: 016-dedup-command-aliases  
**Date**: 2026-04-14

## N/A — Pure Structural Refactor

This feature introduces **no new entities, no new data structures, and no new Pydantic models**.

The refactor operates exclusively on the decorator metadata of existing command handler
functions inside the `register()` scope of 6 command modules. All existing entities
(`ModuleContext`, `ProjectContext`, `Layer`, `ModuleBuilder`, etc.) are unchanged.

### What changes

| Module | Before | After |
|--------|--------|-------|
| `generate_model.py` | Two `def` inside `register()` | One `def` with two `@app.command` |
| `generate_use_case.py` | Two `def` inside `register()` | One `def` with two `@app.command` |
| `generate_helper.py` | Two `def` inside `register()` | One `def` with two `@app.command` |
| `generate_entry_point.py` | Two `def` inside `register()` | One `def` with two `@app.command` |
| `generate_driven_adapter.py` | Two `def` inside `register()` | One `def` with two `@app.command` |
| `delete_module.py` | Two `def` inside `register()` | One `def` with two `@app.command` |

No schema migrations, no new template context fields, no new Pydantic validators.
