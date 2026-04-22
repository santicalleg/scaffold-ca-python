# Research: PyPI Publishing & README Documentation

**Feature**: `020-pypi-publish-readme`
**Status**: Complete — no NEEDS CLARIFICATION items remain

---

## 1. Current `pyproject.toml` gaps vs. PyPI requirements

**Decision**: Add `license`, `keywords`, `classifiers`, `[project.urls]`, and a named `authors` entry to `[project]`.

**Rationale**: PyPI validates these fields at upload time. `classifiers` and `keywords` also
improve discoverability. The `[project.urls]` section enables the sidebar links on the PyPI
project page (Homepage, Repository, Issues).

**Findings**:

| Field | Current state | Required action |
|-------|---------------|-----------------|
| `license` | absent | Add `license = "MIT"` (SPDX identifier, PEP 639) |
| `keywords` | absent | Add `["clean architecture", "scaffold", "code generation", "cli", "python"]` |
| `classifiers` | absent | Add standard Trove classifiers (see data-model.md) |
| `[project.urls]` | absent | Add Homepage, Repository, Issues |
| `authors[0].name` | absent (email-only) | Add `name = "Santiago Callegari"` alongside existing email |
| `description` | ✅ present | "Scaffolder to generate Clean Architecture apps" — keep as-is |
| `readme` | ✅ present | `README.md` — keep as-is |
| `requires-python` | ✅ present | `>=3.13` — keep as-is |

**Alternatives considered**:
- Using `license-files = ["LICENSE"]` (PEP 639 style) instead of `license = "MIT"` — both
  are valid; `license = "MIT"` is simpler and widely supported.

---

## 2. Build system validation

**Decision**: Keep hatchling + uv-dynamic-versioning; use `uv build` to produce artifacts.

**Rationale**: The build system is already functional (`v0.0.1` tag exists). The
`[tool.hatch.build.targets.wheel.force-include]` entry already bundles
`src/scaffold_ca_python/templates/` into the wheel — FR-003 is already satisfied.

**Findings**:
- `uv build` invokes hatchling and produces both wheel (`.whl`) and sdist (`.tar.gz`) in `dist/`.
- `uv-dynamic-versioning` reads the nearest git tag (`v0.0.1`) and produces PEP 440 version strings.
- No changes required to the build system itself.
- The `dist/` directory should be added to `.gitignore` if not already present.

**Alternatives considered**:
- `twine` for publishing — rejected; project already mandates `uv` (Principle IV).
- `flit` as build backend — rejected; hatchling is already configured and working.

---

## 3. `uv publish` authentication

**Decision**: Publish using `uv publish` with a PyPI API token configured via
`UV_PUBLISH_TOKEN` environment variable or `$HOME/.netrc`.

**Rationale**: `uv publish` is the idiomatic method when using the `uv` toolchain.
Credentials should never be stored in `pyproject.toml` or committed to source control.

**Findings**:
- `uv publish` reads credentials from the environment variable `UV_PUBLISH_TOKEN`
  (preferred for CI) or from `~/.netrc` (preferred for local use).
- TestPyPI can be targeted with `uv publish --index https://test.pypi.org/legacy/`.
- CI/CD automation is out of scope for this feature (per spec Assumptions).

**Alternatives considered**:
- `TWINE_USERNAME` / `TWINE_PASSWORD` — not applicable since we're not using twine.

---

## 4. README rendering compatibility

**Decision**: Use standard CommonMark/GFM Markdown. No relative image links. No custom HTML.

**Rationale**: PyPI renders READMEs via `readme_renderer`. It supports CommonMark but
strips many HTML attributes and rejects relative links that can't be resolved. GitHub
renders GFM natively. Both platforms converge on plain Markdown with absolute URLs for
any images or badges.

**Findings**:
- Shields.io badges use absolute URLs — safe for PyPI.
- Code blocks with language annotations (`python`, `bash`) render correctly on both platforms.
- Tables render correctly on both GitHub and PyPI.
- `pyproject.toml` must declare `readme.content-type = "text/markdown"` OR use the shorthand
  `readme = "README.md"` which hatchling infers as `text/markdown` automatically.

**Alternatives considered**:
- RST format — more powerful for PyPI but adds friction for GitHub contributors; rejected.

---

## 5. Trove classifiers selection

**Decision**: Use the following classifiers:

```toml
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Code Generators",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.13",
    "Operating System :: OS Independent",
    "Environment :: Console",
    "Typing :: Typed",
]
```

**Rationale**: These classifiers accurately describe a CLI code-generation tool for
Python developers. `Development Status :: 4 - Beta` is appropriate for a
pre-1.0 tool (latest tag is `v0.0.1`).

**Alternatives considered**:
- `Development Status :: 3 - Alpha` — more conservative, but the tool has functional
  test coverage and published features; Beta is appropriate.
- `Development Status :: 5 - Production/Stable` — premature for `v0.0.1`.
