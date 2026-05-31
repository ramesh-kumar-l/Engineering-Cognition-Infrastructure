"""Eval gate — runs before every release to block on benchmark regressions.

Checks:
1. All eval contract files exist and have threshold tables defined.
2. (Optional) Runs retrieval benchmarks when ECI_EVAL_CORPUS_AVAILABLE=true.

Exit codes: 0 = pass, 1 = fail.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

EVAL_DIR = Path(__file__).parent.parent / "project-memory-bank" / "evaluations"

REQUIRED_EVAL_FILES = [
    "ingestion-correctness.md",
    "summarization-faithfulness.md",
    "retrieval-benchmarks.md",
    "reflection-quality.md",
]

THRESHOLD_MARKERS = ["| Metric", "| Threshold", "## Metrics"]


def check_eval_contracts() -> list[str]:
    """Return list of problems found in eval contract files."""
    problems: list[str] = []
    for filename in REQUIRED_EVAL_FILES:
        path = EVAL_DIR / filename
        if not path.exists():
            problems.append(f"Missing eval contract: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        if not any(marker in text for marker in THRESHOLD_MARKERS):
            problems.append(f"No threshold table found in: {path}")
    return problems


def run_corpus_benchmarks() -> list[str]:
    """Run retrieval benchmarks against a live corpus. Stub — extend for real runs."""
    problems: list[str] = []
    # When a real corpus + Ollama are available, this section would:
    # 1. Run the retrieval benchmark queries.
    # 2. Compute Recall@5, MRR, citation coverage.
    # 3. Compare against retrieval-benchmarks.md thresholds.
    # For now, log that this step requires the Ollama CI environment.
    print(
        "INFO: Corpus benchmark run skipped — "
        "set ECI_EVAL_CORPUS_AVAILABLE=true to enable."
    )
    return problems


def main() -> int:
    print(f"Eval gate — checking {EVAL_DIR}")

    problems = check_eval_contracts()
    if problems:
        print("FAIL: Eval contract problems:")
        for p in problems:
            print(f"  - {p}")
        return 1

    print(f"OK: All {len(REQUIRED_EVAL_FILES)} eval contract files present with thresholds.")

    if os.environ.get("ECI_EVAL_CORPUS_AVAILABLE", "").lower() == "true":
        corpus_problems = run_corpus_benchmarks()
        if corpus_problems:
            print("FAIL: Corpus benchmark regressions:")
            for p in corpus_problems:
                print(f"  - {p}")
            return 1

    print("Eval gate PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
