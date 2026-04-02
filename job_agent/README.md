# Agentic Job Application Assistant

This project builds an **agentic AI workflow** that:
1. Scrapes job boards by skills (not only titles).
2. Scores jobs by resume relevance with a configurable threshold.
3. Generates a **unique resume + cover letter per job** without inventing new facts.
4. Auto-fills applications (or full auto-apply if enabled).
5. Tracks every step in a spreadsheet-compatible log.

## Design Principles
- **No hallucinated profile data**: all generated content is assembled from candidate-provided facts only.
- **Skill-first filtering**: jobs are matched by required skills + responsibilities.
- **Human-in-the-loop by default**: `fill_only` mode opens and fills forms but waits for user click.
- **Auditability**: every decision and artifact gets tracked.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp job_agent/config.example.yaml job_agent/config.yaml
python -m job_agent.main --config job_agent/config.yaml --mode fill_only
```

## Input Files
- `candidate_profile.yaml` — canonical source of candidate facts.
- `config.yaml` — job boards, thresholds, tracking destinations.

## Output
- `outputs/<job_id>/resume_<company>.md`
- `outputs/<job_id>/cover_letter_<company>.md`
- tracking rows written to `tracking.csv` and (optional) Google Sheets.

## Safety Controls
- Reject generation if any line in generated docs is not traceable to profile facts or static templates.
- Never click final submit unless `mode=auto_apply` and `allow_auto_submit=true`.
