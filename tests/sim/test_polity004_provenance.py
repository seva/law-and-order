import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLITY = ROOT / "docs" / "polity-004"
MINDS_PATH = POLITY / "minds.json"

PERSONA_DOMAIN = {
    "customer": "market",
    "vendor": "market",
    "lender": "debt",
    "borrower": "debt",
    "employer": "workplace",
    "worker": "workplace",
    "landlord": "tenancy",
    "tenant": "tenancy",
}


def load_outputs() -> dict:
    cached = {}
    for domain in set(PERSONA_DOMAIN.values()):
        path = POLITY / "provenance" / f"{domain}.output.json"
        cached[domain] = json.loads(path.read_text(encoding="utf-8"))
    return cached


def test_every_line_traces_verbatim_to_a_persisted_output():
    minds = json.loads(MINDS_PATH.read_text(encoding="utf-8"))
    outputs = load_outputs()
    assert set(minds) == set(PERSONA_DOMAIN)
    for name, mind in minds.items():
        source = outputs[PERSONA_DOMAIN[name]][name]
        assert mind["claims"] == source["claims"], name
        assert mind["noise"] == source["noise"], name


def test_outputs_carry_exactly_the_expected_personas():
    outputs = load_outputs()
    for domain, pair in {
        "market": ("customer", "vendor"),
        "debt": ("lender", "borrower"),
        "workplace": ("employer", "worker"),
        "tenancy": ("landlord", "tenant"),
    }.items():
        assert set(outputs[domain]) == set(pair), domain


def test_no_content_selection_every_persona_has_full_lines():
    minds = json.loads(MINDS_PATH.read_text(encoding="utf-8"))
    for name, mind in minds.items():
        assert len(mind["claims"]) == 4, name
        assert len(mind["noise"]) == 3, name
