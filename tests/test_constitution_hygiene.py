import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHITECTURE_PATH = ROOT / "ARCHITECTURE.md"

MAX_LINE_CHARS = 600

NARRATIVE_VOCABULARY = ("critic", "falsif", "repaired", "antedat", "audit")
POINTER_PATTERN = re.compile(r"docs/|issue #|#\d+")


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
        lowered = line.lower()
        if any(word in lowered for word in NARRATIVE_VOCABULARY):
            if not POINTER_PATTERN.search(line):
                offenders.append(number)
    assert not offenders, f"narrative lines without a docs/ or issue pointer: {offenders}"
