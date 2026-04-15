from pathlib import Path
import pytest
from minimythos.utils.files import discover_code_files, batch_files, group_by_directory
from minimythos.utils.json_utils import parse_json_output


def test_discover_finds_code_files(tmp_path: Path):
    (tmp_path / "main.py").write_text("pass")
    (tmp_path / "utils.js").write_text("pass")
    (tmp_path / "README.md").write_text("readme")
    files = discover_code_files(tmp_path)
    names = [f.name for f in files]
    assert "main.py" in names
    assert "utils.js" in names
    assert "README.md" in names


def test_discover_skips_binary_extensions(tmp_path: Path):
    (tmp_path / "image.png").write_bytes(b"\x89PNG")
    (tmp_path / "archive.zip").write_bytes(b"PK")
    (tmp_path / "code.py").write_text("pass")
    files = discover_code_files(tmp_path)
    names = [f.name for f in files]
    assert "code.py" in names
    assert "image.png" not in names
    assert "archive.zip" not in names


def test_discover_skips_skip_dirs(tmp_path: Path):
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "cached.pyc").write_text("bytecode")
    (tmp_path / "app.py").write_text("pass")
    files = discover_code_files(tmp_path)
    names = [f.name for f in files]
    assert "app.py" in names
    assert "cached.pyc" not in names


def test_discover_skips_git(tmp_path: Path):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("gitconfig")
    (tmp_path / "main.py").write_text("pass")
    files = discover_code_files(tmp_path)
    assert all(".git" not in str(p) for p in files)


def test_discover_skips_node_modules(tmp_path: Path):
    nm = tmp_path / "node_modules"
    nm.mkdir()
    (nm / "lib.js").write_text("lib")
    (tmp_path / "index.js").write_text("entry")
    files = discover_code_files(tmp_path)
    names = [f.name for f in files]
    assert "index.js" in names
    assert "lib.js" not in names


def test_discover_nested_dirs(tmp_path: Path):
    sub = tmp_path / "src" / "deep"
    sub.mkdir(parents=True)
    (sub / "module.py").write_text("pass")
    (tmp_path / "root.py").write_text("pass")
    files = discover_code_files(tmp_path)
    assert len(files) == 2


def test_group_by_directory(tmp_path: Path):
    files = [
        Path("src/a.py"),
        Path("src/b.py"),
        Path("tests/test_a.py"),
    ]
    groups = group_by_directory(files)
    assert Path("src") in groups
    assert Path("tests") in groups
    assert len(groups[Path("src")]) == 2
    assert len(groups[Path("tests")]) == 1


def test_batch_files_respects_batch_size():
    files = [Path(f"dir/file_{i}.py") for i in range(25)]
    batches = batch_files(files, 10)
    assert len(batches) == 3
    assert len(batches[0]) == 10
    assert len(batches[1]) == 10
    assert len(batches[2]) == 5


def test_parse_json_raw():
    assert parse_json_output('[{"a": 1}]') == [{"a": 1}]


def test_parse_json_markdown_fences():
    raw = '```json\n[{"a": 1}]\n```'
    assert parse_json_output(raw) == [{"a": 1}]


def test_parse_json_surrounding_text():
    raw = 'Here is the result:\n[{"a": 1}]\nDone.'
    assert parse_json_output(raw) == [{"a": 1}]


def test_parse_json_object():
    raw = '```json\n{"key": "value"}\n```'
    assert parse_json_output(raw) == {"key": "value"}


def test_parse_json_object_with_surrounding_text():
    raw = 'Some preamble\n{"key": "value"}\nSome postamble'
    assert parse_json_output(raw) == {"key": "value"}


def test_parse_json_output_handles_fences():
    raw = '```json\n[{"path": "a.py", "score": 5, "reason": "ok"}]\n```'
    result = parse_json_output(raw)
    assert result[0]["score"] == 5


def test_parse_json_output_raises_on_garbage():
    import pytest

    with pytest.raises(Exception):
        parse_json_output("not json at all")
