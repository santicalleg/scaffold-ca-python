# Contract: `up` / `update-project`

**Command**: `scaffold up` (alias: `scaffold update-project`)  
**US**: US-10 (implicit) — Update project dependencies

---

## Purpose

Updates the dependencies of the current project by delegating to `uv`. Runs `uv lock --upgrade` followed by `uv sync` in the detected project root.

---

## Signature

```
scaffold up [--dry-run]
```

| Flag | Type | Required | Default | Description |
|---|---|---|---|---|
| `--dry-run` | `bool` | No | `False` | Print the commands that would be run without executing them |

---

## Behaviour

Executes the following commands in sequence inside the project root:

```bash
uv lock --upgrade
uv sync
```

Both commands run via `subprocess.run(..., check=True, cwd=<project_root>)`. If either command fails, `up` exits with code `2`.

### Dry-run output

```
Would run:
  uv lock --upgrade   (cwd: /path/to/my_project)
  uv sync             (cwd: /path/to/my_project)
```

### Success output

```
✓ Locked updated dependencies.
✓ Synced virtual environment.
```

---

## Prerequisites

- Must be run inside a directory tree that contains a `pyproject.toml` with a `[tool.scaffold-ca-python]` section.
- `uv` must be available on `$PATH`.

---

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Update completed (or dry-run completed) successfully |
| `1` | `uv` not found on PATH, or no project root found |
| `2` | `uv lock --upgrade` or `uv sync` returned a non-zero exit code |

---

## Errors

| Condition | Message | Exit |
|---|---|---|
| No project root | `No scaffold-ca-python project found. Run 'scaffold ca' first.` | `1` |
| `uv` not on PATH | `'uv' is not installed or not on PATH. Install it from https://docs.astral.sh/uv/` | `1` |
| `uv lock --upgrade` fails | `Dependency lock failed. See output above.` | `2` |
| `uv sync` fails | `Sync failed. See output above.` | `2` |
