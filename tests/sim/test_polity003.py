import json
from pathlib import Path

from law_and_order import RuleSet
from law_and_order.sim.engine import WINDOW, run
from law_and_order.sim.population import Persona

ROOT = Path(__file__).resolve().parents[2]
MINDS_PATH = ROOT / "docs" / "polity-003" / "minds.json"
RULESET_PATH = ROOT / "rulesets" / "v2.json"
ROUNDS = 60
SEED = 7
BASELINE_TAIL = 0.4299404142767987
INSTALLED_TAIL = 0.26404000196569855
FULL_DELTA = 0.16590041231110014
REDUCED_DELTA = 0.0
RESOLVED_FULL = 4
RESOLVED_REDUCED = 0

NONSENSE_CLAIMS = (
    "alpha beta gamma delta",
    "epsilon zeta eta theta",
    "iota kappa lambda mu",
    "nu xi omicron pi",
)
NONSENSE_NOISE = ("rho sigma tau", "upsilon phi chi", "psi omega alpha")


def load_polity003_population() -> tuple[Persona, ...]:
    minds = json.loads(MINDS_PATH.read_text(encoding="utf-8"))
    return tuple(
        Persona(
            name=name,
            claims=tuple(mind["claims"]),
            noise=tuple(mind["noise"]),
            counterparts=tuple(mind["counterparts"]),
        )
        for name, mind in minds.items()
    )


def load_v2() -> RuleSet:
    return RuleSet.from_json(RULESET_PATH.read_text(encoding="utf-8"))


def reduced_v2() -> RuleSet:
    ruleset = load_v2()
    kept = tuple(rule for rule in ruleset.ordered() if rule.rule_id != "R7")
    assert len(kept) == len(ruleset.rules) - 1
    return RuleSet(rules=kept)


def nonsense_population() -> tuple[Persona, ...]:
    minds = json.loads(MINDS_PATH.read_text(encoding="utf-8"))
    return tuple(
        Persona(
            name=name,
            claims=NONSENSE_CLAIMS[: len(mind["claims"])],
            noise=NONSENSE_NOISE[: len(mind["noise"])],
            counterparts=tuple(mind["counterparts"]),
        )
        for name, mind in minds.items()
    )


def tail_friction(records) -> float:
    return sum(record.friction for record in records[-WINDOW:]) / WINDOW


def measure(population, ruleset):
    baseline, _, _ = run(population, ROUNDS, SEED)
    installed, _, resolved = run(population, ROUNDS, SEED, installed=True, ruleset=ruleset)
    return tail_friction(baseline) - tail_friction(installed), resolved


def test_counterpart_graph_is_symmetric_and_rich():
    minds = json.loads(MINDS_PATH.read_text(encoding="utf-8"))
    assert len(minds) == 8
    pairs = set()
    for name, mind in minds.items():
        for other in mind["counterparts"]:
            assert other in minds and other != name
            assert name in minds[other]["counterparts"]
            pairs.add(frozenset((name, other)))
    assert len(pairs) == 9


def test_resolution_is_graded_not_saturated():
    population = load_polity003_population()
    baseline, _, _ = run(population, ROUNDS, SEED)
    installed, _, resolved = run(
        population, ROUNDS, SEED, installed=True, ruleset=load_v2()
    )
    baseline_tail = tail_friction(baseline)
    installed_tail = tail_friction(installed)
    assert baseline_tail == BASELINE_TAIL
    assert installed_tail == INSTALLED_TAIL
    assert resolved == RESOLVED_FULL


def test_two_rulesets_give_two_deltas():
    population = load_polity003_population()
    full_delta, full_resolved = measure(population, load_v2())
    reduced_delta, reduced_resolved = measure(population, reduced_v2())
    assert full_delta == FULL_DELTA
    assert full_resolved == RESOLVED_FULL
    assert reduced_delta == REDUCED_DELTA
    assert reduced_resolved == RESOLVED_REDUCED


def test_nonsense_substitution_changes_the_delta():
    population = load_polity003_population()
    real_delta, _ = measure(population, load_v2())
    nonsense_delta, _ = measure(nonsense_population(), load_v2())
    assert real_delta == FULL_DELTA
    assert nonsense_delta == 0.0


def test_measurement_is_replay_stable():
    population = load_polity003_population()
    first, _ = measure(population, load_v2())
    second, _ = measure(population, load_v2())
    assert first == second
