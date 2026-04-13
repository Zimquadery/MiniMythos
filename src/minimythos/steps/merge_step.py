import json
from pathlib import Path
from minimythos.steps.base import Step
from minimythos.config import Settings
from minimythos.agents.runner import AgentRunner
from minimythos.models.report import (
    AgentReport,
    MergedReport,
    VulnerabilityGroup,
    VulnerabilityGuess,
)
from minimythos.utils.display import console


SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


class MergeStep(Step):
    """Merge attack reports into a final security report."""

    def __init__(
        self,
        settings: Settings,
        runner: AgentRunner,
        attack_reports: list[AgentReport] | None = None,
    ):
        super().__init__(settings, runner)
        self.attack_reports = attack_reports or []

    @property
    def name(self) -> str:
        return "Merge"

    async def run(self) -> None:
        output_dir = self.settings.output_dir or self.settings.target_path

        if not self.attack_reports:
            reports_dir = output_dir / "attack_reports"
            if reports_dir.exists():
                for f in reports_dir.glob("*.json"):
                    try:
                        data = json.loads(f.read_text())
                        self.attack_reports.append(AgentReport(**data))
                    except Exception:
                        pass

        all_vulns: list[VulnerabilityGuess] = []
        for report in self.attack_reports:
            all_vulns.extend(report.vulnerabilities)

        groups = self._group_vulnerabilities(all_vulns)
        groups.sort(key=lambda g: SEVERITY_ORDER.get(g.severity, 99))

        merged = MergedReport(
            target_path=str(self.settings.target_path),
            total_vulnerabilities=len(all_vulns),
            groups=groups,
        )

        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "security_report.json").write_text(
            merged.model_dump_json(indent=2)
        )

        md_lines = [
            f"# Security Report: {self.settings.target_path}",
            f"",
            f"**Total vulnerabilities found:** {merged.total_vulnerabilities}",
            f"**Unique groups:** {len(merged.groups)}",
            f"",
        ]
        for g in groups:
            md_lines.append(f"## {g.title} [{g.severity.upper()}]")
            md_lines.append(f"{g.description}")
            if g.cwe_id:
                md_lines.append(f"CWE: {g.cwe_id}")
            md_lines.append(f"Occurrences: {len(g.occurrences)}")
            md_lines.append("")
        (output_dir / "security_report.md").write_text("\n".join(md_lines))

    def _group_vulnerabilities(
        self, vulns: list[VulnerabilityGuess]
    ) -> list[VulnerabilityGroup]:
        if not vulns:
            return []

        by_cwe: dict[str, list[VulnerabilityGuess]] = {}
        remaining: list[VulnerabilityGuess] = []

        for v in vulns:
            if v.cwe_id:
                by_cwe.setdefault(v.cwe_id, []).append(v)
            else:
                remaining.append(v)

        by_title: dict[str, list[VulnerabilityGuess]] = {}
        for v in remaining:
            key = v.title.lower().strip()
            by_title.setdefault(key, []).append(v)

        groups: list[VulnerabilityGroup] = []

        for cwe_id, occurrences in by_cwe.items():
            groups.append(self._make_group(occurrences))

        for _, occurrences in by_title.items():
            groups.append(self._make_group(occurrences))

        return groups

    def _make_group(self, occurrences: list[VulnerabilityGuess]) -> VulnerabilityGroup:
        first = occurrences[0]
        highest = min(occurrences, key=lambda v: SEVERITY_ORDER.get(v.severity, 99))
        return VulnerabilityGroup(
            title=first.title,
            description=first.description,
            severity=highest.severity,
            cwe_id=first.cwe_id,
            occurrences=occurrences,
        )
