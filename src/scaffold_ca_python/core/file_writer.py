"""file_writer: atomic file creation and deletion using tempdir staging (T023)."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from scaffold_ca_python.models.file_operation import CreateFile, DeleteFile, FileOperation

if TYPE_CHECKING:
    pass


class FileWriter:
    """Execute a list of :class:`FileOperation` objects.

    Real mode:  Uses a temporary directory for staging, then ``os.replace()``
                (atomic on POSIX) to commit every file.  If staging fails for
                *any* file the temp directory is discarded and no partial writes
                reach the target tree.

    Dry-run mode: Returns a list of target :class:`Path` objects that *would*
                  be created or deleted, without touching disk.
    """

    def execute(
        self,
        operations: list[FileOperation],
        *,
        dry_run: bool = False,
    ) -> list[Path]:
        """Execute *operations*.

        Parameters
        ----------
        operations:
            Sequence of :class:`CreateFile` or :class:`DeleteFile` operations.
        dry_run:
            When ``True`` no disk writes occur; the method returns the list of
            paths that *would* be affected.

        Returns
        -------
        list[Path]
            In dry-run mode: the paths that would be written/deleted.
            In real mode: the paths that were successfully written.
        """
        if dry_run:
            return self._dry_run(operations)
        return self._commit(operations)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _dry_run(self, operations: list[FileOperation]) -> list[Path]:
        result: list[Path] = []
        for op in operations:
            if isinstance(op, CreateFile):
                result.append(op.file.path)
            elif isinstance(op, DeleteFile):
                result.append(op.path)
        return result

    def _commit(self, operations: list[FileOperation]) -> list[Path]:
        """Stage all creates in a temp dir, then commit atomically."""
        creates: list[CreateFile] = []
        deletes: list[DeleteFile] = []
        for op in operations:
            if isinstance(op, CreateFile):
                creates.append(op)
            elif isinstance(op, DeleteFile):
                deletes.append(op)

        committed: list[Path] = []

        with tempfile.TemporaryDirectory() as tmpdir:
            # Stage all created files — any error here rolls back automatically
            # because the TemporaryDirectory is discarded on __exit__.
            staged: list[tuple[Path, Path]] = []
            for i, op in enumerate(creates):
                tmp_file = Path(tmpdir) / f"staged_{i}"
                tmp_file.write_text(op.file.content, encoding="utf-8")
                staged.append((tmp_file, op.file.path))

            # Pre-flight: create ALL parent directories before any os.replace().
            # If any mkdir fails, the exception propagates here; the TemporaryDirectory
            # is cleaned up on __exit__ and no target files are committed yet.
            for _, target in staged:
                target.parent.mkdir(parents=True, exist_ok=True)

            # All parents exist — commit via os.replace (atomic on POSIX)
            for tmp_file, target in staged:
                os.replace(tmp_file, target)
                committed.append(target)

        # Process deletes after all creates are committed
        for op in deletes:
            if op.path.exists():
                op.path.unlink()

        return committed
