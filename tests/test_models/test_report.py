import json
import pytest
from minimythos.models.report import (
    VulnerabilityGuess,
    AgentReport,
    MergedReport,
    VulnerabilityGroup,
)


def test_vulnerability_guess_with_cwe():
    v = VulnerabilityGuess(
        title="SQL Injection",
        description="Unsanitized input",
        file_path="db.py",
        line_range="10-20",
        severity="critical",
        cwe_id="CWE-89",
        proof="SELECT * FROM t WHERE id='' OR 1=1",
    )
    assert v.cwe_id == "CWE-89"
    assert v.severity == "critical"


def test_vulnerability_guess_without_cwe():
    v = VulnerabilityGuess(
        title="XSS",
        description="Reflected input",
        file_path="view.py",
        line_range="5-8",
        severity="high",
        proof="<script>alert(1)</script>",
    )
    assert v.cwe_id is None


def test_agent_report():
    report = AgentReport(
        worktree_path="/tmp/wt",
        file_path="src/app.py",
        vulnerabilities=[],
        agent_stdout="output",
        agent_stderr="",
        success=True,
    )
    assert report.success is True
    assert len(report.vulnerabilities) == 0


def test_vulnerability_group():
    occ = VulnerabilityGuess(
        title="XSS",
        description="desc",
        file_path="a.py",
        line_range="1",
        severity="high",
        proof="p",
    )
    g = VulnerabilityGroup(
        title="XSS",
        description="desc",
        severity="high",
        cwe_id="CWE-79",
        occurrences=[occ],
    )
    assert len(g.occurrences) == 1


def test_merged_report():
    g = VulnerabilityGroup(
        title="SQLi",
        description="desc",
        severity="critical",
        cwe_id="CWE-89",
        occurrences=[],
    )
    mr = MergedReport(
        target_path="/project",
        total_vulnerabilities=3,
        groups=[g],
    )
    assert mr.total_vulnerabilities == 3
    assert len(mr.groups) == 1
