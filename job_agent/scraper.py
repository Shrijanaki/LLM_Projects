from __future__ import annotations

import hashlib
from typing import Iterable

import requests
from bs4 import BeautifulSoup

from job_agent.models import JobPosting


class JobScraper:
    def __init__(self, timeout_sec: int = 20) -> None:
        self.timeout_sec = timeout_sec

    def scrape_sources(self, sources: list[dict], max_jobs: int) -> list[JobPosting]:
        postings: list[JobPosting] = []
        for source in sources:
            stype = source["type"]
            name = source.get("name", stype)
            if stype == "greenhouse_json":
                postings.extend(self._scrape_greenhouse(source["url"], name))
            elif stype == "lever_json":
                postings.extend(self._scrape_lever(source["url"], name))
            elif stype == "generic_html":
                postings.extend(self._scrape_generic(source, name))
        uniq = {p.job_id: p for p in postings}
        return list(uniq.values())[:max_jobs]

    def _scrape_greenhouse(self, url: str, source_name: str) -> Iterable[JobPosting]:
        data = requests.get(url, timeout=self.timeout_sec).json()
        for item in data.get("jobs", []):
            desc = (item.get("content") or "")
            yield JobPosting(
                job_id=f"gh_{item['id']}",
                source=source_name,
                title=item.get("title", ""),
                company=item.get("absolute_url", "").split("/")[2] if item.get("absolute_url") else "Unknown",
                location=(item.get("location") or {}).get("name", ""),
                description=desc,
                url=item.get("absolute_url", ""),
            )

    def _scrape_lever(self, url: str, source_name: str) -> Iterable[JobPosting]:
        data = requests.get(url, timeout=self.timeout_sec).json()
        for item in data:
            desc = item.get("descriptionPlain", "") or item.get("description", "")
            company = item.get("hostedUrl", "").split("/")[2] if item.get("hostedUrl") else "Unknown"
            yield JobPosting(
                job_id=f"lever_{item['id']}",
                source=source_name,
                title=item.get("text", ""),
                company=company,
                location=(item.get("categories") or {}).get("location", ""),
                description=desc,
                url=item.get("hostedUrl", ""),
            )

    def _scrape_generic(self, source: dict, source_name: str) -> Iterable[JobPosting]:
        selectors = source["selectors"]
        html = requests.get(source["url"], timeout=self.timeout_sec).text
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select(selectors["job_card"])

        for card in cards:
            title = card.select_one(selectors["title"]).get_text(strip=True)
            location = card.select_one(selectors["location"]).get_text(strip=True)
            description = card.select_one(selectors["description"]).get_text(" ", strip=True)
            link_el = card.select_one(selectors["link"])
            url = link_el.get("href") if link_el else source["url"]
            raw_id = f"{source_name}|{title}|{location}|{url}"
            job_id = hashlib.md5(raw_id.encode("utf-8")).hexdigest()[:12]
            yield JobPosting(
                job_id=f"gen_{job_id}",
                source=source_name,
                title=title,
                company=source.get("company", "Unknown"),
                location=location,
                description=description,
                url=url,
            )
