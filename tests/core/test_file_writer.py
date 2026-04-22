"""Tests for FileWriter: atomic writes, dry-run, delete, rollback (T019)."""

from pathlib import Path

import pytest

from scaffold_ca_python.core.file_writer import FileWriter
from scaffold_ca_python.models.file_operation import CreateFile, DeleteFile, GeneratedFile, InsertAfter

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_op(path: Path, content: str = "# generated") -> CreateFile:
    gf = GeneratedFile(path=path, content=content, template_name="test.j2")
    return CreateFile(file=gf)


def _delete_op(path: Path) -> DeleteFile:
    return DeleteFile(path=path)


# ---------------------------------------------------------------------------
# Real-mode creation
# ---------------------------------------------------------------------------


def test_creates_file_on_disk(tmp_path: Path) -> None:
    target = tmp_path / "output.py"
    writer = FileWriter()
    writer.execute([_create_op(target)], dry_run=False)
    assert target.exists()
    assert target.read_text() == "# generated"


def test_creates_parent_directories(tmp_path: Path) -> None:
    target = tmp_path / "deep" / "nested" / "module.py"
    writer = FileWriter()
    writer.execute([_create_op(target)], dry_run=False)
    assert target.exists()


def test_creates_multiple_files_atomically(tmp_path: Path) -> None:
    files = [_create_op(tmp_path / f"file{i}.py") for i in range(3)]
    writer = FileWriter()
    writer.execute(files, dry_run=False)
    for i in range(3):
        assert (tmp_path / f"file{i}.py").exists()


# ---------------------------------------------------------------------------
# Dry-run mode
# ---------------------------------------------------------------------------


def test_dry_run_does_not_write_files(tmp_path: Path) -> None:
    target = tmp_path / "should_not_exist.py"
    writer = FileWriter()
    writer.execute([_create_op(target)], dry_run=True)
    assert not target.exists()


def test_dry_run_returns_preview_paths(tmp_path: Path) -> None:
    target = tmp_path / "preview.py"
    writer = FileWriter()
    result = writer.execute([_create_op(target)], dry_run=True)
    assert any(str(target) in str(r) for r in result)


# ---------------------------------------------------------------------------
# Delete operations
# ---------------------------------------------------------------------------


def test_delete_removes_existing_file(tmp_path: Path) -> None:
    target = tmp_path / "to_delete.py"
    target.write_text("# delete me")
    writer = FileWriter()
    writer.execute([_delete_op(target)], dry_run=False)
    assert not target.exists()


def test_delete_nonexistent_file_is_noop(tmp_path: Path) -> None:
    target = tmp_path / "does_not_exist.py"
    writer = FileWriter()
    # should not raise
    writer.execute([_delete_op(target)], dry_run=False)


def test_delete_dry_run_does_not_remove_file(tmp_path: Path) -> None:
    target = tmp_path / "keep_this.py"
    target.write_text("# keep")
    writer = FileWriter()
    writer.execute([_delete_op(target)], dry_run=True)
    assert target.exists()


# ---------------------------------------------------------------------------
# Rollback on error
# ---------------------------------------------------------------------------


def test_no_partial_files_on_failure(tmp_path: Path) -> None:
    """If one file in a batch has an unwritable parent, no files should be committed."""
    good = tmp_path / "good.py"
    # Create a file where a directory is needed (so mkdir will fail)
    blocker_file = tmp_path / "blocker"
    blocker_file.write_text("I am a file, not a dir")
    bad = blocker_file / "nested.py"  # parent is a file → mkdir fails

    writer = FileWriter()
    with pytest.raises(Exception):
        writer.execute([_create_op(good), _create_op(bad)], dry_run=False)

    # The good file should NOT be left behind (atomicity)
    assert not good.exists()


# ---------------------------------------------------------------------------
# overwrite flag
# ---------------------------------------------------------------------------


def _create_op_overwrite(path: Path, content: str = "# new") -> CreateFile:
    gf = GeneratedFile(path=path, content=content, template_name="test.j2", overwrite=True)
    return CreateFile(file=gf)


def test_overwrite_true_replaces_existing_file(tmp_path: Path) -> None:
    target = tmp_path / "main.py"
    target.write_text("# original")

    writer = FileWriter()
    writer.execute([_create_op_overwrite(target, "# replaced")], dry_run=False)

    assert target.read_text() == "# replaced"


def test_overwrite_false_raises_on_existing_file(tmp_path: Path) -> None:
    target = tmp_path / "existing.py"
    target.write_text("# original")

    writer = FileWriter()
    with pytest.raises(FileExistsError):
        writer.execute([_create_op(target)], dry_run=False)


def test_overwrite_false_does_not_raise_when_file_absent(tmp_path: Path) -> None:
    target = tmp_path / "new.py"
    writer = FileWriter()
    writer.execute([_create_op(target)], dry_run=False)
    assert target.exists()


def test_overwrite_true_creates_parent_dirs(tmp_path: Path) -> None:
    target = tmp_path / "deep" / "nested" / "main.py"
    writer = FileWriter()
    writer.execute([_create_op_overwrite(target, "# hello")], dry_run=False)
    assert target.read_text() == "# hello"


def test_overwrite_dry_run_does_not_write(tmp_path: Path) -> None:
    target = tmp_path / "main.py"
    target.write_text("# original")

    writer = FileWriter()
    writer.execute([_create_op_overwrite(target, "# replaced")], dry_run=True)

    assert target.read_text() == "# original"


# ---------------------------------------------------------------------------
# insert_after
# ---------------------------------------------------------------------------


def _insert_op(path: Path, anchor: str, content: str) -> InsertAfter:
    return InsertAfter(path=path, anchor=anchor, content=content)


def test_insert_after_adds_content_below_anchor_line(tmp_path: Path) -> None:
    target = tmp_path / "config.py"
    target.write_text('class Settings:\n    ENV: str = "dev"\n    LOG_LEVEL: str = "INFO"\n')
    writer = FileWriter()
    writer.execute([_insert_op(target, "LOG_LEVEL", '    HOST: str = "0.0.0.0"\n    PORT: int = 8000')])

    result = target.read_text()
    lines = result.splitlines()
    log_idx = next(i for i, line in enumerate(lines) if "LOG_LEVEL" in line)
    assert "HOST" in lines[log_idx + 1]
    assert "PORT" in lines[log_idx + 2]


def test_insert_after_anchor_not_found_raises(tmp_path: Path) -> None:
    target = tmp_path / "config.py"
    target.write_text("x = 1\n")
    writer = FileWriter()
    with pytest.raises(ValueError, match="anchor"):
        writer.execute([_insert_op(target, "MISSING_ANCHOR", "y = 2")])


def test_insert_after_file_not_found_raises(tmp_path: Path) -> None:
    target = tmp_path / "nonexistent.py"
    writer = FileWriter()
    with pytest.raises(FileNotFoundError):
        writer.execute([_insert_op(target, "x", "y = 2")])


def test_insert_after_dry_run_returns_path_without_modifying(tmp_path: Path) -> None:
    target = tmp_path / "config.py"
    original = 'LOG_LEVEL: str = "INFO"\n'
    target.write_text(original)
    writer = FileWriter()
    result = writer.execute([_insert_op(target, "LOG_LEVEL", 'HOST: str = "0.0.0.0"')], dry_run=True)

    assert target in result
    assert target.read_text() == original


def test_insert_after_inserts_at_first_occurrence_only(tmp_path: Path) -> None:
    target = tmp_path / "dup.py"
    target.write_text("LOG_LEVEL = 1\nLOG_LEVEL = 2\n")
    writer = FileWriter()
    writer.execute([_insert_op(target, "LOG_LEVEL", "INSERTED = True")])

    lines = target.read_text().splitlines()
    assert lines[1] == "INSERTED = True"
    # second LOG_LEVEL is now at index 2; no second insertion
    assert lines.count("INSERTED = True") == 1
