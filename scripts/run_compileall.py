"""Utility script to compile the extracao package to bytecode.

This mirrors running ``python -m compileall extracao`` from the
repository root, which is useful for a quick syntax check without
executing the application. Running the script avoids having to
remember the exact command.
"""

from __future__ import annotations

import compileall
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    extracao_path = repo_root / "extracao"
    if not extracao_path.exists():
        raise SystemExit(
            "The 'extracao' package was not found. Run this script from inside the repository."
        )

    success = compileall.compile_dir(str(extracao_path), quiet=1)
    if not success:
        raise SystemExit("Compilation failed. Check the log above for syntax errors.")

    print("Successfully compiled 'extracao' package.")


if __name__ == "__main__":
    main()
