import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLITY = ROOT / "docs" / "polity-004"
MINDS_PATH = POLITY / "minds.json"
CORROBORATION_PATH = POLITY / "corroboration.json"

CORROBORATED_INSTANCES = {
    "market": "ses_f8fd7144bffezNkepE7ZUxei76",
    "debt": "ses_f8fd704c7ffejNm2oI2R694Y2f",
    "workplace": "ses_f8fd6f6dcffegYkGR2EDk28m90",
    "tenancy": "ses_f8fd6e858ffe8cEKGxa9FTIfci",
}

GENERATION_WINDOW_START_MS = 1788588125000
GENERATION_WINDOW_END_MS = 1788588137000

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


def load_corroboration() -> dict:
    return json.loads(CORROBORATION_PATH.read_text(encoding="utf-8"))


def test_corroboration_covers_exactly_the_recorded_instances():
    sessions = load_corroboration()["sessions"]
    by_domain = {session["domain"]: session for session in sessions}
    assert set(by_domain) == set(CORROBORATED_INSTANCES)
    parents = set()
    for domain, session in by_domain.items():
        assert session["instance_id"] == CORROBORATED_INSTANCES[domain], domain
        assert session["agent"] == "general", domain
        parents.add(session["parent_id"])
    assert len(parents) == 1


def test_corroboration_sessions_fall_inside_the_disclosed_generation_window():
    for session in load_corroboration()["sessions"]:
        assert GENERATION_WINDOW_START_MS <= session["time_created_ms"] < GENERATION_WINDOW_END_MS, session["domain"]


def test_corroboration_is_single_pass_one_request_one_response():
    for session in load_corroboration()["sessions"]:
        roles = [message["role"] for message in session["messages"]]
        assert roles == ["user", "assistant"], session["domain"]
        for message in session["messages"]:
            text_parts = [part for part in message["parts"] if part["type"] == "text"]
            assert len(text_parts) == 1, message["id"]


def test_corroborated_sent_prompt_is_the_committed_mandate_body():
    for session in load_corroboration()["sessions"]:
        domain = session["domain"]
        mandate = (POLITY / "mandates" / f"{domain}.md").read_text(encoding="utf-8")
        mandate_body = mandate.split("\n", 2)[2]
        sent_prompt = session["messages"][0]["text"]["value"]
        assert sent_prompt.strip() == mandate_body.strip(), domain


def test_corroborated_output_text_parses_to_the_persisted_output():
    outputs = load_outputs()
    for session in load_corroboration()["sessions"]:
        domain = session["domain"]
        from_store = json.loads(session["messages"][1]["text"]["value"])
        assert from_store == outputs[domain], domain
