from __future__ import annotations

import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class Rule:
    rule_id: str
    match: str
    action: str


@dataclass(frozen=True, slots=True)
class RuleSet:
    rules: tuple[Rule, ...]

    @classmethod
    def from_json(cls, raw: str) -> RuleSet:
        items = json.loads(raw)
        if not isinstance(items, list):
            raise ValueError("ruleset artifact must be a JSON array of rules")
        return cls(rules=tuple(Rule(**item) for item in items))

    def ordered(self) -> tuple[Rule, ...]:
        return tuple(sorted(self.rules, key=lambda rule: rule.rule_id))

    def canonical(self) -> str:
        return json.dumps(
            [asdict(rule) for rule in self.ordered()],
            sort_keys=True,
            separators=(",", ":"),
        )

    def compressed_size(self) -> int:
        return len(self.canonical().encode("utf-8"))
