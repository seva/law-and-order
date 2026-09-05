import json
from pathlib import Path

from law_and_order import RuleSet
from law_and_order.sim.engine import WINDOW, run
from law_and_order.sim.population import Persona

ROOT = Path(__file__).resolve().parents[2]
MINDS_PATH = ROOT / "docs" / "polity-004" / "minds.json"
RULESET_PATH = ROOT / "rulesets" / "v2.json"
ROUNDS = 60
SEED = 7

BASELINE_TAIL = 0.4299404142767987
INSTALLED_TAIL = 0.4299404142767987
FULL_DELTA = 0.0
REDUCED_DELTA = 0.0
RESOLVED_FULL = 0
PUBLISHED_FULL = 24
PUBLISHED_REDUCED = 5

NONSENSE_CLAIMS = (
    "alpha beta gamma delta",
    "epsilon zeta eta theta",
    "iota kappa lambda mu",
    "nu xi omicron pi",
)
NONSENSE_NOISE = ("rho sigma tau", "upsilon phi chi", "psi omega alpha")


def load_polity004_population() -> tuple[Persona, ...]:
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
    installed, published, resolved = run(population, ROUNDS, SEED, installed=True, ruleset=ruleset)
    return tail_friction(baseline) - tail_friction(installed), resolved, len(published), installed


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


def test_legislation_settles_nothing_on_honest_content():
    population = load_polity004_population()
    delta, resolved, published, installed = measure(population, load_v2())
    assert delta == FULL_DELTA
    assert resolved == RESOLVED_FULL
    assert published == PUBLISHED_FULL
    baseline, _, _ = run(population, ROUNDS, SEED)
    assert tail_friction(installed) == INSTALLED_TAIL
    assert tail_friction(installed) == tail_friction(baseline)


def test_probe_and_nonsense_settle_nothing_but_publish_diverges():
    population = load_polity004_population()
    reduced_delta, reduced_resolved, reduced_published, _ = measure(population, reduced_v2())
    nonsense_delta, nonsense_resolved, nonsense_published, _ = measure(nonsense_population(), load_v2())
    assert reduced_delta == REDUCED_DELTA
    assert reduced_resolved == 0
    assert reduced_published == PUBLISHED_REDUCED
    assert nonsense_delta == FULL_DELTA
    assert nonsense_resolved == 0
    assert nonsense_published == 0
    assert PUBLISHED_FULL != nonsense_published
    assert PUBLISHED_REDUCED != nonsense_published


def test_empty_ruleset_settles_and_publishes_nothing():
    population = load_polity004_population()
    empty_delta, empty_resolved, empty_published, _ = measure(population, RuleSet(rules=()))
    assert empty_delta == FULL_DELTA
    assert empty_resolved == 0
    assert empty_published == 0


def test_measurement_is_replay_stable():
    population = load_polity004_population()
    first, _, _, _ = measure(population, load_v2())
    second, _, _, _ = measure(population, load_v2())
    assert first == second
