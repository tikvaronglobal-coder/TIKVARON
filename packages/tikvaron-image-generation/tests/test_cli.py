from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from tikvaron_image_generation import cli


class FakeGenerator:
    def __init__(self):
        self.calls = []

    def generate(self, *args, **kwargs):
        self.calls.append(("generate", args, kwargs))
        return SimpleNamespace(paths=(Path(args[1]),), partial_paths=(), model="gpt-image-2.5-sunburst", response_id=None)

    def edit(self, *args, **kwargs):
        self.calls.append(("edit", args, kwargs))
        return SimpleNamespace(paths=(Path(args[2]),), partial_paths=(), model="gpt-image-2.5-sunburst", response_id=None)

    def stream_with_images(self, *args, **kwargs):
        self.calls.append(("stream-images", args, kwargs))
        return SimpleNamespace(paths=(), partial_paths=(Path("preview.png"),), model="gpt-image-2.5-sunburst", response_id=None)

    def upload_vision_file(self, path):
        self.calls.append(("upload", (Path(path),), {}))
        return "file_cli"

    def generate_with_responses(self, *args, **kwargs):
        self.calls.append(("respond", args, kwargs))
        return SimpleNamespace(paths=(Path(args[1]),), partial_paths=(), model="gpt-6-astra", response_id="resp_cli")

    def stream_with_responses(self, *args, **kwargs):
        self.calls.append(("stream", args, kwargs))
        return SimpleNamespace(paths=(Path(args[1]),), partial_paths=(Path("preview.png"),), model="gpt-6-astra", response_id="resp_stream")


def install_fake(monkeypatch):
    fake = FakeGenerator()
    monkeypatch.setattr(cli, "ImageGenerationClient", lambda: fake)
    return fake


def test_generate_command_prints_metadata_without_base64(monkeypatch, capsys, tmp_path):
    fake = install_fake(monkeypatch)
    output = tmp_path / "art.png"
    code = cli.main(["generate", "--prompt", "A little otter", "--output", str(output)])
    record = json.loads(capsys.readouterr().out)
    assert code == 0
    assert fake.calls[0][0] == "generate"
    assert record["paths"] == [str(output)]
    assert "base64" not in record


def test_edit_command_passes_all_reference_images(monkeypatch, tmp_path):
    fake = install_fake(monkeypatch)
    first = tmp_path / "one.png"
    second = tmp_path / "two.png"
    output = tmp_path / "result.png"
    code = cli.main(["edit", "--prompt", "Combine", "--image", str(first), "--image", str(second), "--output", str(output)])
    assert code == 0
    assert fake.calls[0][0] == "edit"
    assert fake.calls[0][1][1] == [first, second]


def test_responses_command_passes_previous_response_id(monkeypatch, capsys, tmp_path):
    fake = install_fake(monkeypatch)
    code = cli.main(["respond", "--prompt", "Make realistic", "--output", str(tmp_path / "out.png"), "--previous-response-id", "resp_old", "--action", "edit"])
    record = json.loads(capsys.readouterr().out)
    assert code == 0
    assert fake.calls[0][2]["previous_response_id"] == "resp_old"
    assert record["response_id"] == "resp_cli"


def test_responses_stream_passes_partial_image_count(monkeypatch, tmp_path):
    fake = install_fake(monkeypatch)
    cli.main(["stream", "--prompt", "Winter river", "--output", str(tmp_path / "out.png"), "--partial-images", "3"])
    assert fake.calls[0][0] == "stream"
    assert fake.calls[0][2]["partial_images"] == 3


def test_images_stream_command_passes_partial_image_count(monkeypatch, tmp_path):
    fake = install_fake(monkeypatch)
    cli.main(["stream-images", "--prompt", "Winter river", "--output", str(tmp_path / "out.png"), "--partial-images", "1"])
    assert fake.calls[0][0] == "stream-images"
    assert fake.calls[0][2]["partial_images"] == 1


def test_responses_command_passes_reference_paths_file_ids_and_mask(monkeypatch, tmp_path):
    fake = install_fake(monkeypatch)
    reference = tmp_path / "reference.png"
    cli.main(["respond", "--prompt", "Use references", "--output", str(tmp_path / "basket.png"), "--action", "edit", "--reference-image", str(reference), "--reference-file-id", "file_existing", "--mask-file-id", "file_mask"])
    options = fake.calls[0][2]
    assert options["reference_images"] == [reference]
    assert options["reference_file_ids"] == ["file_existing"]
    assert options["mask_file_id"] == "file_mask"


def test_upload_command_prints_file_id_as_json(monkeypatch, capsys, tmp_path):
    fake = install_fake(monkeypatch)
    image = tmp_path / "reference.png"
    code = cli.main(["upload", "--image", str(image)])
    record = json.loads(capsys.readouterr().out)
    assert code == 0
    assert record["file_id"] == "file_cli"
    assert fake.calls[0][0] == "upload"
