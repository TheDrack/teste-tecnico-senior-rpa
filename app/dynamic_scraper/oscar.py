"""
Oscar scraper using Selenium for dynamic JavaScript/AJAX content.

Este módulo implementa o scraper para dados de Oscar usando Selenium,
adequado para páginas dinâmicas que carregam dados via JavaScript/AJAX.

PREENCHER: Configurar a URL correta do site no arquivo .env (OSCAR_URL)
"""

from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

from app.core.config import settings


class OscarScraper:
    """
    Scraper para coletar dados de filmes premiados no Oscar.

    Utiliza Selenium para lidar com conteúdo dinâmico carregado
    via JavaScript/AJAX. Suporta modo headless para execução em servidores.

    Attributes:
        base_url: URL base do site a fazer scraping
        driver: WebDriver do Selenium
        wait: WebDriverWait para esperar elementos

    Example:
        >>> scraper = OscarScraper()
        >>> data = scraper.scrape_all_data()
        >>> print(f"Coletados {len(data)} filmes")
        >>> scraper.close()
    """

    def __init__(self) -> None:
        """
        Inicializa o scraper e configura o Selenium WebDriver.

        PREENCHER: A URL do site deve ser configurada no .env
        """
        # PREENCHER: Configurar URL correta no .env
        self.base_url: str = settings.oscar_url

        # Configurar opções do Chrome
        self.options = Options()

        # Modo headless (sem interface gráfica)
        if settings.selenium_headless:
            self.options.add_argument("--headless")

        # Argumentos adicionais para rodar em containers/CI
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument(f"user-agent={settings.scraper_user_agent}")

        # PREENCHER: Configurar caminho do ChromeDriver se necessário
        # service = Service(executable_path="/path/to/chromedriver")
        # self.driver = webdriver.Chrome(service=service, options=self.options)

        # Inicializar WebDriver
        self.driver: webdriver.Chrome = webdriver.Chrome(options=self.options)

        # Configurar timeout para esperas
        self.wait = WebDriverWait(self.driver, settings.selenium_timeout)

    def scrape_all_data(self) -> List[Dict[str, Any]]:
        """
        Faz scraping de todos os dados disponíveis.

        Returns:
            List[Dict[str, Any]]: Lista de dicionários com dados dos filmes

        Raises:
            TimeoutException: Se timeout ao aguardar elementos

        Example:
            >>> scraper = OscarScraper()
            >>> data = scraper.scrape_all_data()
            >>> for movie in data:
            >>>     print(movie["title"], movie["year"])
        """
        print(f"[Oscar] Acessando {self.base_url}...")

        # Acessar página
        self.driver.get(self.base_url)

        # PREENCHER: Aguardar carregamento do conteúdo AJAX
        # Exemplo: aguardar elemento específico aparecer
        try:
            # Adaptar seletor conforme estrutura da página
            self.wait.until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "film")
                )  # ADAPTAR seletor
            )
            print("[Oscar] Conteúdo AJAX carregado")
        except TimeoutException:
            print("[Oscar] Timeout aguardando conteúdo AJAX")
            return []

        # Delay adicional para garantir carregamento completo
        time.sleep(2)

        # Parsear dados da página
        return self._parse_oscar_data()

    def _parse_oscar_data(self) -> List[Dict[str, Any]]:
        """
        Extrai dados dos filmes da página carregada.

        Returns:
            List[Dict[str, Any]]: Lista de dados extraídos

        Example:
            >>> scraper.driver.get(url)
            >>> data = scraper._parse_oscar_data()
        """
        movies_data: List[Dict[str, Any]] = []

        # PREENCHER: Adaptar seletores conforme estrutura HTML/DOM do site
        # Exemplo: encontrar todos os elementos de filmes
        try:
            # Adaptar seletor CSS/XPath conforme necessário
            movie_elements = self.driver.find_elements(By.CLASS_NAME, "film")  # ADAPTAR

            print(f"[Oscar] Encontrados {len(movie_elements)} filmes")

            for element in movie_elements:
                try:
                    movie_data = self._extract_movie_data(element)
                    if movie_data:
                        movies_data.append(movie_data)
                except Exception as e:
                    # Log erro mas continua processando
                    print(f"[Oscar] Erro ao processar filme: {e}")
                    continue

        except NoSuchElementException as e:
            print(f"[Oscar] Erro ao localizar elementos: {e}")

        return movies_data

    def _extract_movie_data(self, element: Any) -> Optional[Dict[str, Any]]:
        """
        Extrai dados de um único filme de um elemento HTML.

        Args:
            element: WebElement do Selenium representando um filme

        Returns:
            Optional[Dict[str, Any]]: Dicionário com dados do filme ou None se inválido

        Example:
            >>> element = driver.find_element(By.CLASS_NAME, "film")
            >>> movie = scraper._extract_movie_data(element)
            >>> print(movie["title"])
        """
        # PREENCHER: Adaptar seletores conforme estrutura do site

        try:
            # Ano da premiação
            year_elem = element.find_element(By.CLASS_NAME, "year")  # ADAPTAR
            year = int(year_elem.text.strip()) if year_elem else 0

            # Título do filme
            title_elem = element.find_element(By.CLASS_NAME, "film-title")  # ADAPTAR
            title = title_elem.text.strip() if title_elem else ""

            if not title:
                return None

            # Número de indicações
            nominations_elem = element.find_element(
                By.CLASS_NAME, "nominations"
            )  # ADAPTAR
            nominations = int(nominations_elem.text.strip()) if nominations_elem else 0

            # Número de prêmios ganhos
            awards_elem = element.find_element(By.CLASS_NAME, "awards")  # ADAPTAR
            awards = int(awards_elem.text.strip()) if awards_elem else 0

            # Best Picture (verificar se tem classe/atributo específico)
            # ADAPTAR: lógica pode variar conforme site
            best_picture_elem = element.find_elements(
                By.CLASS_NAME, "best-picture"
            )  # ADAPTAR
            best_picture = len(best_picture_elem) > 0

            return {
                "year": year,
                "title": title,
                "nominations": nominations,
                "awards": awards,
                "best_picture": best_picture,
            }

        except NoSuchElementException as e:
            print(f"[Oscar] Elemento não encontrado: {e}")
            return None

    def scrape_by_year(self, year: int) -> List[Dict[str, Any]]:
        """
        Faz scraping de filmes de um ano específico.

        Args:
            year: Ano da premiação (ex: 2010)

        Returns:
            List[Dict[str, Any]]: Dados dos filmes do ano

        Example:
            >>> scraper = OscarScraper()
            >>> data_2010 = scraper.scrape_by_year(2010)
        """
        # PREENCHER: Implementar filtragem por ano se o site suportar
        # Pode envolver clicar em filtros, alterar URL, etc.

        print(f"[Oscar] Coletando dados do ano {year}...")

        # Exemplo: se site tem dropdown de anos
        # year_dropdown = self.driver.find_element(By.ID, "year-filter")
        # year_dropdown.click()
        # year_option = self.driver.find_element(By.XPATH, f"//option[@value='{year}']")
        # year_option.click()
        # time.sleep(2)  # Aguardar filtro aplicar

        return self._parse_oscar_data()

    def close(self) -> None:
        """
        Fecha o WebDriver e libera recursos.

        Sempre chame este método ao finalizar o uso do scraper
        para evitar processos do Chrome/ChromeDriver rodando em segundo plano.

        Example:
            >>> scraper = OscarScraper()
            >>> # ... usar scraper ...
            >>> scraper.close()
        """
        if self.driver:
            self.driver.quit()


def scrape_oscar_data() -> List[Dict[str, Any]]:
    """
    Função auxiliar para executar scraping de Oscar.

    Cria um scraper, coleta todos os dados e fecha o driver.

    Returns:
        List[Dict[str, Any]]: Dados coletados

    Example:
        >>> data = scrape_oscar_data()
        >>> print(f"Coletados {len(data)} filmes")
    """
    scraper = OscarScraper()
    try:
        data = scraper.scrape_all_data()
        return data
    finally:
        scraper.close()
