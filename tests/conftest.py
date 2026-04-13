import json
import sys
from pathlib import Path
import pytest
from minimythos.config import Settings

FAKE_AGENT = str(Path(__file__).parent / "helpers" / "fake_agent.py")


@pytest.fixture
def tmp_codebase(tmp_path: Path) -> Path:
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("print('hello')")
    (src / "utils.py").write_text("def add(a, b): return a + b")
    (src / "auth.py").write_text("password = 'hardcoded'")
    (tmp_path / "README.md").write_text("# test project")
    return tmp_path


@pytest.fixture
def default_settings(tmp_codebase: Path, tmp_path: Path) -> Settings:
    return Settings(
        target_path=tmp_codebase,
        agent_command=[sys.executable, FAKE_AGENT],
        batch_size=10,
        max_parallel_agents=2,
        score_threshold=7,
        output_dir=tmp_path / "output",
    )
