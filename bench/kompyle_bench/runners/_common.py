# Copyright (c) 2026 Ibrahim El Kaddouri
# Licensed under apachev2
"""Helpers used by more than one runner."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def skip_if_exists(out: Path) -> bool:
    """Print a ``[skip]`` message and return ``True`` if ``out`` already exists."""
    if out.exists():
        print(f"[skip] {out}")
        return True
    return False


def load_compile_result(cp: Path) -> Optional[dict]:
    """Load a prior compile result, print and return ``None`` if missing or
    if the compile recorded an error / timeout.

    Both downstream stages (infer, experiment) gate on having a successful
    compile, so this consolidates the boilerplate.
    """
    if not cp.exists():
        print(f"[skip] no compile result: {cp}")
        return None
    cr = json.loads(cp.read_text())
    if cr.get("compile_s") is None:
        print(f"[skip] compile timed-out or errored: {cp}")
        return None
    return cr


def write_json(out: Path, payload: dict) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2))
