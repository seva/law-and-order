import inspect
from pathlib import Path

import pytest

from law_and_order import config as config_module
from law_and_order.config import CONFIG_PATH, load_config

REPO_ROOT = Path(__file__).resolve().parents[1]


def write_config(tmp_path, text):
    path = tmp_path / "config.env"
    path.write_text(text, encoding="utf-8")
    return path


def test_load_config_parses_key_value_pairs(tmp_path):
    path = write_config(tmp_path, "A=1\nB=two words\n")
    assert load_config(path) == {"A": "1", "B": "two words"}


def test_load_config_skips_blank_lines_and_full_line_comments(tmp_path):
    path = write_config(tmp_path, "\n# comment\n  \nA=1\n#B=2\n")
    assert load_config(path) == {"A": "1"}


def test_load_config_does_not_strip_inline_hash_from_values(tmp_path):
    path = write_config(tmp_path, "A=value#with-hash\n")
    assert load_config(path) == {"A": "value#with-hash"}


def test_load_config_strips_matching_surrounding_quotes(tmp_path):
    path = write_config(tmp_path, 'A="quoted"\nB=\'single\'\nC="mismatched\'\n')
    assert load_config(path) == {"A": "quoted", "B": "single", "C": '"mismatched\''}


def test_load_config_missing_file_is_empty_never_raises(tmp_path):
    assert load_config(tmp_path / "absent.env") == {}


def test_load_config_missing_default_path_is_empty_never_raises(monkeypatch, tmp_path):
    monkeypatch.setattr(config_module, "CONFIG_PATH", tmp_path / "absent.env")
    assert load_config() == {}


def test_load_config_fails_loud_on_duplicate_keys(tmp_path):
    path = write_config(tmp_path, "A=1\nA=2\n")
    with pytest.raises(ValueError, match="duplicate key.*A"):
        load_config(path)


def test_load_config_fails_loud_on_malformed_line_without_echoing_it(tmp_path):
    path = write_config(tmp_path, "A=1\nzzq-secret-shaped-line-without-equals\n")
    with pytest.raises(ValueError) as excinfo:
        load_config(path)
    message = str(excinfo.value)
    assert "line 2" in message
    assert "zzq-secret-shaped-line-without-equals" not in message


def test_load_config_returns_an_immutable_mapping(tmp_path):
    path = write_config(tmp_path, "A=1\n")
    loaded = load_config(path)
    with pytest.raises(TypeError):
        loaded["A"] = "mutated"


def test_load_config_signature_is_optional_path_only():
    assert list(inspect.signature(load_config).parameters) == ["path"]


def test_gitignore_covers_the_real_config():
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "config.env" in gitignore.splitlines()


def test_template_is_committed_and_documents_both_credential_keys_with_no_values():
    template = (REPO_ROOT / "config.env.example").read_text(encoding="utf-8")
    lines = {
        line.split("=", 1)[0].strip(): line.split("=", 1)[1].strip()
        for line in template.splitlines()
        if "=" in line and not line.strip().startswith("#")
    }
    assert lines["REDDIT_CLIENT_ID"] == ""
    assert lines["REDDIT_CLIENT_SECRET"] == ""


def test_config_path_is_the_repo_root_config_env():
    assert CONFIG_PATH == REPO_ROOT / "config.env"


def test_corpus_credentials_prefer_config_file_over_env(monkeypatch, tmp_path):
    from law_and_order.corpus import require_credentials

    path = write_config(tmp_path, "REDDIT_CLIENT_ID=file-id\nREDDIT_CLIENT_SECRET=file-secret\n")
    monkeypatch.setattr(config_module, "CONFIG_PATH", path)
    monkeypatch.setenv("REDDIT_CLIENT_ID", "env-id")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "env-secret")
    assert require_credentials() == ("file-id", "file-secret")


def test_corpus_credentials_fall_back_to_env_when_file_absent(monkeypatch, tmp_path):
    from law_and_order.corpus import require_credentials

    monkeypatch.setattr(config_module, "CONFIG_PATH", tmp_path / "absent.env")
    monkeypatch.setenv("REDDIT_CLIENT_ID", "env-id")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "env-secret")
    assert require_credentials() == ("env-id", "env-secret")


def test_corpus_credentials_error_names_the_config_file_and_template(monkeypatch, tmp_path):
    from law_and_order.corpus import require_credentials

    monkeypatch.setattr(config_module, "CONFIG_PATH", tmp_path / "absent.env")
    monkeypatch.delenv("REDDIT_CLIENT_ID", raising=False)
    monkeypatch.delenv("REDDIT_CLIENT_SECRET", raising=False)
    with pytest.raises(RuntimeError) as excinfo:
        require_credentials()
    message = str(excinfo.value)
    assert "config.env" in message
    assert "config.env.example" in message
    assert "REDDIT_CLIENT_ID" in message
    assert "REDDIT_CLIENT_SECRET" in message
