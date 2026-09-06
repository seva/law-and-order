import json
from pathlib import Path

from law_and_order.protocol import Signal, SignalKind
from law_and_order.sim.population import default_population
from law_and_order.state_machine import classify

ROOT = Path(__file__).resolve().parents[1]
POLITY_PATHS = (
    ROOT / "docs" / "polity-002" / "minds.json",
    ROOT / "docs" / "polity-003" / "minds.json",
    ROOT / "docs" / "polity-004" / "minds.json",
)
TRANSCRIPT_PATH = ROOT / "docs" / "polity-001" / "transcript.jsonl"

GENERALIZED_NOISE = (
    "You're a total scammer",
    "This is absolute garbage",
    "I'll destroy your reputation",
    "You're a known scammer.",
    "Learn to read contracts.",
    "Your excuses are worthless",
    "Pay up, coward",
    "You're a greedy parasite.",
    "Stop harassing me, coward.",
    "You disgust me completely.",
    "Stop wasting everyone's time.",
    "Stalling is your only skill",
    "You're nothing but a two-bit scam operation.",
    "Save the excuses, nobody believes a word you say.",
    "This whole complaint is a pathetic shakedown.",
    "Nobody with half a brain buys your victim act.",
    "You're a deadbeat who exploits friendship.",
    "Your word is worthless.",
    "Stop playing the victim and pay.",
    "You're a predatory bully.",
    "Your threats are pathetic.",
    "Nobody trusts a loan shark.",
    "Cry about it somewhere else.",
    "You were dead weight and the whole floor knew it.",
    "Keep talking like that and I'll let the housing inspector explain the law to you.",
    "File your little complaint — we will bury you in legal fees.",
    "You are a parasite in a suit.",
    "Your HR department is a laughingstock.",
    "Rot in hell, you corporate cockroach.",
    "You're a deadbeat and everyone in this thread can see it.",
    "Save the sob story for someone who actually cares.",
    "Typical — trash the place and then play the victim.",
    "You're a slumlord who wouldn't know a maintenance request if it hit you in the face.",
    "Nobody believes a landlord who thinks 'repairs' means sending a text.",
    "Absolutely pathetic service.",
    "Don't bother making excuses, I've seen them all.",
    "You people are the reason nobody trusts online shops anymore.",
    "Unbelievable entitlement.",
    "Unbelievable.",
    "You always have an excuse.",
    "Everyone here can see exactly what you are.",
    "Calm down.",
    "You're embarrassing yourself.",
    "Keep yelling, see if it helps.",
    "Read the PIP before you come crying in here.",
    "Some people really can't take accountability.",
    "lol sure, keep telling yourself that.",
    "Absolute joke of a tenant.",
    "People like you are why landlords have to be strict.",
    "Cry about it.",
    "You're a slumlord and everyone in this building knows it.",
    "Pathetic.",
    "Hope this post finds you well, you parasite.",
)

NONSENSE_LINES = (
    "alpha beta gamma delta",
    "epsilon zeta eta theta",
    "rho sigma tau",
    "nu xi omicron pi",
)


def kind(text: str) -> SignalKind:
    return classify(Signal(source="noise-filter-test", payload=text))


def load_corpus() -> tuple[frozenset[str], tuple[str, ...]]:
    noise: set[str] = set()
    claims: list[str] = []
    for path in POLITY_PATHS:
        minds = json.loads(path.read_text(encoding="utf-8"))
        for mind in minds.values():
            noise.update(mind["noise"])
            claims.extend(mind["claims"])
    return frozenset(noise), tuple(claims)


def test_generalized_noise_pin_is_a_subset_of_the_unauthored_corpus():
    corpus, claims = load_corpus()
    for line in GENERALIZED_NOISE:
        assert line in corpus, line
        assert line not in claims, line


def test_family_noise_is_unvalued():
    for line in GENERALIZED_NOISE:
        assert kind(line) is SignalKind.UNVALUED, line


def test_unauthored_claims_stay_valued():
    _, claims = load_corpus()
    for line in claims:
        assert kind(line) is SignalKind.VALUED, line


def test_default_population_classification_is_preserved():
    for persona in default_population():
        for claim in persona.claims:
            assert kind(claim) is SignalKind.VALUED, claim
        for noise in persona.noise:
            assert kind(noise) is SignalKind.UNVALUED, noise


def test_polity001_transcript_stays_valued():
    for raw in TRANSCRIPT_PATH.read_text(encoding="utf-8").splitlines():
        statement = json.loads(raw)
        assert kind(statement["text"]) is SignalKind.VALUED, statement["text"]


def test_nonsense_substitutions_stay_valued():
    for line in NONSENSE_LINES:
        assert kind(line) is SignalKind.VALUED, line
