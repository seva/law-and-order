from pathlib import Path

from law_and_order import RuleSet
from law_and_order.sim.engine import CRITICAL_FRICTION, WINDOW, run
from law_and_order.sim.population import Persona, default_population

RULESET_PATH = Path(__file__).resolve().parents[2] / "rulesets" / "v1.json"
ROUNDS = 60
SEED = 7

DEFAULT_BASELINE_TAIL = 0.5382051282051282
DEFAULT_INSTALLED_TAIL = 0.061080586080586086
DEFAULT_PUBLISHED = 45
DEFAULT_RESOLVED = 7


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


def unmatched_population() -> tuple[Persona, ...]:
    return (
        Persona(
            name="alpha",
            claims=("gamma delta epsilon", "zeta eta theta"),
            noise=("iota kappa lambda",),
            counterparts=("beta",),
        ),
        Persona(
            name="beta",
            claims=("mu nu xi", "omicron pi rho"),
            noise=("sigma tau upsilon",),
            counterparts=("alpha",),
        ),
    )


def test_unmatched_disputes_persist_without_rulings():
    population = unmatched_population()
    baseline, _, _ = run(population, ROUNDS, SEED)
    installed, published, resolved = run(
        population, ROUNDS, SEED, installed=True, ruleset=load_ruleset()
    )
    assert resolved == 0
    assert published == ()
    assert [record.friction for record in baseline] == [
        record.friction for record in installed
    ]


def affirm_settling_population() -> tuple[Persona, ...]:
    return (
        Persona(
            name="claimant",
            claims=("demand a refund for the goods",),
            noise=("gamma delta epsilon",),
            counterparts=("denier",),
        ),
        Persona(
            name="denier",
            claims=("I refuse to pay anything further",),
            noise=("zeta eta theta",),
            counterparts=("claimant",),
        ),
    )


def test_settlement_flows_through_affirm_on_appeal():
    installed, published, resolved = run(
        affirm_settling_population(), ROUNDS, SEED, installed=True, ruleset=load_ruleset()
    )
    baseline, _, _ = run(affirm_settling_population(), ROUNDS, SEED)
    assert resolved == 1
    assert len(published) >= 2
    assert sum(tail_frictions(installed)) / WINDOW < sum(tail_frictions(baseline)) / WINDOW


def natural_claim_population() -> tuple[Persona, ...]:
    return (
        Persona(
            name="buyer",
            claims=("I paid full price and I demand a complete refund.",),
            noise=("zeta eta theta",),
            counterparts=("seller",),
        ),
        Persona(
            name="seller",
            claims=("We will not issue a refund for that.",),
            noise=("iota kappa lambda",),
            counterparts=("buyer",),
        ),
    )


def test_natural_claim_phrasing_settles_through_due_process():
    population = natural_claim_population()
    installed, published, resolved = run(
        population, ROUNDS, SEED, installed=True, ruleset=load_ruleset()
    )
    baseline, _, _ = run(population, ROUNDS, SEED)
    assert resolved == 1
    assert len(published) >= 2
    assert any(ruling.action == "affirm" for ruling in published)
    assert sum(tail_frictions(installed)) / WINDOW < sum(tail_frictions(baseline)) / WINDOW


def overturn_population() -> tuple[Persona, ...]:
    return (
        Persona(
            name="buyer",
            claims=("full refund due immediately",),
            noise=("gamma delta epsilon",),
            counterparts=("seller",),
        ),
        Persona(
            name="seller",
            claims=("this is a breach of nothing we signed",),
            noise=("another breach of process",),
            counterparts=("buyer",),
        ),
    )


def test_counterclaim_marker_overturns_and_the_dispute_persists():
    v2 = RuleSet.from_json(
        (Path(__file__).resolve().parents[2] / "rulesets" / "v2.json").read_text(encoding="utf-8")
    )
    population = overturn_population()
    baseline, _, _ = run(population, ROUNDS, SEED)
    installed, published, resolved = run(
        population, ROUNDS, SEED, installed=True, ruleset=v2
    )
    assert resolved == 0
    assert len(published) >= 1
    assert [record.friction for record in baseline] == [
        record.friction for record in installed
    ]


def test_default_sim_seed7_measurement_is_pinned():
    ruleset = load_ruleset()
    baseline, _, _ = run(default_population(), ROUNDS, SEED)
    installed, published, resolved = run(
        default_population(), ROUNDS, SEED, installed=True, ruleset=ruleset
    )
    assert sum(tail_frictions(baseline)) / WINDOW == DEFAULT_BASELINE_TAIL
    assert sum(tail_frictions(installed)) / WINDOW == DEFAULT_INSTALLED_TAIL
    assert (
        DEFAULT_BASELINE_TAIL - DEFAULT_INSTALLED_TAIL
        == 0.47712454212454214
    )
    assert len(published) == DEFAULT_PUBLISHED
    assert resolved == DEFAULT_RESOLVED
