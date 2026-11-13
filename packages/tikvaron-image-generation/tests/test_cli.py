from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from tikvaron_image_generation import cli


class FakeGenerator:
    def __init__(self, **kwargs):
        self.options = kwargs
        self.calls = []

    def generate(self, *args, **kwargs):
        self.calls.append(("generate", args, kwargs))
        return SimpleNamespace(
            paths=(Path(args[1]),),
            partial_paths=(),
            model="gpt-image-2.5-sunburst",
            response_id=None,
        )

    def edit(self, *args, **kwargs):
        self.calls.append(("edit", args, kwargs))
        return SimpleNamespace(
            paths=(Path(args[2]),),
            partial_paths=(),
            model="gpt-image-2.5-sunburst",
            response_id=None,
        )

    def stream_with_images(self, *args, **kwargs):
        self.calls.append(("stream-images", args, kwargs))
        return SimpleNamespace(
            paths=(), partial_paths=(Path("preview.png"),),
            model="gpt-image-2.5-sunburst", response_id=None
        )

    def upload_vision_file(self, file_path):
        self.calls.append(("upload", (Path(file_path),), {}))
        return "file_from_cli"

    def generate_with_responses(self, *args, **kwargs):
        self.calls.append(("respond", args, kwargs))
        return SimpleNamespace(
            paths=(Path(args[1]),), partial_paths=(), model="gpt-6-astra", response_id="resp_cli"
        )

    def stream_with_responses(self, *args, **kwargs):
        self.calls.append(("stream", args, kwargs))
        return SimpleNamespace(
            paths=(Path(args[1]),), partial_paths=(Path("preview.png"),),
            model="gpt-6-astra", response_id="resp_stream"
        )


def test_generate_command_prints_machine_readable_metadata(monkeypatch, capsys, tmp_path):
    fake = FakeGenerator()
    monkeypatch.setattr(cli, "ImageGenerationClient", lambda: fake)
    output = tmp_path / "art.png"

    exit_code = cli.main(["generate", "--prompt", "A little otter", "--output", str(output)])

    record = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert fake.calls[0][0] == "generate"
    assert record["paths"] == [str(output])
    assert "base64" not in record


def test_edit_command_accepts_multiple_reference_images(monkeypatch, tmp_path):
    fake = FakeGenerator()
    monkeypatch.setattr(cli, "ImageGenerationClient", lambda: fake)
    first = tmp_path / "one.png"
    second = tmp_path / "two.png"

    exit_code = cli.main([
        "edit", "--prompt", "Combine references", "--image", str(first),
        "--image", str(second), "--output", str(tmp_path / "result.png")
    ])

    assert exit_code == 0
    assert fake.calls[0][0] == "edit"
    assert fake.calls[0][1][1] == [first, second]


def test_respond_command_passes_previous_response_id(monkeypatch, capsys, tmp_path):
    fake = FakeGenerator()
    monkeypatch.setattr(cli, "ImageGenerationClient", lambda: fake)

    cli.main([
        "respond", "--prompt", "Make it realistic", "--output", str(tmp_path / "out.png"),
        "--previous-response-id", "resp_old", "--action", "edit"
    ])

    record = json.loads(capsys.readouterr().out)
    assert fake.calls[0][2]["previous_response_id"] == "resp_old"
    assert record["response_id"] == "resp_cli"


def test_stream_command_passes_partial_image_count(monkeypatch, tmp_path):
    fake = FakeGenerator()
    monkeypatch.setattr(cli, "ImageGenerationClient", lambda: fake)

    cli.main([
        "stream", "--prompt", "Winter river", "--output", str(tmp_path / "out.png"),
        "--partial-images", "3"
    ])

    assert fake.calls[0][2]["partial_images"] == 3


def test_images_stream_command_routes_partial_image_count(monkeypatch, tmp_path):
    fake = FakeGenerator()
    monkeypatch.setattr(cli, "ImageGenerationClient", lambda: fake)

    cli.main([
        "stream-images", "--prompt", "Winter river", "--output", str(tmp_path / "river.png"),
        "--partial-images", "1"
    ])

    assert fake.calls[0][0] == "stream-images"
    assert fake.calls[0][2]["partial_images"] == 1


def test_respond_command_passes_reference_images_file_ids_and_mask(monkeypatch, tmp_path):
    fake = FakeGenerator()
    monkeypatch.setattr(cli, "ImageGenerationClient", lambda: fake)
    local_reference = tmp_path / "reference.png"

    cli.main([
        "respond", "--prompt", "Use the product references",
        "--output", str(tmp_path / "basket.png"),
        "--action", "edit",
        "--reference-image", str(local_reference),
        "--reference-file-id", "file_existing",
        "--mask-file-id", "file_mask",
    ])

    kwargs = fake.calls[0][2]
    assert kwargs["reference_images"] == [local_reference]
    assert kwargs["reference_file_ids"] == ["file_existing"]
    assert kwargs["mask_file_id"] == "file_mask"


def test_upload_command_returns_file_id_as_json(monkeypatch, capsys, tmp_path):
    fake = FakeGenerator()
    monkeypatch.setattr(cli, "ImageGenerationClient", lambda: fake)

    exit_code = cli.main(["upload", "--image", str(tmp_path / "reference.png")])

    record = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert record["file_id"] == "file_from_cli"
    assert fake.calls[0][0] == "upload"
