"""Executable record-law gate v1 (RCA A1, docs/rca-record-layer-drift-2026-09-06.md).

Declared v1 limitations (Lesson-Mechanism rule — the enforcer states its own scope):
- The density budget applies per physical line; a record split across lines would
  evade it. Markdown table rows cannot span lines (splitting is self-damaging),
  list items can — row-aware density is gate v2 (issue #10, A4).
- Pointer existence is verified for every docs/ target on the line — a dead
  pointer beside a live one is stale-record drift and fails; issue references
  (issue #N) are not existence-checkable from the repo and are accepted as
  declared.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHITECTURE_PATH = ROOT / "ARCHITECTURE.md"

MAX_LINE_CHARS = 600

NARRATIVE_PATTERN = re.compile(r"critic|falsif|repaired|antedat|audit(?!able)", re.I)
POINTER_PATTERN = re.compile(r"docs/|issue #|#\d+")
DOCS_TARGET_PATTERN = re.compile(r"docs/[A-Za-z0-9_\-./]+")


def test_architecture_lines_stay_within_the_density_budget():
    text = ARCHITECTURE_PATH.read_text(encoding="utf-8")
    over = [
        (number, len(line))
        for number, line in enumerate(text.splitlines(), start=1)
        if len(line) > MAX_LINE_CHARS
    ]
    assert not over, f"lines over {MAX_LINE_CHARS} chars: {over}"


def test_falsification_narrative_points_to_its_committed_home():
    text = ARCHITECTURE_PATH.read_text(encoding="utf-8")
    offenders = []
    for number, line in enumerate(text.splitlines(), start=1):
        if not NARRATIVE_PATTERN.search(line):
            continue
        if not POINTER_PATTERN.search(line):
            offenders.append((number, "no pointer"))
            continue
        targets = DOCS_TARGET_PATTERN.findall(line)
        missing = [target for target in targets if not (ROOT / target).exists()]
        if missing:
            offenders.append((number, f"docs pointers do not exist: {missing}"))
    assert not offenders, f"narrative lines without a valid committed home: {offenders}"
