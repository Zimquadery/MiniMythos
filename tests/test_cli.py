from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from minimythos.cli import main


def test_help_exits_cleanly(capsys: pytest.CaptureFixture[str]):
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0


def test_default_target_uses_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "main.py").write_text("pass")
    with patch("minimythos.cli.scan") as mock_scan:
        main([])
    mock_scan.assert_called_once()
    assert mock_scan.call_args.kwargs["target"] == tmp_path.resolve()


def test_explicit_target(tmp_path: Path):
    fake_target = tmp_path / "project"
    fake_target.mkdir()
    (fake_target / "main.py").write_text("pass")
    with patch("minimythos.cli.scan") as mock_scan:
        main([str(fake_target)])
    assert mock_scan.call_args.kwargs["target"] == fake_target.resolve()


def test_nonexistent_target_exits():
    with pytest.raises(SystemExit):
        main(["/nonexistent/path/xyz123"])


def test_options_forwarded(tmp_path: Path):
    fake_target = tmp_path / "project"
    fake_target.mkdir()
    (fake_target / "main.py").write_text("pass")
    with patch("minimythos.cli.scan") as mock_scan:
        main(
            [
                str(fake_target),
                "--agent",
                "echo",
                "--batch-size",
                "5",
                "--threshold",
                "8",
                "--max-parallel",
                "2",
                "--output",
                str(tmp_path / "out"),
            ]
        )
    kwargs = mock_scan.call_args.kwargs
    assert kwargs["agent"] == "echo"
    assert kwargs["batch_size"] == 5
    assert kwargs["threshold"] == 8
    assert kwargs["max_parallel"] == 2
    assert kwargs["output"] == (tmp_path / "out").resolve()
