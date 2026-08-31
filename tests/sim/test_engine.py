from pathlib import Path

from law_and_order import RuleSet
from law_and_order.sim.engine import CRITICAL_FRICTION, WINDOW, run
from law_and_order.sim.population import default_population

RULESET_PATH = Path(__file__).resolve().parents[2] / "rulesets" / "v1.json"
ROUNDS = 60
SEED = 7


def load_ruleset() -> RuleSet:
    return RuleSet.from_json(RULESET_PATH.read_text(encoding="utf-8"))


def tail_frictions(history) -> list[float]:
    return [record.friction for record in history[-WINDOW:]]


def test_run_is_deterministic():
    population = default_population()
    ruleset = load_ruleset()
    first, published_first, resolved_first = run(
        population, ROUNDS, SEED, installed=True, ruleset=ruleset
    )
    second, published_second, resolved_second = run(
        population, ROUNDS, SEED, installed=True, ruleset=ruleset
    )
    assert [r.friction for r in first] == [r.friction for r in second]
    assert len(published_first) == len(published_second)
    assert resolved_first == resolved_second


def test_baseline_sustains_disorder():
    history, published, resolved = run(default_population(), ROUNDS, SEED)
    assert sum(tail_frictions(history)) / WINDOW >= CRITICAL_FRICTION
    assert published == ()
    assert resolved == 0


def test_installed_transitions_to_order():
    history, published, resolved = run(
        default_population(), ROUNDS, SEED, installed=True, ruleset=load_ruleset()
    )
    assert sum(tail_frictions(history)) / WINDOW < CRITICAL_FRICTION
    assert len(published) > 0
    assert resolved > 0


def test_friction_delta_is_positive():
    population = default_population()
    baseline, _, _ = run(population, ROUNDS, SEED)
    installed, _, _ = run(population, ROUNDS, SEED, installed=True, ruleset=load_ruleset())
    baseline_tail = sum(tail_frictions(baseline)) / WINDOW
    installed_tail = sum(tail_frictions(installed)) / WINDOW
    assert baseline_tail - installed_tail > 0
