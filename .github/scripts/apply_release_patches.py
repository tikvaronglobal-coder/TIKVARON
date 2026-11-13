"""Apply small, explicit deployment fixes to the pinned v0.2.0 source bundle.

The source ZIP remains byte-for-byte pinned. Every overlay is checked for the
expected pre-image and exact replacement count so drift fails the workflow.
"""
from __future__ import annotations

import argparse
from pathlib import Path

PATCHES = (
    (
        "src/tikvaron_engineering/dependency_intelligence.py",
        "for index, row in zip(pending, page_rows):",
        "for index, row in zip(pending, page_rows, strict=True):",
    ),
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release_dir", type=Path)
    root = parser.parse_args().release_dir.resolve()
    for relative, before, after in PATCHES:
        target = root / relative
        if not target.is_file():
            raise SystemExit(f"release overlay target missing: {relative}")
        source = target.read_text(encoding="utf-8")
        count = source.count(before)
        if count != 1:
            raise SystemExit(
                f"release overlay expected exactly one target in {relative}; found {count}"
            )
        target.write_text(source.replace(before, after, 1), encoding="utf-8")
        print(f"Applied validated release overlay: {relative}")


if __name__ == "__main__":
    main()
