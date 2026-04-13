import json
import subprocess
from pathlib import Path
from minimythos.steps.base import Step
from minimythos.config import Settings
from minimythos.agents.runner import AgentRunner
from minimythos.utils.display import print_error
from minimythos.exceptions import PipelineAbort


def create_worktree(target_repo: Path, worktree_path: Path) -> bool:
    result = subprocess.run(
        ["git", "worktree", "add", str(worktree_path), "HEAD"],
        capture_output=True,
        text=True,
        cwd=str(target_repo),
    )
    return result.returncode == 0


def remove_worktree(target_repo: Path, worktree_path: Path) -> bool:
    result = subprocess.run(
        ["git", "worktree", "remove", str(worktree_path), "--force"],
        capture_output=True,
        text=True,
        cwd=str(target_repo),
    )
    return result.returncode == 0


class SelectStep(Step):
    """Select high-score files and create git worktrees."""

    @property
    def name(self) -> str:
        return "Select"

    async def run(self) -> None:
        output_dir = self.settings.output_dir or self.settings.target_path
        score_file = output_dir / "vulnerability_score.json"

        if not score_file.exists():
            raise PipelineAbort(
                "vulnerability_score.json not found — cannot select files"
            )

        data = json.loads(score_file.read_text())

        scored_files = []
        for batch in data["batches"]:
            for s in batch["scores"]:
                if s["score"] >= self.settings.score_threshold:
                    scored_files.append(s)

        if not scored_files:
            from minimythos.utils.display import console

            console.print(
                "[yellow]No files scored above threshold. Pipeline ending gracefully.[/yellow]"
            )
            (output_dir / "selected_files.json").write_text(json.dumps([], indent=2))
            return

        scored_files.sort(key=lambda x: x["score"], reverse=True)

        target = self.settings.target_path
        worktree_base = (
            self.settings.worktree_base or target.parent / "minimythos_worktrees"
        )
        worktree_base.mkdir(parents=True, exist_ok=True)

        selected = []
        for idx, entry in enumerate(scored_files):
            safe_name = entry["path"].replace("/", "_").replace("\\", "_")
            wt_path = worktree_base / f"minimythos_attack_{idx}_{safe_name}"
            ok = create_worktree(target, wt_path)
            if ok:
                selected.append(
                    {
                        "file_path": entry["path"],
                        "score": entry["score"],
                        "worktree_path": str(wt_path),
                    }
                )
            else:
                print_error(f"Failed to create worktree for {entry['path']}")

        if not selected:
            raise PipelineAbort("No worktrees could be created")

        (output_dir / "selected_files.json").write_text(json.dumps(selected, indent=2))
