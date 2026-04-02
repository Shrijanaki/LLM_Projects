from __future__ import annotations

import argparse
from pathlib import Path

from job_agent.apply_bot import ApplicationBot
from job_agent.generator import DocumentGenerator
from job_agent.io_utils import load_candidate_profile, load_yaml
from job_agent.scoring import RelevanceScorer
from job_agent.scraper import JobScraper
from job_agent.tracker import ApplicationTracker


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Agentic AI job matcher and applier")
    parser.add_argument("--config", required=True, help="Path to config YAML")
    parser.add_argument(
        "--profile",
        default="job_agent/candidate_profile.yaml",
        help="Path to candidate profile YAML",
    )
    parser.add_argument(
        "--mode",
        choices=["fill_only", "auto_apply"],
        default="fill_only",
        help="fill_only: fill forms and stop, auto_apply: submit when enabled",
    )
    return parser.parse_args()


def run(config_path: str, profile_path: str, mode: str) -> None:
    config = load_yaml(config_path)
    profile = load_candidate_profile(profile_path)

    scraper = JobScraper()
    scorer = RelevanceScorer(threshold=config["threshold"])
    generator = DocumentGenerator(
        templates_dir=Path(__file__).parent / "templates",
        output_dir=config.get("output_dir", "outputs"),
    )
    tracker = ApplicationTracker(
        csv_path=config["tracking"]["csv_path"],
        gsheets_cfg=config["tracking"].get("google_sheets", {}),
    )
    apply_bot = ApplicationBot(
        headless=config["application"].get("headless", False),
        allow_auto_submit=config["application"].get("allow_auto_submit", False),
    )

    postings = scraper.scrape_sources(config["sources"], max_jobs=config.get("max_jobs", 50))

    for posting in postings:
        result = scorer.score(posting, profile)
        if not scorer.is_relevant(result):
            tracker.record(result, status="rejected_low_relevance")
            continue

        resume_path, cover_path = generator.generate(profile, result)

        status = apply_bot.run(posting, profile, mode=mode)
        tracker.record(
            result,
            status=status,
            resume_path=str(resume_path),
            cover_path=str(cover_path),
            notes=f"threshold={config['threshold']}",
        )


if __name__ == "__main__":
    args = parse_args()
    run(args.config, args.profile, args.mode)
