import json
from pathlib import Path
from minimythos.steps.base import Step
from minimythos.config import Settings
from minimythos.agents.runner import AgentRunner
from minimythos.models.file_score import FileScore, ScoreBatch, VulnerabilityScoreFile
from minimythos.utils.files import discover_code_files, batch_files
from minimythos.utils.display import console, print_error
from minimythos.utils.json_utils import parse_json_output
from minimythos.exceptions import PipelineAbort


class ScoreStep(Step):
    """Score files for vulnerability likelihood."""

    @property
    def name(self) -> str:
        return "Score"

    async def run(self) -> None:
        files = discover_code_files(self.settings.target_path)
        if not files:
            raise PipelineAbort("No code files discovered in target path")

        batches = batch_files(files, self.settings.batch_size)
        prompt_path = (
            Path(__file__).resolve().parent.parent.parent.parent
            / "prompts"
            / "score_prompt.txt"
        )
        prompt_template = prompt_path.read_text()

        tasks = []
        for i, batch in enumerate(batches):
            file_list = "\n".join(str(f) for f in batch)
            prompt = prompt_template.replace("{file_list}", file_list)
            tasks.append((prompt, self.settings.target_path))

        results = await self.runner.run_parallel(tasks)

        score_batches: list[ScoreBatch] = []
        any_agent_succeeded = False

        for i, (batch, result) in enumerate(zip(batches, results)):
            scores: list[FileScore] = []
            if result.success:
                any_agent_succeeded = True
                try:
                    parsed = parse_json_output(result.stdout)
                    for item in parsed:
                        scores.append(FileScore(**item))
                except (json.JSONDecodeError, Exception):
                    snippet = result.stdout[:200] if result.stdout else "(empty)"
                    console.print(
                        f"[yellow]Warning: Failed to parse scores for batch {i}, assigning 0[/yellow]"
                    )
                    console.print(f"[dim]  Raw output: {snippet}[/dim]")
                    for f in batch:
                        scores.append(
                            FileScore(path=str(f), score=0, reason="Parsing failed")
                        )
            else:
                print_error(f"Agent failed for batch {i}: {result.stderr}")
                for f in batch:
                    scores.append(
                        FileScore(path=str(f), score=0, reason="Agent failed")
                    )

            score_batches.append(
                ScoreBatch(
                    batch_id=i,
                    files=[str(f) for f in batch],
                    scores=scores,
                )
            )

        if not any_agent_succeeded:
            raise PipelineAbort("All scoring agents failed")

        vsf = VulnerabilityScoreFile(
            target_path=str(self.settings.target_path),
            batches=score_batches,
        )
        output_dir = self.settings.output_dir or self.settings.target_path
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "vulnerability_score.json").write_text(
            vsf.model_dump_json(indent=2)
        )
