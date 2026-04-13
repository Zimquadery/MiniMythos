from pydantic import BaseModel


class VulnerabilityGuess(BaseModel):
    title: str
    description: str
    file_path: str
    line_range: str
    severity: str
    cwe_id: str | None = None
    proof: str


class AgentReport(BaseModel):
    worktree_path: str
    file_path: str
    vulnerabilities: list[VulnerabilityGuess]
    agent_stdout: str
    agent_stderr: str
    success: bool


class VulnerabilityGroup(BaseModel):
    title: str
    description: str
    severity: str
    cwe_id: str | None
    occurrences: list[VulnerabilityGuess]


class MergedReport(BaseModel):
    target_path: str
    total_vulnerabilities: int
    groups: list[VulnerabilityGroup]
