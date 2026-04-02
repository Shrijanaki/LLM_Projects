from __future__ import annotations

from playwright.sync_api import sync_playwright

from job_agent.models import CandidateProfile, JobPosting


class ApplicationBot:
    def __init__(self, headless: bool = True, allow_auto_submit: bool = False) -> None:
        self.headless = headless
        self.allow_auto_submit = allow_auto_submit

    def run(self, posting: JobPosting, profile: CandidateProfile, mode: str) -> str:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            page.goto(posting.url, timeout=45_000)

            self._safe_fill(page, ["input[name='name']", "input#name"], profile.name)
            self._safe_fill(page, ["input[name='email']", "input#email"], profile.email)
            self._safe_fill(page, ["input[name='phone']", "input#phone"], profile.phone)
            self._safe_fill(page, ["input[name='location']", "input#location"], profile.location)

            status = "filled_waiting_user"
            if mode == "auto_apply" and self.allow_auto_submit:
                for selector in ["button[type='submit']", "button:has-text('Apply')"]:
                    if page.locator(selector).count() > 0:
                        page.locator(selector).first.click()
                        status = "submitted"
                        break

            browser.close()
            return status

    @staticmethod
    def _safe_fill(page, selectors: list[str], value: str) -> None:
        for selector in selectors:
            loc = page.locator(selector)
            if loc.count() > 0:
                loc.first.fill(value)
                return
