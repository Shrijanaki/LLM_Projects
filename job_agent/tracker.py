from __future__ import annotations

import csv
from datetime import datetime, UTC
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

from job_agent.models import MatchResult


class ApplicationTracker:
    def __init__(self, csv_path: str, gsheets_cfg: dict | None = None) -> None:
        self.csv_path = Path(csv_path)
        self.gsheets_cfg = gsheets_cfg or {"enabled": False}
        self._ensure_csv_header()

    def record(
        self,
        result: MatchResult,
        status: str,
        resume_path: str | None = None,
        cover_path: str | None = None,
        notes: str = "",
    ) -> None:
        row = [
            datetime.now(UTC).isoformat(),
            result.posting.job_id,
            result.posting.source,
            result.posting.company,
            result.posting.title,
            result.posting.url,
            f"{result.score:.4f}",
            ", ".join(result.matched_skills),
            status,
            resume_path or "",
            cover_path or "",
            notes,
        ]

        with self.csv_path.open("a", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow(row)

        if self.gsheets_cfg.get("enabled"):
            self._append_google_sheet(row)

    def _ensure_csv_header(self) -> None:
        if self.csv_path.exists():
            return
        with self.csv_path.open("w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow(
                [
                    "timestamp_utc",
                    "job_id",
                    "source",
                    "company",
                    "title",
                    "url",
                    "score",
                    "matched_skills",
                    "status",
                    "resume_path",
                    "cover_letter_path",
                    "notes",
                ]
            )

    def _append_google_sheet(self, row: list[str]) -> None:
        creds = Credentials.from_service_account_file(
            self.gsheets_cfg["service_account_json"],
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        client = gspread.authorize(creds)
        sh = client.open_by_key(self.gsheets_cfg["spreadsheet_id"])
        worksheet = sh.worksheet(self.gsheets_cfg.get("worksheet", "Applications"))
        worksheet.append_row(row, value_input_option="RAW")
