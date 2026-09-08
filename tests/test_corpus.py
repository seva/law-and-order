import hashlib
import inspect
import json
from dataclasses import FrozenInstanceError

import pytest

from law_and_order import config as config_module
from law_and_order.corpus import (
    MIN_AGE_HOURS,
    PostRef,
    collect,
    is_aged,
    manifest_line,
    require_credentials,
    split_of,
)

SENTINEL_TITLE = "zzq-title-sentinel-7731"
SENTINEL_BODY = "zzq-body-sentinel-4412 paid but never delivered"


def make_raw(post_id, created_utc, selftext=SENTINEL_BODY, title=SENTINEL_TITLE, score=3):
    return {
        "id": post_id,
        "permalink": f"/r/Scams/comments/{post_id}/x/",
        "created_utc": created_utc,
        "score": score,
        "title": title,
        "selftext": selftext,
    }


def test_postref_is_closed_frozen_and_contentless():
    fields = tuple(PostRef.__dataclass_fields__)
    assert fields == ("subreddit", "post_id", "permalink", "created_utc", "score", "split")
    ref = PostRef(
        subreddit="Scams",
        post_id="p1",
        permalink="/r/Scams/comments/p1/x/",
        created_utc=1000.0,
        score=2,
        split="train",
    )
    with pytest.raises(FrozenInstanceError):
        ref.post_id = "other"
    assert not hasattr(ref, "__dict__")


def test_split_of_is_deterministic_by_sha256_last_hex_digit():
    assert split_of("post0001") == "train"
    assert split_of("post0002") == "holdout"
    for post_id in ("a", "b", "t3_zzz", "9999"):
        expected = "train" if int(hashlib.sha256(post_id.encode("utf-8")).hexdigest()[-1], 16) < 8 else "holdout"
        assert split_of(post_id) == expected
        assert split_of(post_id) == split_of(post_id)


def test_split_covers_both_branches_on_a_realistic_id_range():
    splits = {split_of(f"id{i}") for i in range(200)}
    assert splits == {"train", "holdout"}


def test_min_age_is_legislated_at_24_hours():
    assert MIN_AGE_HOURS == 24


def test_is_aged_boundary_is_inclusive_at_24h():
    now = 1_000_000.0
    assert is_aged(now - 24 * 3600, now) is True
    assert is_aged(now - 24 * 3600 + 1, now) is False
    assert is_aged(now - 25 * 3600, now) is True
    assert is_aged(now - 1 * 3600, now) is False


def test_collect_admits_only_aged_selftext_posts_up_to_target():
    now = 1_000_000.0
    raw = (
        make_raw("old1", now - 30 * 3600),
        make_raw("new1", now - 1 * 3600),
        make_raw("old2", now - 48 * 3600, selftext=""),
        make_raw("old3", now - 72 * 3600),
        make_raw("old4", now - 96 * 3600),
    )
    calls = []

    def fetcher(subreddit, limit):
        calls.append((subreddit, limit))
        return iter(raw)

    refs = collect(fetcher, "Scams", target=2, now=now)
    assert calls == [("Scams", 2 * 3)]
    assert [ref.post_id for ref in refs] == ["old1", "old3"]
    assert all(is_aged(ref.created_utc, now) for ref in refs)
    assert all(ref.subreddit == "Scams" for ref in refs)
    assert refs[0].split == split_of("old1")


def test_collect_never_leaks_content_into_any_persisted_surface():
    now = 1_000_000.0
    raw = (make_raw("leak1", now - 30 * 3600),)
    refs = collect(lambda subreddit, limit: iter(raw), "Scams", target=5, now=now)
    assert len(refs) == 1
    serialized = repr(refs) + json.dumps([json.loads(manifest_line(ref)) for ref in refs])
    assert SENTINEL_TITLE not in serialized
    assert SENTINEL_BODY not in serialized
    assert "zzq" not in serialized


def test_collect_target_zero_yields_empty_without_fetching():
    calls = []

    def fetcher(subreddit, limit):
        calls.append(subreddit)
        return iter(())

    assert collect(fetcher, "Scams", target=0, now=1_000_000.0) == ()
    assert calls == []


def test_manifest_line_is_closed_sorted_and_contentless():
    ref = PostRef(
        subreddit="Scams",
        post_id="p1",
        permalink="/r/Scams/comments/p1/x/",
        created_utc=1000.0,
        score=2,
        split="holdout",
    )
    line = manifest_line(ref)
    assert line.endswith("\n")
    record = json.loads(line)
    assert tuple(sorted(record)) == ("created_utc", "permalink", "post_id", "score", "split", "subreddit")
    assert record == {
        "subreddit": "Scams",
        "post_id": "p1",
        "permalink": "/r/Scams/comments/p1/x/",
        "created_utc": 1000.0,
        "score": 2,
        "split": "holdout",
    }


def test_require_credentials_returns_pair_when_both_present(monkeypatch, tmp_path):
    monkeypatch.setattr(config_module, "CONFIG_PATH", tmp_path / "absent.env")
    monkeypatch.setenv("REDDIT_CLIENT_ID", "id-value")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "secret-value")
    assert require_credentials() == ("id-value", "secret-value")


def test_require_credentials_fails_fast_naming_both_vars(monkeypatch, tmp_path):
    monkeypatch.setattr(config_module, "CONFIG_PATH", tmp_path / "absent.env")
    monkeypatch.delenv("REDDIT_CLIENT_ID", raising=False)
    monkeypatch.delenv("REDDIT_CLIENT_SECRET", raising=False)
    with pytest.raises(RuntimeError) as excinfo:
        require_credentials()
    message = str(excinfo.value)
    assert "REDDIT_CLIENT_ID" in message
    assert "REDDIT_CLIENT_SECRET" in message


def test_require_credentials_error_never_echoes_the_present_value(monkeypatch, tmp_path):
    monkeypatch.setattr(config_module, "CONFIG_PATH", tmp_path / "absent.env")
    monkeypatch.setenv("REDDIT_CLIENT_ID", "id-sentinel-8817")
    monkeypatch.delenv("REDDIT_CLIENT_SECRET", raising=False)
    with pytest.raises(RuntimeError) as excinfo:
        require_credentials()
    assert "id-sentinel-8817" not in str(excinfo.value)
    assert "REDDIT_CLIENT_SECRET" in str(excinfo.value)


def test_corpus_module_never_imports_asyncpraw():
    import law_and_order.corpus as corpus_module

    source = inspect.getsource(corpus_module)
    assert "asyncpraw" not in source
    assert "import praw" not in source


def test_collect_signature_is_closed():
    assert list(inspect.signature(collect).parameters) == ["fetch_posts", "subreddit", "target", "now"]
