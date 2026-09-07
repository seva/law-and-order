"""Executable record-law gate v1 (RCA A1, docs/rca-record-layer-drift-2026-09-06.md).

Declared v1 limitations (Lesson-Mechanism rule — the enforcer states its own scope):
- The density budget applies per physical line; a record split across lines would
  evade it. Markdown table rows cannot span lines (splitting is self-damaging),
  list items can — row-aware density is gate v2 (issue #10, A4).
- Pointer existence is verified for EVERY .md token on the line — docs/ paths
  and bare root-doc names alike, fail-closed: an unrecognized or nonexistent
  name fails even beside a live pointer (Critic N2, migration verdict
  docs/critic-migration-verdict-2026-09-07.md). Issue references (issue #N)
  are not existence-checkable from the repo and are accepted as declared.
- CJK fragment scan over committed records (root *.md, docs/): generation
  artifacts slipped non-English fragments into three records on 2026-09-06/07;
  the scan makes the class enforced instead of vigilance (Lesson-Mechanism
  rule). Records are English; quoted exceptions, if ever legitimate, amend
  this gate deliberately.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHITECTURE_PATH = ROOT / "ARCHITECTURE.md"

MAX_LINE_CHARS = 600

NARRATIVE_PATTERN = re.compile(r"critic|falsif|repaired|antedat|audit(?!able)", re.I)
ISSUE_POINTER_PATTERN = re.compile(r"issue #|#\d+")
MD_TOKEN_PATTERN = re.compile(r"\b[A-Za-z0-9_\-./]+\.md\b")
CJK_PATTERN = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
RECORD_GLOBS = ("*.md", "docs/*.md", "docs/*/*.md")


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
        md_targets = MD_TOKEN_PATTERN.findall(line)
        missing = [target for target in md_targets if not (ROOT / target).exists()]
        if missing:
            offenders.append((number, f"md pointers do not exist: {missing}"))
        elif not md_targets and not ISSUE_POINTER_PATTERN.search(line):
            offenders.append((number, "no pointer"))
    assert not offenders, f"narrative lines without a valid committed home: {offenders}"


def test_records_carry_no_non_english_fragments():
    offenders = []
    for pattern in RECORD_GLOBS:
        for path in ROOT.glob(pattern):
            text = path.read_text(encoding="utf-8")
            for number, line in enumerate(text.splitlines(), start=1):
                if CJK_PATTERN.search(line):
                    offenders.append(f"{path.relative_to(ROOT)}:{number}")
    assert not offenders, f"CJK fragments in committed records: {offenders}"
