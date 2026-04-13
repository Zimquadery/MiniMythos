import json
from pathlib import Path
from minimythos.steps.base import Step
from minimythos.config import Settings
from minimythos.agents.runner import AgentRunner
from minimythos.exceptions import PipelineAbort
from minimythos.utils.display import print_error


class MapStep(Step):
    """Map codebase file dependencies."""

    @property
    def name(self) -> str:
        return "Map"

    async def run(self) -> None:
        prompt_path = (
            Path(__file__).resolve().parent.parent.parent.parent
            / "prompts"
            / "map_prompt.txt"
        )
        prompt = prompt_path.read_text()
        prompt = prompt.replace("{target_path}", str(self.settings.target_path))

        result = await self.runner.run(prompt, workdir=self.settings.target_path)

        if not result.success:
            print_error(f"Map agent failed: {result.stderr}")
            raise PipelineAbort(f"Map step failed: {result.stderr}")

        output_dir = self.settings.output_dir or self.settings.target_path
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "codebase_map.txt").write_text(result.stdout)
