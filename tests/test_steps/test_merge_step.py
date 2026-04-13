import json
from pathlib import Path
from unittest.mock import AsyncMock
import pytest
from minimythos.agents.runner import AgentRunner
from minimythos.models.report import AgentReport, VulnerabilityGuess
from minimythos.steps.merge_step import MergeStep


@pytest.mark.asyncio
async def test_merge_step_empty_reports(default_settings):
    runner = AgentRunner(command="echo", max_parallel=1)
    step = MergeStep(default_settings, runner, attack_reports=[])
    await step.run()
    output_dir = default_settings.output_dir
    report = json.loads((output_dir / "security_report.json").read_text())
    assert report["total_vulnerabilities"] == 0


@pytest.mark.asyncio
async def test_merge_step_with_vulns(default_settings):
    guess = VulnerabilityGuess(
        title="SQL Injection",
        description="Unsanitized input in query",
        file_path="src/db.py",
        line_range="10-15",
        severity="high",
        cwe_id="CWE-89",
        proof="SELECT * FROM users WHERE id = '' OR 1=1",
    )
    report = AgentReport(
        worktree_path="/tmp/wt",
        file_path="src/db.py",
        vulnerabilities=[guess],
        agent_stdout="{}",
        agent_stderr="",
        success=True,
    )
    runner = AgentRunner(command="echo", max_parallel=1)
    step = MergeStep(default_settings, runner, attack_reports=[report])
    await step.run()
    output_dir = default_settings.output_dir
    data = json.loads((output_dir / "security_report.json").read_text())
    assert data["total_vulnerabilities"] == 1
    assert len(data["groups"]) == 1


@pytest.mark.asyncio
async def test_merge_step_groups_by_cwe_id(default_settings):
    guesses = [
        VulnerabilityGuess(
            title="SQL Injection",
            description="desc1",
            file_path="a.py",
            line_range="1",
            severity="high",
            cwe_id="CWE-89",
            proof="p1",
        ),
        VulnerabilityGuess(
            title="SQLi variant",
            description="desc2",
            file_path="b.py",
            line_range="2",
            severity="critical",
            cwe_id="CWE-89",
            proof="p2",
        ),
    ]
    report = AgentReport(
        worktree_path="/tmp/wt",
        file_path="a.py",
        vulnerabilities=guesses,
        agent_stdout="",
        agent_stderr="",
        success=True,
    )
    runner = AsyncMock(spec=AgentRunner)
    step = MergeStep(default_settings, runner, attack_reports=[report])
    await step.run()
    data = json.loads(
        (default_settings.output_dir / "security_report.json").read_text()
    )
    assert data["total_vulnerabilities"] == 2
    assert len(data["groups"]) == 1
    assert data["groups"][0]["severity"] == "critical"


@pytest.mark.asyncio
async def test_merge_step_groups_by_title(default_settings):
    guesses = [
        VulnerabilityGuess(
            title="XSS",
            description="desc1",
            file_path="a.py",
            line_range="1",
            severity="high",
            proof="p1",
        ),
        VulnerabilityGuess(
            title="xss",
            description="desc2",
            file_path="b.py",
            line_range="2",
            severity="medium",
            proof="p2",
        ),
    ]
    report = AgentReport(
        worktree_path="/tmp/wt",
        file_path="a.py",
        vulnerabilities=guesses,
        agent_stdout="",
        agent_stderr="",
        success=True,
    )
    runner = AsyncMock(spec=AgentRunner)
    step = MergeStep(default_settings, runner, attack_reports=[report])
    await step.run()
    data = json.loads(
        (default_settings.output_dir / "security_report.json").read_text()
    )
    assert len(data["groups"]) == 1
    assert len(data["groups"][0]["occurrences"]) == 2


@pytest.mark.asyncio
async def test_merge_step_sorts_by_severity(default_settings):
    guesses = [
        VulnerabilityGuess(
            title="Low Bug",
            description="d",
            file_path="a.py",
            line_range="1",
            severity="low",
            proof="p",
        ),
        VulnerabilityGuess(
            title="Critical Bug",
            description="d",
            file_path="b.py",
            line_range="1",
            severity="critical",
            cwe_id="CWE-1",
            proof="p",
        ),
        VulnerabilityGuess(
            title="Medium Bug",
            description="d",
            file_path="c.py",
            line_range="1",
            severity="medium",
            cwe_id="CWE-2",
            proof="p",
        ),
    ]
    report = AgentReport(
        worktree_path="/tmp/wt",
        file_path="a.py",
        vulnerabilities=guesses,
        agent_stdout="",
        agent_stderr="",
        success=True,
    )
    runner = AsyncMock(spec=AgentRunner)
    step = MergeStep(default_settings, runner, attack_reports=[report])
    await step.run()
    data = json.loads(
        (default_settings.output_dir / "security_report.json").read_text()
    )
    severities = [g["severity"] for g in data["groups"]]
    assert severities == ["critical", "medium", "low"]


@pytest.mark.asyncio
async def test_merge_step_writes_markdown(default_settings):
    guess = VulnerabilityGuess(
        title="SQL Injection",
        description="desc",
        file_path="db.py",
        line_range="10",
        severity="high",
        cwe_id="CWE-89",
        proof="evidence",
    )
    report = AgentReport(
        worktree_path="/tmp/wt",
        file_path="db.py",
        vulnerabilities=[guess],
        agent_stdout="",
        agent_stderr="",
        success=True,
    )
    runner = AsyncMock(spec=AgentRunner)
    step = MergeStep(default_settings, runner, attack_reports=[report])
    await step.run()
    md = (default_settings.output_dir / "security_report.md").read_text()
    assert "SQL Injection" in md
    assert "HIGH" in md
    assert "CWE-89" in md
