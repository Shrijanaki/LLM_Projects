from job_agent.models import CandidateProfile, JobPosting
from job_agent.scoring import RelevanceScorer


def _profile() -> CandidateProfile:
    return CandidateProfile(
        name="Test User",
        email="t@example.com",
        phone="1",
        location="US",
        linkedin="l",
        github="g",
        summary="summary",
        skills=["Python", "SQL", "AWS"],
        experience_bullets=[
            "Built Python APIs for data processing",
            "Maintained Java services",
        ],
        projects=[],
        education=[],
    )


def test_relevance_scoring_high_when_skills_match() -> None:
    posting = JobPosting(
        job_id="1",
        source="x",
        title="Backend Engineer",
        company="C",
        location="Remote",
        description="Need Python and SQL on AWS for backend services",
        url="http://example.com",
    )
    scorer = RelevanceScorer(threshold=0.4)
    result = scorer.score(posting, _profile())

    assert result.score >= 0.4
    assert "Python" in result.matched_skills


def test_relevance_filter_rejects_irrelevant_jobs() -> None:
    posting = JobPosting(
        job_id="2",
        source="x",
        title="Nurse",
        company="H",
        location="Local",
        description="Clinical care and patient bedside support",
        url="http://example.com/2",
    )
    scorer = RelevanceScorer(threshold=0.4)
    result = scorer.score(posting, _profile())

    assert scorer.is_relevant(result) is False
