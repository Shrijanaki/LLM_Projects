from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class JobPosting:
    job_id: str
    source: str
    title: str
    company: str
    location: str
    description: str
    url: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CandidateProfile:
    name: str
    email: str
    phone: str
    location: str
    linkedin: str
    github: str
    summary: str
    skills: list[str]
    experience_bullets: list[str]
    projects: list[dict[str, Any]]
    education: list[str]


@dataclass
class MatchResult:
    posting: JobPosting
    score: float
    matched_skills: list[str]
    selected_experience: list[str]
