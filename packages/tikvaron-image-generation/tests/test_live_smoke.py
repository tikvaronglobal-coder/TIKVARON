from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import live_smoke  # noqa: E402


def test_live_smoke_blocks_without_api_key(monkeypatch, capsys, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("TIKVARON_IMAGE_SMOKE_OUTPUT", str(tmp_path / "smoke.png"))

    class ForbiddenClient:
        def __init__(self):
            raise AssertionError("client must not be initialized without the API key")

    monkeypatch.setattr(live_smoke, "ImageGenerationClient", ForbiddenClient)

    exit_code = live_smoke.main()

    assert exit_code == 2
    assert json.loads(capsys.readouterr().err)["status"] == "blocked"


def test_live_smoke_generates_one_artifact_when_opted_in(monkeypatch, capsys, tmp_path):
    output = tmp_path / "live.png"
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("TIKVARON_IMAGE_SMOKE_OUTPUT", str(output))

    class FakeClient:
        def generate(self, prompt, output_path, **kwargs):
            Path(output_path).write_bytes(b"test-image")
            return SimpleNamespace(
                paths=(Path(output_path),),
                model="gpt-image-2.5-sunburst",
                response_id=None,
                partial_paths=(),
            )

    monkeypatch.setattr(live_smoke, "ImageGenerationClient", FakeClient)

    exit_code = live_smoke.main()

    record = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output.read_bytes() == b"test-image"
    assert record["status"] == "passed"
    assert record["paths"] == [str(output)]
