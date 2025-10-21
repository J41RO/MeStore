"""
Project-specific site customizations executed automatically when Python starts.

We make sure the repository's local `bin` directory is added to PATH so that
test helpers like the Alembic shim are discoverable during subprocess calls.
"""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
LOCAL_BIN_DIRS = [
    PROJECT_ROOT / "bin",
    PROJECT_ROOT / "scripts/bin",
]


def _ensure_local_bins_on_path() -> None:
    """Prepend local bin directories to PATH once per interpreter session."""
    current_path = os.environ.get("PATH", "")
    path_parts = current_path.split(os.pathsep) if current_path else []

    updated = False
    for bin_path in LOCAL_BIN_DIRS:
        if bin_path.exists():
            bin_str = str(bin_path)
            if bin_str not in path_parts:
                path_parts.insert(0, bin_str)
                updated = True

    if updated:
        os.environ["PATH"] = os.pathsep.join(path_parts)


_ensure_local_bins_on_path()

