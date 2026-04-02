from __future__ import annotations

import re

from job_agent.models import CandidateProfile, JobPosting, MatchResult


WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+.#-]{1,}")


def _tokenize(text: str) -> set[str]:
    return {t.lower() for t in WORD_RE.findall(text or "")}


class RelevanceScorer:
    def __init__(self, threshold: float) -> None:
        self.threshold = threshold

    def score(self, posting: JobPosting, profile: CandidateProfile) -> MatchResult:
        job_tokens = _tokenize(f"{posting.title} {posting.description}")
        profile_skills = [s.strip() for s in profile.skills if s.strip()]
        skill_tokens = {s.lower() for s in profile_skills}

        matched_skills = [s for s in profile_skills if s.lower() in job_tokens]
        skill_score = len(matched_skills) / max(1, len(profile_skills))

        exp_scores: list[tuple[str, float]] = []
        for bullet in profile.experience_bullets:
            overlap = len(_tokenize(bullet) & job_tokens)
            denom = max(1, len(_tokenize(bullet)))
            exp_scores.append((bullet, overlap / denom))

        exp_scores.sort(key=lambda x: x[1], reverse=True)
        selected_experience = [b for b, s in exp_scores[:4] if s > 0]
        exp_score = sum(s for _, s in exp_scores[:4]) / max(1, len(exp_scores[:4]))

        keyword_density = len(skill_tokens & job_tokens) / max(1, len(skill_tokens))
        total = 0.55 * skill_score + 0.35 * exp_score + 0.10 * keyword_density

        return MatchResult(
            posting=posting,
            score=round(total, 4),
            matched_skills=matched_skills,
            selected_experience=selected_experience,
        )

    def is_relevant(self, result: MatchResult) -> bool:
        return result.score >= self.threshold
