#!/usr/bin/env python3
"""Reassemble the committed TIKVARON CBOS HTML source segments."""
from pathlib import Path
HERE = Path(__file__).resolve().parent
PARTS = sorted((HERE / "source").glob("TIKVARON_Business_Systems_Register.part-*"))
if len(PARTS) != 8:
    raise SystemExit(f"Expected 8 source segments; found {len(PARTS)}")
output = HERE / "TIKVARON_Business_Systems_Register.html"
output.write_text("".join(p.read_text(encoding="utf-8") for p in PARTS), encoding="utf-8")
print(f"Reassembled {len(PARTS)} segments into {output} ({output.stat().st_size} bytes)")
