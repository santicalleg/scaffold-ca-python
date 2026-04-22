# Quickstart: Building & Publishing scaffold-ca-python to PyPI

**Feature**: `020-pypi-publish-readme`
**Audience**: Package maintainer

---

## Prerequisites

- Python ≥3.13
- [uv](https://docs.astral.sh/uv/) installed (`pip install uv` or `brew install uv`)
- A PyPI account with a project API token
- A git tag on the commit to release (`vX.Y.Z`)

---

## 1. Configure PyPI credentials

**Option A — environment variable (recommended for CI)**:
```bash
export UV_PUBLISH_TOKEN=pypi-xxxxxxxxxxxx
```

**Option B — ~/.netrc (recommended for local)**:
```
machine upload.pypi.org
  login __token__
  password pypi-xxxxxxxxxxxx
```

---

## 2. Tag the release

Version is derived automatically from the most recent git tag via `uv-dynamic-versioning`.

```bash
git tag v0.1.0
git push origin v0.1.0
```

---

## 3. Build the distribution artifacts

```bash
uv build
```

Expected output in `dist/`:
```
dist/
├── scaffold_ca_python-0.1.0-py3-none-any.whl
└── scaffold_ca_python-0.1.0.tar.gz
```

Verify the wheel contents include templates:
```bash
unzip -l dist/scaffold_ca_python-*.whl | grep templates | head -5
```

---

## 4. (Optional) Test against TestPyPI first

```bash
uv publish --index https://test.pypi.org/legacy/
```

Then verify installation from TestPyPI:
```bash
pip install --index-url https://test.pypi.org/simple/ scaffold-ca-python
scaffold --help
```

---

## 5. Publish to PyPI

```bash
uv publish
```

After upload, the package is available at:
```
https://pypi.org/project/scaffold-ca-python/
```

---

## 6. Verify installation from PyPI

```bash
python -m venv /tmp/verify-env
source /tmp/verify-env/bin/activate
pip install scaffold-ca-python
scaffold --help
scaffold ca --name my-test-project
deactivate
rm -rf /tmp/verify-env
```

---

## Development build (without tagging)

Running `uv build` without a clean git tag produces a dev version (e.g., `0.0.1.dev3+ga4f2bb8`).
This is expected and useful for local testing; do NOT publish dev versions to PyPI.

---

## Cleaning build artifacts

```bash
rm -rf dist/
```

Add `dist/` to `.gitignore` if not already present:
```bash
echo "dist/" >> .gitignore
```
