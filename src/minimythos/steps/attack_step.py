import json
from pathlib import Path
from minimythos.steps.base import Step
from minimythos.config import Settings
from minimythos.agents.runner import AgentRunner
from minimythos.models.report import AgentReport, VulnerabilityGuess
from minimythos.steps.select_step import remove_worktree
from minimythos.utils.display import print_error


class AttackStep(Step):
    """Attack selected files to find proven vulnerabilities."""

    @property
    def name(self) -> str:
        return "Attack"

    async def run(self) -> list[AgentReport]:
        output_dir = self.settings.output_dir or self.settings.target_path
        selected_file = output_dir / "selected_files.json"

        if not selected_file.exists():
            print_error("selected_files.json not found")
            return []

        selected = json.loads(selected_file.read_text())
        prompt_path = (
            Path(__file__).resolve().parent.parent.parent.parent
            / "prompts"
            / "attack_prompt.txt"
        )
        prompt_template = prompt_path.read_text()

        tasks = []
        for entry in selected:
            prompt = prompt_template.replace("{file_path}", entry["file_path"])
            tasks.append((prompt, Path(entry["worktree_path"])))

        results = await self.runner.run_parallel(tasks)

        reports_dir = output_dir / "attack_reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        reports: list[AgentReport] = []

        try:
            for entry, result in zip(selected, results):
                vulnerabilities: list[VulnerabilityGuess] = []
                success = result.success

                if result.success:
                    try:
                        parsed = json.loads(result.stdout)
                        vuln_data = parsed.get("vulnerabilities", [])
                        for v in vuln_data:
                            vulnerabilities.append(VulnerabilityGuess(**v))
                    except (json.JSONDecodeError, Exception):
                        success = False

                report = AgentReport(
                    worktree_path=entry["worktree_path"],
                    file_path=entry["file_path"],
                    vulnerabilities=vulnerabilities,
                    agent_stdout=result.stdout,
                    agent_stderr=result.stderr,
                    success=success,
                )
                reports.append(report)

                safe_name = entry["file_path"].replace("/", "_").replace("\\", "_")
                (reports_dir / f"report_{safe_name}.json").write_text(
                    report.model_dump_json(indent=2)
                )
        finally:
            for entry in selected:
                try:
                    remove_worktree(
                        self.settings.target_path, Path(entry["worktree_path"])
                    )
                except Exception:
                    pass

        return reports
