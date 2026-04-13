import asyncio
from pathlib import Path
from minimythos.config import Settings
from minimythos.agents.runner import AgentRunner
from minimythos.exceptions import PipelineAbort
from minimythos.steps.map_step import MapStep
from minimythos.steps.score_step import ScoreStep
from minimythos.steps.select_step import SelectStep
from minimythos.steps.attack_step import AttackStep
from minimythos.steps.merge_step import MergeStep
from minimythos.utils.display import print_step_header, print_step_result


class Orchestrator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.runner = AgentRunner(
            command=settings.agent_command,
            max_parallel=settings.max_parallel_agents,
        )

    async def run(self) -> None:
        attack_reports = []

        steps = [
            ("Map", MapStep),
            ("Score", ScoreStep),
            ("Select", SelectStep),
            ("Attack", AttackStep),
            ("Merge", MergeStep),
        ]

        for step_name, step_cls in steps:
            print_step_header(step_name, step_cls.__doc__ or "")

            if step_name == "Merge":
                step = MergeStep(
                    self.settings, self.runner, attack_reports=attack_reports
                )
            else:
                step = step_cls(self.settings, self.runner)

            try:
                result = await step.run()
                if step_name == "Attack":
                    attack_reports = result or []
                print_step_result(step_name, True)
            except PipelineAbort as e:
                print_step_result(step_name, False, str(e))
                break
            except Exception as e:
                print_step_result(step_name, False, f"Unexpected error: {e}")
                break
