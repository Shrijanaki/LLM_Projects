from __future__ import annotations

from pathlib import Path
from typing import Iterable

from jinja2 import Environment, FileSystemLoader, select_autoescape

from job_agent.io_utils import ensure_dir
from job_agent.models import CandidateProfile, MatchResult


class DocumentGenerator:
    def __init__(self, templates_dir: str | Path, output_dir: str | Path) -> None:
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(enabled_extensions=("html", "xml")),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.output_dir = ensure_dir(output_dir)

    def generate(self, profile: CandidateProfile, result: MatchResult) -> tuple[Path, Path]:
        posting = result.posting
        selected_skills = result.matched_skills or profile.skills[:6]
        selected_experience = result.selected_experience or profile.experience_bullets[:3]
        top_focus = selected_skills[0] if selected_skills else "practical software delivery"

        resume_text = self.env.get_template("resume.md.j2").render(
            profile=profile,
            job=posting,
            selected_skills=selected_skills,
            selected_experience=selected_experience,
        )
        cover_text = self.env.get_template("cover_letter.md.j2").render(
            profile=profile,
            job=posting,
            selected_experience=selected_experience,
            top_job_focus=top_focus,
        )

        self._assert_no_hallucinations(profile, result, resume_text)
        self._assert_no_hallucinations(profile, result, cover_text)

        job_dir = ensure_dir(self.output_dir / posting.job_id)
        safe_company = posting.company.replace("/", "_")
        resume_path = job_dir / f"resume_{safe_company}.md"
        cover_path = job_dir / f"cover_letter_{safe_company}.md"
        resume_path.write_text(resume_text, encoding="utf-8")
        cover_path.write_text(cover_text, encoding="utf-8")
        return resume_path, cover_path

    def _assert_no_hallucinations(self, profile: CandidateProfile, result: MatchResult, text: str) -> None:
        allowed = self._build_allowed_phrases(profile, result)
        for line in text.splitlines():
            stripped = line.strip().lstrip("- ").strip()
            if not stripped:
                continue
            if stripped.startswith(("#", "##", "###", "Email:", "Location:", "LinkedIn:", "Dear", "Sincerely,", "I am excited", "I am particularly interested", "Thank you for your consideration", "I am excited to apply", "I am particularly")):
                continue
            if stripped in allowed:
                continue
            if "role" in stripped or "consideration" in stripped or "My experience aligns" in stripped:
                continue
            raise ValueError(f"Possible hallucinated line detected: {stripped}")

    @staticmethod
    def _build_allowed_phrases(profile: CandidateProfile, result: MatchResult) -> set[str]:
        phrases: set[str] = {
            profile.name,
            profile.email,
            profile.phone,
            profile.location,
            profile.linkedin,
            profile.github,
            profile.summary.strip(),
            result.posting.title,
            result.posting.company,
        }
        phrases.update(s.strip() for s in profile.skills)
        phrases.update(b.strip() for b in profile.experience_bullets)
        for p in profile.projects:
            phrases.add((p.get("name") or "").strip())
            phrases.update((b or "").strip() for b in p.get("bullets", []))
        phrases.update(e.strip() for e in profile.education)
        return {p for p in phrases if p}
