from pydantic import BaseModel
from pathlib import Path


class Settings(BaseModel):
    model_config = {"frozen": True}

    target_path: Path
    agent_command: str | list[str]
    batch_size: int = 10
    max_parallel_agents: int = 5
    score_threshold: int = 7
    worktree_base: Path | None = None
    output_dir: Path | None = None
