"""
Hockey scraper using BeautifulSoup for static HTML parsing.

Scraper adaptado para:
https://www.scrapethissite.com/pages/forms/

Página HTML estática com paginação via querystring (?page=1)
e filtros opcionais via formulário GET.
"""

from typing import List, Dict, Any, Optional
import time
import requests
from bs4 import BeautifulSoup

from app.core.config import settings


class HockeyScraper:
    """
    Scraper para coletar dados de times de Hockey
    a partir do site Scrapethissite (Forms).
    """

    def __init__(self) -> None:
        self.base_url: str = settings.hockey_url
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": settings.scraper_user_agent}
        )

    def scrape_page(self, page_number: int = 1) -> List[Dict[str, Any]]:
        """
        Coleta uma página da tabela de Hockey.
        """
        params = {"page": page_number}

        response = self.session.get(
            self.base_url,
            params=params,
            timeout=30,
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        return self._parse_teams_from_soup(soup)

    def _parse_teams_from_soup(
        self, soup: BeautifulSoup
    ) -> List[Dict[str, Any]]:
        teams: List[Dict[str, Any]] = []

        rows = soup.select("table.table tr.team")

        for row in rows:
            team = self._extract_team_data(row)
            if team:
                teams.append(team)

        return teams

    def _extract_team_data(
        self, row: Any
    ) -> Optional[Dict[str, Any]]:
        def get_text(selector: str) -> Optional[str]:
            cell = row.select_one(selector)
            return cell.text.strip() if cell else None

        try:
            return {
                "team_name": get_text("td.name"),
                "year": int(get_text("td.year")),
                "wins": int(get_text("td.wins")),
                "losses": int(get_text("td.losses")),
                "ot_losses": int(get_text("td.ot-losses")),
                "win_pct": float(get_text("td.pct")),
                "gf": int(get_text("td.gf")),
                "ga": int(get_text("td.ga")),
                "diff": int(get_text("td.diff")),
            }
        except (TypeError, ValueError):
            return None

    def scrape_all_pages(
        self, max_pages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        all_data: List[Dict[str, Any]] = []
        page = 1

        while True:
            if max_pages and page > max_pages:
                break

            print(f"[Hockey] Coletando página {page}")

            page_data = self.scrape_page(page)
            if not page_data:
                break

            all_data.extend(page_data)
            page += 1

            time.sleep(settings.scraper_delay)

        return all_data

    def close(self) -> None:
        self.session.close()


def scrape_hockey_data() -> List[Dict[str, Any]]:
    scraper = HockeyScraper()
    try:
        return scraper.scrape_all_pages()
    finally:
        scraper.close()