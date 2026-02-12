"""
Oscar scraper using Selenium for dynamic JavaScript/AJAX content.

Este módulo implementa o scraper para dados de Oscar usando Selenium,
adequado para páginas dinâmicas que carregam dados via JavaScript/AJAX.

Site alvo:
https://www.scrapethissite.com/pages/ajax-javascript/
"""

from typing import List, Dict, Any, Optional
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from app.core.config import settings


class OscarScraper:
    """
    Scraper para coletar dados de filmes premiados no Oscar
    a partir de conteúdo carregado via AJAX.
    """

    def __init__(self) -> None:
        self.base_url: str = settings.oscar_url

        options = Options()

        if settings.selenium_headless:
            options.add_argument("--headless")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(f"user-agent={settings.scraper_user_agent}")

        self.driver: webdriver.Chrome = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, settings.selenium_timeout)

    def scrape_all_data(self) -> List[Dict[str, Any]]:
        print(f"[Oscar] Acessando {self.base_url}")
        self.driver.get(self.base_url)

        try:
            # Espera os links de anos aparecerem
            self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a[data-year]")
                )
            )
        except TimeoutException:
            print("[Oscar] Timeout aguardando lista de anos")
            return []

        all_movies: List[Dict[str, Any]] = []

        year_links = self.driver.find_elements(By.CSS_SELECTOR, "a[data-year]")

        for link in year_links:
            year = link.get_attribute("data-year")
            print(f"[Oscar] Coletando dados do ano {year}")

            # Clique via JS evita problemas de overlay
            self.driver.execute_script("arguments[0].click();", link)

            try:
                self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "tr.film")
                    )
                )
            except TimeoutException:
                print(f"[Oscar] Timeout carregando filmes de {year}")
                continue

            time.sleep(0.5)  # folga para AJAX completar

            movies = self._parse_oscar_data()
            all_movies.extend(movies)

        return all_movies

    def _parse_oscar_data(self) -> List[Dict[str, Any]]:
        movies_data: List[Dict[str, Any]] = []

        rows = self.driver.find_elements(By.CSS_SELECTOR, "tr.film")
        print(f"[Oscar] Filmes encontrados: {len(rows)}")

        for row in rows:
            movie = self._extract_movie_data(row)
            if movie:
                movies_data.append(movie)

        return movies_data

    def _extract_movie_data(self, element: Any) -> Optional[Dict[str, Any]]:
        try:
            title = element.find_element(By.CLASS_NAME, "title").text.strip()
            year = int(element.find_element(By.CLASS_NAME, "year").text.strip())
            nominations = int(
                element.find_element(By.CLASS_NAME, "nominations").text.strip()
            )
            awards = int(
                element.find_element(By.CLASS_NAME, "awards").text.strip()
            )

            best_picture_text = element.find_element(
                By.CLASS_NAME, "best-picture"
            ).text.strip()

            best_picture = best_picture_text.lower() == "yes"

            return {
                "year": year,
                "title": title,
                "nominations": nominations,
                "awards": awards,
                "best_picture": best_picture,
            }

        except NoSuchElementException:
            return None

    def scrape_by_year(self, year: int) -> List[Dict[str, Any]]:
        self.driver.get(self.base_url)

        try:
            year_link = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, f"a[data-year='{year}']")
                )
            )
            self.driver.execute_script("arguments[0].click();", year_link)

            self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "tr.film")
                )
            )
            time.sleep(0.5)

            return self._parse_oscar_data()

        except TimeoutException:
            print(f"[Oscar] Não foi possível carregar dados de {year}")
            return []

    def close(self) -> None:
        if self.driver:
            self.driver.quit()


def scrape_oscar_data() -> List[Dict[str, Any]]:
    scraper = OscarScraper()
    try:
        return scraper.scrape_all_data()
    finally:
        scraper.close()