from pathlib import Path

from law_and_order import RuleSet
from law_and_order.protocol import Phase
from law_and_order.sim.engine import CRITICAL_FRICTION, WINDOW, run
from law_and_order.sim.population import default_population

ROUNDS = 60
SEED = 7


def main() -> None:
    ruleset_path = Path(__file__).resolve().parent.parent / "rulesets" / "v1.json"
    ruleset = RuleSet.from_json(ruleset_path.read_text(encoding="utf-8"))
    population = default_population()

    baseline, _, _ = run(population, ROUNDS, SEED)
    installed, published, resolved = run(
        population, ROUNDS, SEED, installed=True, ruleset=ruleset
    )

    print(f"round  baseline  installed")
    for index in range(0, ROUNDS, 5):
        print(f"{index:>5}  {baseline[index].friction:>8.3f}  {installed[index].friction:>9.3f}")

    baseline_tail = sum(record.friction for record in baseline[-WINDOW:]) / WINDOW
    installed_tail = sum(record.friction for record in installed[-WINDOW:]) / WINDOW
    baseline_phase = Phase.ORDERED if baseline_tail < CRITICAL_FRICTION else Phase.DISORDERED
    installed_phase = Phase.ORDERED if installed_tail < CRITICAL_FRICTION else Phase.DISORDERED

    print()
    print(f"baseline tail friction:  {baseline_tail:.3f}  ({baseline_phase.value})")
    print(f"installed tail friction: {installed_tail:.3f}  ({installed_phase.value})")
    print(f"friction delta:          {baseline_tail - installed_tail:.3f}")
    print(f"rulings published:       {len(published)}")
    print(f"disputes resolved:       {resolved}")


if __name__ == "__main__":
    main()
