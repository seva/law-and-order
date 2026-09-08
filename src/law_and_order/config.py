from __future__ import annotations

from pathlib import Path
from types import MappingProxyType

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.env"


def load_config(path: Path | str | None = None) -> MappingProxyType:
    config_path = Path(path) if path is not None else CONFIG_PATH
    if not config_path.exists():
        return MappingProxyType({})
    values: dict[str, str] = {}
    for number, raw_line in enumerate(config_path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, separator, value = stripped.partition("=")
        if not separator or not key.strip():
            raise ValueError(
                f"malformed line {number} in {config_path.name}: expected KEY=VALUE (line content withheld)"
            )
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if key in values:
            raise ValueError(f"duplicate key {key} at line {number} in {config_path.name}")
        values[key] = value
    return MappingProxyType(values)
