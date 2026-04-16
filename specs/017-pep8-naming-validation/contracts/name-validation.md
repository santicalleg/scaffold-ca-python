# Contract: `--name` Argument Validation

**Type**: CLI input validation contract  
**Applies to**: All scaffold commands accepting `--name`  
**Commands**: `ca`, `gm`, `guc`, `gh`, `gda`, `gep`, `dm`

---

## Accepted Values

A valid `--name` value MUST match:

```
^[a-z][a-z0-9]*([_-][a-z0-9]+)*$
```

| Format | Example | Accepted |
|--------|---------|----------|
| Single lowercase word | `order` | ✅ |
| `snake_case` | `my_project` | ✅ |
| `kebab-case` | `my-project` | ✅ |
| Alphanumeric (no separator) | `project2025` | ✅ |
| `PascalCase` | `MyProject` | ❌ |
| `camelCase` | `myProject` | ❌ |
| Consecutive separators | `my--project` | ❌ |
| Leading/trailing separator | `-my`, `my_` | ❌ |
| Starts with digit | `1project` | ❌ |
| Special characters | `my@project` | ❌ |
| Empty string | `` | ❌ |

---

## Error Response (invalid name)

When validation fails, the tool MUST:

- Print to stdout a message containing both `kebab-case` and `snake_case`
- Exit with code **1**

**Example output**:
```
Error: Invalid name 'MyProject'. Use kebab-case (e.g., 'my-project') or snake_case (e.g., 'my_project').
```

---

## Internal Normalisation

After validation, `kebab-case` input is silently normalised to `snake_case` for use as Python identifiers. No output or warning is printed for this conversion.

| Input | Module name | Class name |
|-------|-------------|------------|
| `my-project` | `my_project` | `MyProject` |
| `my_project` | `my_project` | `MyProject` |
| `order` | `order` | `Order` |
| `my-order-service` | `my_order_service` | `MyOrderService` |

---

## Invariants

1. **Generated `.py` file names**: always `snake_case` — `[a-z][a-z0-9_]*\.py`
2. **Generated `class` names**: always `PascalCase` — `[A-Z][a-zA-Z0-9]*`
3. **Validation applies regardless of `--dry-run`**
4. **Validation applies to all commands uniformly** — no command bypasses these rules
