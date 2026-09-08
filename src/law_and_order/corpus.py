from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass

from .config import load_config

MIN_AGE_HOURS = 24
FETCH_FACTOR = 3


@dataclass(frozen=True, slots=True)
class PostRef:
    subreddit: str
    post_id: str
    permalink: str
    created_utc: float
    score: int
    split: str


def split_of(post_id: str) -> str:
    digest = hashlib.sha256(post_id.encode("utf-8")).hexdigest()
    return "train" if int(digest[-1], 16) < 8 else "holdout"


def is_aged(created_utc: float, now: float) -> bool:
    return now - created_utc >= MIN_AGE_HOURS * 3600


def require_credentials() -> tuple[str, str]:
    config = load_config()
    client_id = config.get("REDDIT_CLIENT_ID") or os.environ.get("REDDIT_CLIENT_ID")
    client_secret = config.get("REDDIT_CLIENT_SECRET") or os.environ.get("REDDIT_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError(
            "missing Reddit credentials: copy config.env.example to config.env (gitignored) and set "
            "REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET there, or export them as environment variables "
            "(config file wins; values are read at runtime only, never logged)"
        )
    return client_id, client_secret


def collect(
    fetch_posts: Callable[[str, int], Iterable[Mapping]],
    subreddit: str,
    target: int,
    now: float,
) -> tuple[PostRef, ...]:
    if target <= 0:
        return ()
    refs: list[PostRef] = []
    for post in fetch_posts(subreddit, target * FETCH_FACTOR):
        if not str(post.get("selftext", "")).strip():
            continue
        if not is_aged(float(post["created_utc"]), now):
            continue
        post_id = str(post["id"])
        refs.append(
            PostRef(
                subreddit=subreddit,
                post_id=post_id,
                permalink=str(post["permalink"]),
                created_utc=float(post["created_utc"]),
                score=int(post["score"]),
                split=split_of(post_id),
            )
        )
        if len(refs) == target:
            break
    return tuple(refs)


def manifest_line(ref: PostRef) -> str:
    record = {
        "subreddit": ref.subreddit,
        "post_id": ref.post_id,
        "permalink": ref.permalink,
        "created_utc": ref.created_utc,
        "score": ref.score,
        "split": ref.split,
    }
    return json.dumps(record, separators=(",", ":"), sort_keys=True) + "\n"
