#!/usr/bin/env python3
"""Summarize the latest agent-skills-eval run for local/CI feedback."""

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_WORKSPACE = Path("/tmp/cc-thingz-skill-eval-workspace")


@dataclass(frozen=True)
class Failure:
    skill: str
    eval_slug: str
    mode: str
    text: str
    evidence: str
    output_path: Path
    grading_path: Path


@dataclass(frozen=True)
class Counts:
    passed: int = 0
    failed: int = 0

    @property
    def total(self) -> int:
        return self.passed + self.failed

    @property
    def rate(self) -> float:
        return self.passed / self.total if self.total else 1.0

    def add(self, other: "Counts") -> "Counts":
        return Counts(self.passed + other.passed, self.failed + other.failed)


@dataclass
class SkillStats:
    with_skill: Counts = field(default_factory=Counts)
    without_skill: Counts = field(default_factory=Counts)

    @property
    def lift(self) -> float:
        return self.with_skill.rate - self.without_skill.rate


def latest_iteration(workspace: Path) -> Path:
    iterations = []
    for path in workspace.glob("iteration-*"):
        if not path.is_dir():
            continue
        try:
            number = int(path.name.removeprefix("iteration-"))
        except ValueError:
            continue
        iterations.append((number, path))
    if not iterations:
        raise FileNotFoundError(f"no iteration-* directories under {workspace}")
    return max(iterations)[1]


def read_meta_name(path: Path, fallback: str) -> str:
    meta_path = path / "meta.json"
    if not meta_path.is_file():
        return fallback
    try:
        with meta_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return fallback
    name = data.get("name")
    return name if isinstance(name, str) and name else fallback


def infer_skill(iteration: Path, grading_path: Path) -> tuple[str, str, str]:
    mode_dir = grading_path.parent
    mode = mode_dir.name
    eval_dir = mode_dir.parent
    rel_parts = eval_dir.relative_to(iteration).parts
    if len(rel_parts) == 1:
        return read_meta_name(iteration, iteration.name), rel_parts[0], mode

    skill_slug = rel_parts[0]
    skill = read_meta_name(iteration / skill_slug, skill_slug)
    return skill, rel_parts[-1], mode


def collect(
    iteration: Path,
) -> tuple[dict[str, Counts], dict[str, SkillStats], list[Failure]]:
    counts: dict[str, Counts] = {
        "with_skill": Counts(),
        "without_skill": Counts(),
    }
    per_skill: dict[str, SkillStats] = defaultdict(SkillStats)
    failures: list[Failure] = []

    for grading_path in sorted(iteration.glob("**/grading.json")):
        skill, eval_slug, mode = infer_skill(iteration, grading_path)
        with grading_path.open("r", encoding="utf-8") as file:
            grading = json.load(file)
        summary = grading.get("summary", {})
        current = Counts(
            passed=int(summary.get("passed", 0)),
            failed=int(summary.get("failed", 0)),
        )
        counts[mode] = counts.get(mode, Counts()).add(current)
        stats = per_skill[skill]
        if mode == "with_skill":
            stats.with_skill = stats.with_skill.add(current)
        elif mode == "without_skill":
            stats.without_skill = stats.without_skill.add(current)

        output_path = grading_path.parent / "outputs" / "output.txt"
        for result in grading.get("assertion_results", []):
            if result.get("passed") is True:
                continue
            failures.append(
                Failure(
                    skill=skill,
                    eval_slug=eval_slug,
                    mode=mode,
                    text=str(result.get("text", "(missing assertion text)")),
                    evidence=str(result.get("evidence", "(missing evidence)")),
                    output_path=output_path,
                    grading_path=grading_path,
                )
            )
    return counts, dict(per_skill), failures


def format_counts(label: str, counts: Counts) -> str:
    return f"{label}: {counts.passed}/{counts.total} passed ({counts.rate:.1%})"


def failure_lines(failures: list[Failure], limit: int) -> list[str]:
    if not failures:
        return ["  none"]
    lines: list[str] = []
    for failure in failures[:limit]:
        lines.extend(
            [
                f"  - {failure.skill} / {failure.eval_slug} [{failure.mode}]",
                f"    assertion: {failure.text}",
                f"    evidence: {failure.evidence}",
                f"    output: {failure.output_path}",
            ]
        )
    hidden = len(failures) - limit
    if hidden > 0:
        lines.append(f"  ... {hidden} more failure(s) omitted")
    return lines


def sorted_skill_rows(per_skill: dict[str, SkillStats]) -> list[tuple[str, SkillStats]]:
    return sorted(
        per_skill.items(),
        key=lambda item: (item[1].with_skill.rate, item[1].lift, item[0]),
    )


def render_text(
    iteration: Path,
    counts: dict[str, Counts],
    per_skill: dict[str, SkillStats],
    failures: list[Failure],
    limit: int,
) -> str:
    with_failures = [failure for failure in failures if failure.mode == "with_skill"]
    baseline_failures = [
        failure for failure in failures if failure.mode == "without_skill"
    ]
    lines = [
        "SKILL EVAL SUMMARY",
        "------------------",
        f"workspace: {iteration}",
        format_counts("with_skill", counts.get("with_skill", Counts())),
        format_counts("without_skill", counts.get("without_skill", Counts())),
        f"report: {iteration / 'report' / 'index.html'}",
        "",
        "LOWEST WITH-SKILL PASS RATES",
    ]
    for skill, stats in sorted_skill_rows(per_skill)[:10]:
        lines.append(
            f"  - {skill}: {stats.with_skill.rate:.1%} "
            f"({stats.with_skill.passed}/{stats.with_skill.total}), "
            f"baseline {stats.without_skill.rate:.1%}, lift {stats.lift:+.1%}"
        )
    lines.extend(
        [
            "",
            "WITH-SKILL FAILURES TO FIX",
            *failure_lines(with_failures, limit),
            "",
            "WITHOUT-SKILL FAILURES (baseline lift signal)",
            *failure_lines(baseline_failures, limit),
        ]
    )
    return "\n".join(lines)


def pct(value: float) -> str:
    return f"{value:.1%}"


def markdown_failure_lines(failures: list[Failure], limit: int) -> list[str]:
    if not failures:
        return ["_None._"]
    lines: list[str] = []
    for failure in failures[:limit]:
        lines.extend(
            [
                f"- **{failure.skill} / {failure.eval_slug}** `[{failure.mode}]`",
                f"  - Assertion: {failure.text}",
                f"  - Evidence: {failure.evidence}",
                f"  - Output: `{failure.output_path}`",
            ]
        )
    hidden = len(failures) - limit
    if hidden > 0:
        lines.append(f"- _{hidden} more failure(s) omitted._")
    return lines


def render_markdown(
    iteration: Path,
    counts: dict[str, Counts],
    per_skill: dict[str, SkillStats],
    failures: list[Failure],
    limit: int,
) -> str:
    with_counts = counts.get("with_skill", Counts())
    baseline_counts = counts.get("without_skill", Counts())
    with_failures = [failure for failure in failures if failure.mode == "with_skill"]
    baseline_failures = [
        failure for failure in failures if failure.mode == "without_skill"
    ]
    lines = [
        "# Skill eval report",
        "",
        f"- Workspace: `{iteration}`",
        f"- HTML report: `{iteration / 'report' / 'index.html'}`",
        f"- With skill: **{with_counts.passed}/{with_counts.total}** "
        f"passed ({pct(with_counts.rate)})",
        f"- Baseline: **{baseline_counts.passed}/{baseline_counts.total}** "
        f"passed ({pct(baseline_counts.rate)})",
        "",
        "## Per-skill results",
        "",
        "| Skill | With skill | Baseline | Lift |",
        "| --- | ---: | ---: | ---: |",
    ]
    for skill, stats in sorted_skill_rows(per_skill):
        lines.append(
            f"| `{skill}` | {stats.with_skill.passed}/{stats.with_skill.total} "
            f"({pct(stats.with_skill.rate)}) | "
            f"{stats.without_skill.passed}/{stats.without_skill.total} "
            f"({pct(stats.without_skill.rate)}) | {pct(stats.lift)} |"
        )
    lines.extend(
        [
            "",
            "## With-skill failures to fix",
            "",
            "These are the actionable failures. Fix the skill, or tighten the eval "
            "only when the judge evidence shows the assertion is wrong.",
            "",
            *markdown_failure_lines(with_failures, limit),
            "",
            "## Baseline failures",
            "",
            "These show skill lift. They are not failures to fix unless the baseline "
            "is outperforming the skill or the eval is malformed.",
            "",
            *markdown_failure_lines(baseline_failures, limit),
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", nargs="?", type=Path, default=DEFAULT_WORKSPACE)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--markdown", type=Path, help="write a Markdown report")
    args = parser.parse_args()

    try:
        iteration = latest_iteration(args.workspace)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        return 1

    counts, per_skill, failures = collect(iteration)
    print(render_text(iteration, counts, per_skill, failures, args.limit))

    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(
            render_markdown(iteration, counts, per_skill, failures, args.limit),
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
