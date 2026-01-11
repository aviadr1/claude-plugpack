#!/usr/bin/env python3
"""
Quality Report Generator for Claude Code Plugins.

Generates comprehensive quality reports to help plugin creators
improve their plugins. Reports include security, maintenance,
documentation, and testing assessments.

Usage:
    python -m generator.quality_report https://github.com/user/plugin
    python -m generator.quality_report /path/to/plugin
"""

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from skills.plugin_analyzer.analyzer import (
    PluginAnalysis,
    _analyze_plugin_path,
    clone_plugin,
    find_files,
)


@dataclass
class SecurityCheck:
    """Security assessment results."""

    score: int = 100
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    passes: list[str] = field(default_factory=list)


@dataclass
class MaintenanceCheck:
    """Maintenance assessment results."""

    score: int = 100
    status: str = "unknown"
    last_commit: str = ""
    commit_frequency: str = ""
    issue_response: str = ""


@dataclass
class DocumentationCheck:
    """Documentation assessment results."""

    score: int = 100
    has_readme: bool = False
    has_changelog: bool = False
    has_license: bool = False
    has_contributing: bool = False
    command_docs: int = 0
    agent_docs: int = 0
    issues: list[str] = field(default_factory=list)


@dataclass
class TestingCheck:
    """Testing assessment results."""

    score: int = 100
    has_tests: bool = False
    has_ci: bool = False
    test_framework: str = ""
    issues: list[str] = field(default_factory=list)


@dataclass
class QualityReport:
    """Complete quality report."""

    plugin_name: str
    plugin_url: str
    generated_at: str
    overall_score: int = 0
    security: SecurityCheck = field(default_factory=SecurityCheck)
    maintenance: MaintenanceCheck = field(default_factory=MaintenanceCheck)
    documentation: DocumentationCheck = field(default_factory=DocumentationCheck)
    testing: TestingCheck = field(default_factory=TestingCheck)
    recommendations: list[dict[str, Any]] = field(default_factory=list)


def check_security(plugin_path: Path) -> SecurityCheck:
    """Check for common security issues."""
    security = SecurityCheck()

    # Patterns to check for
    dangerous_patterns = [
        (r"eval\s*\(", "Uses eval() - potential code injection", "issue"),
        (r"exec\s*\(", "Uses exec() - potential code injection", "issue"),
        (r"child_process|subprocess\.call|os\.system", "Executes external processes", "warning"),
        (r"fs\.unlink|os\.remove|shutil\.rmtree", "Deletes files/directories", "warning"),
        (r"requests\.get|httpx\.get|fetch\s*\(", "Makes external HTTP requests", "warning"),
        (r"__import__", "Dynamic imports - review carefully", "warning"),
    ]

    # Safe patterns to award points for
    safe_patterns = [
        (r"validate|sanitize|escape", "Uses input validation/sanitization"),
        (r"try\s*:|except\s*:", "Has error handling"),
    ]

    for file in find_files(plugin_path, "**/*.py"):
        try:
            content = file.read_text()
            for pattern, message, severity in dangerous_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    if severity == "issue":
                        security.issues.append(f"{file.name}: {message}")
                        security.score -= 20
                    else:
                        security.warnings.append(f"{file.name}: {message}")
                        security.score -= 5

            for pattern, message in safe_patterns:
                if re.search(pattern, content, re.IGNORECASE) and message not in security.passes:
                    security.passes.append(message)
        except UnicodeDecodeError:
            pass

    for file in find_files(plugin_path, "**/*.js"):
        try:
            content = file.read_text()
            for pattern, message, severity in dangerous_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    if severity == "issue":
                        security.issues.append(f"{file.name}: {message}")
                        security.score -= 20
                    else:
                        security.warnings.append(f"{file.name}: {message}")
                        security.score -= 5
        except UnicodeDecodeError:
            pass

    # Check for hardcoded secrets
    secret_patterns = [
        r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]",
        r"password\s*=\s*['\"][^'\"]+['\"]",
        r"secret\s*=\s*['\"][^'\"]+['\"]",
        r"token\s*=\s*['\"][^'\"]+['\"]",
    ]

    for file in find_files(plugin_path, "**/*"):
        if file.is_file() and file.suffix in (".py", ".js", ".ts", ".json", ".yml", ".yaml"):
            try:
                content = file.read_text()
                for pattern in secret_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        security.issues.append(f"{file.name}: Potential hardcoded secret")
                        security.score -= 30
                        break
            except UnicodeDecodeError:
                pass

    # Ensure score is within bounds
    security.score = max(0, min(100, security.score))

    if not security.issues and not security.warnings:
        security.passes.append("No critical security issues found")

    return security


def check_maintenance(analysis: PluginAnalysis) -> MaintenanceCheck:
    """Check maintenance status and activity."""
    maintenance = MaintenanceCheck()

    if analysis.quality.maintenance_status:
        maintenance.status = analysis.quality.maintenance_status
        maintenance.last_commit = analysis.quality.last_commit

        # Score based on maintenance status
        status_scores = {
            "active": 100,
            "maintained": 85,
            "slow": 60,
            "stale": 30,
            "unknown": 50,
        }
        maintenance.score = status_scores.get(maintenance.status, 50)

        # Estimate commit frequency based on last commit
        if maintenance.last_commit:
            try:
                last = datetime.fromisoformat(maintenance.last_commit.replace("Z", "+00:00"))
                days_since = (datetime.now(UTC) - last).days
                if days_since < 7:
                    maintenance.commit_frequency = "Very active (< 1 week)"
                elif days_since < 30:
                    maintenance.commit_frequency = "Active (< 1 month)"
                elif days_since < 90:
                    maintenance.commit_frequency = "Moderate (< 3 months)"
                else:
                    maintenance.commit_frequency = "Infrequent (3+ months)"
            except ValueError:
                pass

    return maintenance


def check_documentation(plugin_path: Path, analysis: PluginAnalysis) -> DocumentationCheck:
    """Check documentation quality."""
    docs = DocumentationCheck()

    # Check for standard files
    docs.has_readme = (plugin_path / "README.md").exists() or (plugin_path / "readme.md").exists()
    docs.has_changelog = (plugin_path / "CHANGELOG.md").exists() or (
        plugin_path / "changelog.md"
    ).exists()
    docs.has_license = (plugin_path / "LICENSE").exists() or (plugin_path / "LICENSE.md").exists()
    docs.has_contributing = (plugin_path / "CONTRIBUTING.md").exists()

    # Check for command/agent documentation
    commands_dir = plugin_path / "commands"
    agents_dir = plugin_path / "agents"

    if commands_dir.exists():
        docs.command_docs = len(list(commands_dir.glob("*.md")))
    if agents_dir.exists():
        docs.agent_docs = len(list(agents_dir.glob("*.md")))

    # Calculate score
    score = 0
    if docs.has_readme:
        score += 40
    else:
        docs.issues.append("Missing README.md")

    if docs.has_changelog:
        score += 15
    else:
        docs.issues.append("Missing CHANGELOG.md")

    if docs.has_license:
        score += 15
    else:
        docs.issues.append("Missing LICENSE file")

    if docs.has_contributing:
        score += 10

    # Check if components are documented
    if analysis.components.commands > 0:
        if docs.command_docs >= analysis.components.commands:
            score += 10
        else:
            docs.issues.append(
                f"Only {docs.command_docs}/{analysis.components.commands} commands documented"
            )

    if analysis.components.agents > 0:
        if docs.agent_docs >= analysis.components.agents:
            score += 10
        else:
            docs.issues.append(
                f"Only {docs.agent_docs}/{analysis.components.agents} agents documented"
            )

    docs.score = min(100, score)

    return docs


def check_testing(plugin_path: Path) -> TestingCheck:
    """Check testing infrastructure."""
    testing = TestingCheck()

    # Check for test directories/files
    test_patterns = [
        ("tests/", "pytest"),
        ("test/", "pytest"),
        ("__tests__/", "jest"),
        ("spec/", "rspec"),
    ]

    for pattern, framework in test_patterns:
        if (plugin_path / pattern).exists():
            testing.has_tests = True
            testing.test_framework = framework
            break

    # Check for test files
    test_files = list(plugin_path.glob("**/test_*.py")) + list(plugin_path.glob("**/*_test.py"))
    test_files += list(plugin_path.glob("**/*.test.js")) + list(plugin_path.glob("**/*.spec.js"))

    if test_files:
        testing.has_tests = True

    # Check for CI
    ci_configs = [
        ".github/workflows",
        ".circleci",
        ".travis.yml",
        "azure-pipelines.yml",
        "Jenkinsfile",
    ]

    for ci in ci_configs:
        if (plugin_path / ci).exists():
            testing.has_ci = True
            break

    # Calculate score
    score = 0
    if testing.has_tests:
        score += 50
    else:
        testing.issues.append("No automated tests found")

    if testing.has_ci:
        score += 50
    else:
        testing.issues.append("No CI/CD configuration found")

    testing.score = score

    return testing


def generate_recommendations(report: QualityReport) -> list[dict[str, Any]]:
    """Generate prioritized recommendations."""
    recommendations = []

    # High priority: Security issues
    for issue in report.security.issues:
        recommendations.append(
            {
                "priority": "high",
                "category": "security",
                "issue": issue,
                "action": "Review and fix security vulnerability",
            }
        )

    # High priority: Missing README
    if not report.documentation.has_readme:
        recommendations.append(
            {
                "priority": "high",
                "category": "documentation",
                "issue": "Missing README.md",
                "action": "Add a README with installation and usage instructions",
            }
        )

    # Medium priority: Testing
    if not report.testing.has_tests:
        recommendations.append(
            {
                "priority": "medium",
                "category": "testing",
                "issue": "No automated tests found",
                "action": "Add test coverage for commands and agents",
            }
        )

    if not report.testing.has_ci:
        recommendations.append(
            {
                "priority": "medium",
                "category": "testing",
                "issue": "No CI/CD configuration",
                "action": "Set up GitHub Actions for automated testing",
            }
        )

    # Medium priority: Documentation gaps
    for issue in report.documentation.issues:
        if "README" not in issue:  # Already handled as high priority
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "documentation",
                    "issue": issue,
                    "action": "Add missing documentation",
                }
            )

    # Low priority: Maintenance warnings
    if report.maintenance.status == "stale":
        recommendations.append(
            {
                "priority": "low",
                "category": "maintenance",
                "issue": "Repository hasn't been updated in 6+ months",
                "action": "Consider updating or marking as unmaintained",
            }
        )

    # Low priority: Security warnings
    for warning in report.security.warnings:
        recommendations.append(
            {
                "priority": "low",
                "category": "security",
                "issue": warning,
                "action": "Review if this is necessary for plugin functionality",
            }
        )

    return recommendations


def generate_quality_report(plugin_url_or_path: str) -> QualityReport:
    """Generate comprehensive quality report for a plugin."""

    # Get plugin path
    if plugin_url_or_path.startswith("http"):
        # Use context manager to clone once and clean up after
        with clone_plugin(plugin_url_or_path) as plugin_path:
            return _generate_report_for_path(plugin_path, plugin_url_or_path)
    else:
        # Local path - no cleanup needed
        plugin_path = Path(plugin_url_or_path)
        return _generate_report_for_path(plugin_path, "")


def _generate_report_for_path(plugin_path: Path, repo_url: str) -> QualityReport:
    """Internal function to generate report for a plugin at a given path."""
    # Run plugin analysis (reusing the path, no second clone)
    analysis = _analyze_plugin_path(plugin_path, repo_url)

    # Create report
    report = QualityReport(
        plugin_name=analysis.name,
        plugin_url=repo_url or str(plugin_path),
        generated_at=datetime.now(UTC).isoformat(),
    )

    # Run checks
    report.security = check_security(plugin_path)
    report.maintenance = check_maintenance(analysis)
    report.documentation = check_documentation(plugin_path, analysis)
    report.testing = check_testing(plugin_path)

    # Calculate overall score (weighted average)
    report.overall_score = int(
        report.security.score * 0.30
        + report.maintenance.score * 0.25
        + report.documentation.score * 0.25
        + report.testing.score * 0.20
    )

    # Generate recommendations
    report.recommendations = generate_recommendations(report)

    return report


def format_report_markdown(report: QualityReport) -> str:
    """Format report as Markdown."""
    lines = []

    lines.append(f"# Quality Report: {report.plugin_name}")
    lines.append("")
    lines.append(f"Generated: {report.generated_at[:10]}")
    lines.append(f"Overall Score: **{report.overall_score}/100**")
    lines.append("")

    # Security
    lines.append(f"## Security ({report.security.score}/100)")
    lines.append("")
    if report.security.issues:
        lines.append("**Issues:**")
        for issue in report.security.issues:
            lines.append(f"- {issue}")
        lines.append("")
    if report.security.warnings:
        lines.append("**Warnings:**")
        for warning in report.security.warnings:
            lines.append(f"- {warning}")
        lines.append("")
    if report.security.passes:
        lines.append("**Passes:**")
        for pass_item in report.security.passes:
            lines.append(f"- {pass_item}")
        lines.append("")

    # Maintenance
    lines.append(f"## Maintenance ({report.maintenance.score}/100)")
    lines.append("")
    lines.append(f"- Status: **{report.maintenance.status.title()}**")
    if report.maintenance.commit_frequency:
        lines.append(f"- Commit frequency: {report.maintenance.commit_frequency}")
    lines.append("")

    # Documentation
    lines.append(f"## Documentation ({report.documentation.score}/100)")
    lines.append("")
    lines.append(f"- README: {'Yes' if report.documentation.has_readme else 'No'}")
    lines.append(f"- CHANGELOG: {'Yes' if report.documentation.has_changelog else 'No'}")
    lines.append(f"- LICENSE: {'Yes' if report.documentation.has_license else 'No'}")
    lines.append(f"- CONTRIBUTING: {'Yes' if report.documentation.has_contributing else 'No'}")
    if report.documentation.issues:
        lines.append("")
        lines.append("**Improvements needed:**")
        for issue in report.documentation.issues:
            lines.append(f"- {issue}")
    lines.append("")

    # Testing
    lines.append(f"## Testing ({report.testing.score}/100)")
    lines.append("")
    lines.append(f"- Automated tests: {'Yes' if report.testing.has_tests else 'No'}")
    lines.append(f"- CI/CD: {'Yes' if report.testing.has_ci else 'No'}")
    if report.testing.test_framework:
        lines.append(f"- Framework: {report.testing.test_framework}")
    if report.testing.issues:
        lines.append("")
        lines.append("**Improvements needed:**")
        for issue in report.testing.issues:
            lines.append(f"- {issue}")
    lines.append("")

    # Recommendations
    if report.recommendations:
        lines.append("## Recommendations")
        lines.append("")

        high = [r for r in report.recommendations if r["priority"] == "high"]
        medium = [r for r in report.recommendations if r["priority"] == "medium"]
        low = [r for r in report.recommendations if r["priority"] == "low"]

        if high:
            lines.append("### High Priority")
            for i, rec in enumerate(high, 1):
                lines.append(f"{i}. **{rec['issue']}**")
                lines.append(f"   - {rec['action']}")
            lines.append("")

        if medium:
            lines.append("### Medium Priority")
            for i, rec in enumerate(medium, 1):
                lines.append(f"{i}. **{rec['issue']}**")
                lines.append(f"   - {rec['action']}")
            lines.append("")

        if low:
            lines.append("### Low Priority")
            for i, rec in enumerate(low, 1):
                lines.append(f"{i}. **{rec['issue']}**")
                lines.append(f"   - {rec['action']}")

    return "\n".join(lines)


def main():
    """Main entry point for CLI usage."""
    import sys

    if len(sys.argv) < 2:
        print(
            "Usage: python -m generator.quality_report <plugin-url-or-path> [--format json|markdown]"
        )
        sys.exit(1)

    plugin_url = sys.argv[1]
    output_format = "markdown"

    if "--format" in sys.argv:
        idx = sys.argv.index("--format")
        if idx + 1 < len(sys.argv):
            output_format = sys.argv[idx + 1]

    try:
        report = generate_quality_report(plugin_url)

        if output_format == "json":
            print(
                json.dumps(
                    {
                        "plugin_name": report.plugin_name,
                        "plugin_url": report.plugin_url,
                        "generated_at": report.generated_at,
                        "overall_score": report.overall_score,
                        "security": {
                            "score": report.security.score,
                            "issues": report.security.issues,
                            "warnings": report.security.warnings,
                            "passes": report.security.passes,
                        },
                        "maintenance": {
                            "score": report.maintenance.score,
                            "status": report.maintenance.status,
                            "commit_frequency": report.maintenance.commit_frequency,
                        },
                        "documentation": {
                            "score": report.documentation.score,
                            "has_readme": report.documentation.has_readme,
                            "has_changelog": report.documentation.has_changelog,
                            "has_license": report.documentation.has_license,
                            "issues": report.documentation.issues,
                        },
                        "testing": {
                            "score": report.testing.score,
                            "has_tests": report.testing.has_tests,
                            "has_ci": report.testing.has_ci,
                            "issues": report.testing.issues,
                        },
                        "recommendations": report.recommendations,
                    },
                    indent=2,
                )
            )
        else:
            print(format_report_markdown(report))
    except Exception as e:
        print(f"Error generating report: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
