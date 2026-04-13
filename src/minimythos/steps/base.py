from abc import ABC, abstractmethod
from minimythos.config import Settings
from minimythos.agents.runner import AgentRunner


class Step(ABC):
    def __init__(self, settings: Settings, runner: AgentRunner):
        self.settings = settings
        self.runner = runner

    @abstractmethod
    async def run(self) -> None: ...

    @property
    @abstractmethod
    def name(self) -> str: ...
