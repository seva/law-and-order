from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from .measurement import LiveFrictionMonitor


class JsonlLedger:
    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._seq: int | None = None

    def touch(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.touch(exist_ok=True)

    def append(
        self,
        channel: str,
        speaker: str,
        counterpart: str | None,
        rulings: Iterable[tuple[str, str]],
        settled: bool,
    ) -> None:
        self.touch()
        record = {
            "seq": self._next_seq(),
            "channel": channel,
            "speaker": speaker,
            "counterpart": counterpart,
            "rulings": [list(ruling) for ruling in rulings],
            "settled": settled,
        }
        with self._path.open("a", encoding="utf-8", newline="\n") as ledger_file:
            ledger_file.write(json.dumps(record, separators=(",", ":"), sort_keys=True) + "\n")

    def _next_seq(self) -> int:
        if self._seq is None:
            self._seq = 0
            if self._path.exists():
                with self._path.open(encoding="utf-8") as ledger_file:
                    self._seq = sum(1 for _ in ledger_file)
        value = self._seq
        self._seq += 1
        return value


def replay(path: Path | str) -> LiveFrictionMonitor:
    monitor = LiveFrictionMonitor()
    ledger_path = Path(path)
    if not ledger_path.exists():
        return monitor
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        record = json.loads(line)
        monitor.record_message(
            record["channel"],
            record["speaker"],
            record["counterpart"],
            tuple(tuple(ruling) for ruling in record["rulings"]),
            record["settled"],
        )
    return monitor
