from __future__ import annotations

from pathlib import Path
import yaml

from job_agent.models import CandidateProfile


def load_yaml(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_candidate_profile(path: str | Path) -> CandidateProfile:
    data = load_yaml(path)
    return CandidateProfile(**data)


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
