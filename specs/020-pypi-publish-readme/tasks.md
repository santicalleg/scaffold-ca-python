# Tasks: PyPI Publishing & README Documentation

**Branch**: `020-pypi-publish-readme`
**Input**: Design documents from `/specs/020-pypi-publish-readme/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/readme-outline.md ✅, quickstart.md ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.
**Tests**: No new test files — this feature contains no logic changes. Smoke-test tasks validate build output.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup

**Purpose**: Verify the repository baseline before making any changes.

- [X] T001 Verify `LICENSE` file exists at repo root with MIT text (file: `LICENSE`)
- [X] T002 [P] Add `dist/` to `.gitignore` if not already present (file: `.gitignore`)

**Checkpoint**: Repo baseline confirmed — ready for user story work.

---

## Phase 2: User Story 1 — Publishable PyPI package (Priority: P1) 🎯 MVP

**Goal**: `pyproject.toml` satisfies all PyPI metadata requirements so that `uv build` produces a valid, uploadable wheel and sdist.

**Independent Test**: Run `uv build` from the project root; confirm `dist/*.whl` and `dist/*.tar.gz` are produced; run `pip install dist/*.whl` in a clean venv and verify `scaffold --help` works.

### Implementation for User Story 1

- [X] T003 [US1] Add `license = "MIT"` field to `[project]` table in `pyproject.toml`
- [X] T004 [P] [US1] Add `keywords` list to `[project]` table in `pyproject.toml` (values from data-model.md §1)
- [X] T005 [P] [US1] Add `classifiers` list to `[project]` table in `pyproject.toml` (10 Trove classifiers from data-model.md §1)
- [X] T006 [P] [US1] Update `authors` entry to add `name = "Santiago Callegari"` alongside existing email in `pyproject.toml`
- [X] T007 [US1] Add `[project.urls]` table with `Homepage`, `Repository`, and `Issues` keys to `pyproject.toml` (URLs from data-model.md §2)
- [X] T008 [US1] Smoke-test: run `uv build` and confirm `dist/scaffold_ca_python-*.whl` and `dist/scaffold_ca_python-*.tar.gz` are produced

**Checkpoint**: US1 done — `pyproject.toml` is PyPI-ready and `uv build` produces valid artifacts.

---

## Phase 3: User Story 2 — Complete, reader-friendly README (Priority: P2)

**Goal**: `README.md` is fully rewritten with all 9 required sections so a new developer can onboard in ≤5 minutes.

**Independent Test**: Open `README.md` in a Markdown viewer; confirm all 9 sections are present; confirm each command sub-section has a fenced `bash` example; confirm all badge URLs are absolute.

### Implementation for User Story 2

- [X] T009 [US2] Write Section 1 (title + badges) in `README.md` — H1 heading + PyPI version badge + Python badge + MIT license badge (absolute Shields.io URLs)
- [X] T010 [US2] Write Section 2 ("What is this?") in `README.md` — 2–4 sentences covering Clean Architecture, Python, CLI code scaffolding (no framework names)
- [X] T011 [US2] Write Section 3 ("Installation") in `README.md` — `pip install scaffold-ca-python` and `uv add scaffold-ca-python` fenced blocks + Python ≥3.13 note
- [X] T012 [US2] Write Section 4 ("Quick Start") in `README.md` — numbered 4-step walkthrough: install → `scaffold ca --name my-app` → `scaffold gm --name Order` → `scaffold vs`
- [X] T013 [US2] Write Section 5 ("Commands & Examples") in `README.md` — 10 `###` sub-sections (ca, gm, guc, gda, gep, gh, gpipe, vs, dm, up) each with description + fenced `bash` example per contracts/readme-outline.md
- [X] T014 [P] [US2] Write Section 6 ("Technologies") in `README.md` — Markdown table (Tool/Library | Version | Role) with all 11 entries from data-model.md §3
- [X] T015 [P] [US2] Write Section 7 ("Current Features") in `README.md` — bullet list covering all 10 commands, `--dry-run`, Jinja2 templates, Pydantic v2, Rich output, mypy strict, ruff, 80%+ coverage gate
- [X] T016 [US2] Write Section 8 ("Contributing") in `README.md` — numbered 8-step guide (fork → clone → `uv sync` → branch → `uv run pytest` → ruff → mypy → PR) per contracts/readme-outline.md §8
- [X] T017 [P] [US2] Write Section 9 ("License") in `README.md` — one-liner "MIT License" + link to `LICENSE` file
- [X] T018 [US2] Validate README renders correctly: check all badge URLs are absolute, no relative image links, all code blocks have language identifiers

**Checkpoint**: US2 done — README covers all 9 required sections per spec FR-005/FR-006.

---

## Phase 4: User Story 3 — Maintainer publish workflow (Priority: P3)

**Goal**: The `quickstart.md` build/publish workflow (already documented in the spec artifact) is validated end-to-end, and `dist/` hygiene is confirmed.

**Independent Test**: Follow steps in `specs/020-pypi-publish-readme/quickstart.md`; confirm `uv build` produces correct version from a git tag; confirm `dist/` is in `.gitignore`.

### Implementation for User Story 3

- [X] T019 [US3] Verify `dist/` appears in `.gitignore` (confirm T002 result)
- [X] T020 [US3] Smoke-test wheel contents: run `unzip -l dist/scaffold_ca_python-*.whl | grep templates` to confirm templates are bundled (FR-003)
- [X] T021 [US3] Verify existing tests still pass after `pyproject.toml` changes: run `uv run pytest --tb=short`
- [X] T021b [US3] Smoke-test clean-venv install (SC-002): `python -m venv /tmp/scaffold-test-env && /tmp/scaffold-test-env/bin/pip install dist/scaffold_ca_python-*.whl && /tmp/scaffold-test-env/bin/scaffold --help && rm -rf /tmp/scaffold-test-env`

**Checkpoint**: US3 done — build artifacts are valid, templates are bundled, test suite is green.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency checks across both modified files.

- [X] T022 [P] Cross-check: confirm `license` SPDX value in `pyproject.toml` (`"MIT"`) matches the Trove classifier (`License :: OSI Approved :: MIT License`) and the `LICENSE` file header
- [X] T023 [P] Cross-check: confirm `[project.urls]` Repository URL in `pyproject.toml` matches the GitHub link used in README badges and Contributing section
- [X] T024 Run `uv run ruff check src/ tests/` to confirm no ruff violations were introduced by any incidental edits
- [X] T025 Run full build smoke-test one final time: `uv build && ls -lh dist/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (US1)**: Depends on Phase 1 (T001, T002 complete); T003–T007 can run in parallel; T008 depends on T003–T007
- **Phase 3 (US2)**: Independent of Phase 2 (different file: README.md); T009–T013 sequential within the section; T014/T015/T017 parallel; T016 sequential; T018 depends on T009–T017
- **Phase 4 (US3)**: Depends on Phase 2 (T008) and Phase 3 (T018)
- **Phase 5 (Polish)**: Depends on all prior phases

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 1; no dependency on US2 or US3
- **US2 (P2)**: Starts after Phase 1; independent of US1 (different file)
- **US3 (P3)**: Depends on US1 (build artifacts) and implicitly US2 (README already done)

### Parallel Opportunities

US1 and US2 can be worked in parallel (they touch different files):

```
Phase 1 (T001, T002)
     |
     +---- Phase 2 US1: T003 → T004/T005/T006 [parallel] → T007 → T008
     |
     +---- Phase 3 US2: T009 → T010 → T011 → T012 → T013 → T014/T015/T017 [parallel] → T016 → T018
     |
Phase 4 US3 (T019, T020, T021) ← after T008 + T018
     |
Phase 5 Polish (T022–T025)
```

---

## Implementation Strategy

**MVP (recommended first)**: Complete Phase 2 (US1) — it unblocks PyPI publishing immediately with minimal effort (4 field additions to `pyproject.toml`). Then Phase 3 (US2) for full README.

**Suggested task order for solo execution**:
1. T001, T002 (setup — 2 min)
2. T003 → T006 in parallel → T007 → T008 (pyproject.toml fields + build smoke-test — 10 min)
3. T009 → T018 (README rewrite — 30–45 min)
4. T019 → T021 (validation — 5 min)
5. T022 → T025 (polish — 5 min)

**Total estimate**: ~55–65 minutes
