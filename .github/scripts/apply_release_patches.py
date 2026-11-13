"""Apply explicit, validated overlays to the pinned v0.2.0 source bundle.

The source ZIP remains byte-for-byte pinned. Source replacements require an
exact pre-image match. The optional Responses API tools helper is copied from
the tracked repository script into the restored Python package.
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

    helper_source = Path(__file__).with_name("responses_tools.py")
    helper_target = root / "src/tikvaron_engineering/responses_tools.py"
    if not helper_source.is_file():
        raise SystemExit("Responses API tools overlay source is missing")
    if not (root / "src/tikvaron_engineering").is_dir():
        raise SystemExit("release overlay package directory is missing")
    helper_target.write_bytes(helper_source.read_bytes())
    print("Applied optional Responses API tools module: src/tikvaron_engineering/responses_tools.py")


if __name__ == "__main__":
    main()
