import json
from pathlib import Path

from law_and_order import RuleSet
from law_and_order.sim.engine import WINDOW, run
from law_and_order.sim.population import Persona

ROOT = Path(__file__).resolve().parents[2]
RULESET_PATH = ROOT / "rulesets" / "v2.json"
MINDS_PATH = ROOT / "docs" / "polity-002" / "minds.json"
ROUNDS = 60
SEED = 7
COUNTERPARTS = {
    "buyer": ("seller", "creditor"),
    "seller": ("buyer", "debtor"),
    "creditor": ("debtor", "buyer"),
    "debtor": ("creditor", "seller"),
}

NONSENSE_CLAIMS = (
    "alpha beta gamma delta",
    "epsilon zeta eta theta",
    "iota kappa lambda mu",
    "nu xi omicron pi",
)
NONSENSE_NOISE = ("rho sigma tau", "upsilon phi chi", "psi omega alpha")


def load_polity002_population() -> tuple[Persona, ...]:
    minds = json.loads(MINDS_PATH.read_text(encoding="utf-8"))
    return tuple(
        Persona(
            name=name,
            claims=tuple(mind["claims"]),
            noise=tuple(mind["noise"]),
            counterparts=COUNTERPARTS[name],
        )
        for name, mind in minds.items()
    )


def load_ruleset() -> RuleSet:
    return RuleSet.from_json(RULESET_PATH.read_text(encoding="utf-8"))


def load_empty_ruleset() -> RuleSet:
    return RuleSet.from_json("[]")


def nonsense_population() -> tuple[Persona, ...]:
    minds = json.loads(MINDS_PATH.read_text(encoding="utf-8"))
    return tuple(
        Persona(
            name=name,
            claims=NONSENSE_CLAIMS[: len(mind["claims"])],
            noise=NONSENSE_NOISE[: len(mind["noise"])],
            counterparts=COUNTERPARTS[name],
        )
        for name, mind in minds.items()
    )


def tail_friction(records) -> float:
    return sum(record.friction for record in records[-WINDOW:]) / WINDOW


def friction_delta(population, ruleset) -> float:
    baseline, _, _ = run(population, ROUNDS, SEED)
    installed, _, _ = run(population, ROUNDS, SEED, installed=True, ruleset=ruleset)
    return tail_friction(baseline) - tail_friction(installed)


def test_nonsense_substitution_changes_the_delta():
    population = load_polity002_population()
    real_delta = friction_delta(population, load_ruleset())
    nonsense_delta = friction_delta(nonsense_population(), load_ruleset())
    assert real_delta > 0
    assert nonsense_delta != real_delta


def test_empty_ruleset_changes_the_delta():
    population = load_polity002_population()
    real_delta = friction_delta(population, load_ruleset())
    empty_delta = friction_delta(population, load_empty_ruleset())
    assert empty_delta != real_delta


def test_polity002_measurement_is_replay_stable():
    population = load_polity002_population()
    assert friction_delta(population, load_ruleset()) == friction_delta(
        population, load_ruleset()
    )
