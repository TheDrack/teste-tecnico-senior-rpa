"""
Hockey scraper using BeautifulSoup for static HTML parsing.

Este módulo implementa o scraper para dados de Hockey usando BeautifulSoup,
adequado para páginas HTML estáticas com paginação tradicional.

PREENCHER: Configurar a URL correta do site no arquivo .env (HOCKEY_URL)
"""

from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
import time

from app.core.config import settings


class HockeyScraper:
    """
    Scraper para coletar dados de times de Hockey.

    Utiliza BeautifulSoup para parsear HTML estático e extrair
    informações sobre times, estatísticas de jogos e temporadas.

    Attributes:
        base_url: URL base do site a fazer scraping
        session: Sessão HTTP para reuso de conexões
        user_agent: User agent para requests

    Example:
        >>> scraper = HockeyScraper()
        >>> data = scraper.scrape_all_pages()
        >>> print(f"Coletados {len(data)} registros")
    """

    def __init__(self) -> None:
        """
        Inicializa o scraper com configurações.

        PREENCHER: A URL do site deve ser configurada no .env
        """
        # PREENCHER: Configurar URL correta no .env
        self.base_url: str = settings.hockey_url

        # Criar sessão HTTP para reuso de conexões
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": settings.scraper_user_agent})

    def scrape_page(self, page_number: int = 1) -> List[Dict[str, Any]]:
        """
        Faz scraping de uma única página de dados.

        Args:
            page_number: Número da página a ser coletada (inicia em 1)

        Returns:
            List[Dict[str, Any]]: Lista de dicionários com dados dos times

        Raises:
            requests.RequestException: Se falhar ao acessar a página

        Example:
            >>> scraper = HockeyScraper()
            >>> data = scraper.scrape_page(page_number=1)
            >>> for team in data:
            >>>     print(team["team_name"], team["year"])
        """
        # PREENCHER: Construir URL com número da página
        # Exemplo: url = f"{self.base_url}?page={page_number}"
        url = f"{self.base_url}?page={page_number}"  # ADAPTAR conforme necessário

        # Fazer request HTTP
        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        # Parsear HTML com BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # PREENCHER: Adaptar seletores CSS conforme estrutura HTML do site
        return self._parse_teams_from_soup(soup)

    def _parse_teams_from_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extrai dados dos times do HTML parseado.

        Args:
            soup: Objeto BeautifulSoup com HTML da página

        Returns:
            List[Dict[str, Any]]: Lista de dados extraídos

        Example:
            >>> soup = BeautifulSoup(html, "html.parser")
            >>> teams = scraper._parse_teams_from_soup(soup)
        """
        teams_data: List[Dict[str, Any]] = []

        # PREENCHER: Adaptar seletores CSS conforme HTML do site
        # Exemplo: rows = soup.find_all("tr", class_="team")
        rows = soup.find_all("tr", class_="team")  # ADAPTAR seletor

        for row in rows:
            try:
                team_data = self._extract_team_data(row)
                if team_data:
                    teams_data.append(team_data)
            except Exception as e:
                # Log erro mas continua processando outros registros
                print(f"Erro ao processar linha: {e}")
                continue

        return teams_data

    def _extract_team_data(self, row: Any) -> Optional[Dict[str, Any]]:
        """
        Extrai dados de um único time de uma linha HTML.

        Args:
            row: Elemento BeautifulSoup representando uma linha da tabela

        Returns:
            Optional[Dict[str, Any]]: Dicionário com dados do time ou None se inválido

        Example:
            >>> row = soup.find("tr", class_="team")
            >>> team = scraper._extract_team_data(row)
            >>> print(team["team_name"])
        """
        # PREENCHER: Adaptar seletores conforme estrutura HTML
        # Exemplo de campos a extrair:

        # Nome do time
        team_name_elem = row.find("td", class_="name")  # ADAPTAR classe
        if not team_name_elem:
            return None
        team_name = team_name_elem.text.strip()

        # Ano
        year_elem = row.find("td", class_="year")  # ADAPTAR classe
        year = int(year_elem.text.strip()) if year_elem else 0

        # Estatísticas de jogos
        wins_elem = row.find("td", class_="wins")  # ADAPTAR classe
        wins = int(wins_elem.text.strip()) if wins_elem else 0

        losses_elem = row.find("td", class_="losses")  # ADAPTAR classe
        losses = int(losses_elem.text.strip()) if losses_elem else 0

        ot_losses_elem = row.find("td", class_="ot-losses")  # ADAPTAR classe
        ot_losses = int(ot_losses_elem.text.strip()) if ot_losses_elem else 0

        # Estatísticas calculadas
        win_pct_elem = row.find("td", class_="pct")  # ADAPTAR classe
        win_pct = float(win_pct_elem.text.strip()) if win_pct_elem else None

        gf_elem = row.find("td", class_="gf")  # ADAPTAR classe
        gf = int(gf_elem.text.strip()) if gf_elem else None

        ga_elem = row.find("td", class_="ga")  # ADAPTAR classe
        ga = int(ga_elem.text.strip()) if ga_elem else None

        diff_elem = row.find("td", class_="diff")  # ADAPTAR classe
        diff = int(diff_elem.text.strip()) if diff_elem else None

        return {
            "team_name": team_name,
            "year": year,
            "wins": wins,
            "losses": losses,
            "ot_losses": ot_losses,
            "win_pct": win_pct,
            "gf": gf,
            "ga": ga,
            "diff": diff,
        }

    def scrape_all_pages(self, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Faz scraping de todas as páginas disponíveis.

        Args:
            max_pages: Número máximo de páginas a coletar (None = todas)

        Returns:
            List[Dict[str, Any]]: Lista com todos os dados coletados

        Example:
            >>> scraper = HockeyScraper()
            >>> all_data = scraper.scrape_all_pages(max_pages=5)
            >>> print(f"Total de registros: {len(all_data)}")
        """
        all_data: List[Dict[str, Any]] = []
        page = 1

        while True:
            # Verificar limite de páginas
            if max_pages and page > max_pages:
                break

            print(f"[Hockey] Coletando página {page}...")

            try:
                # Coletar dados da página
                page_data = self.scrape_page(page_number=page)

                # Se não houver dados, assumir que chegou ao fim
                if not page_data:
                    print("[Hockey] Nenhum dado encontrado. Finalizando.")
                    break

                all_data.extend(page_data)
                print(f"[Hockey] Coletados {len(page_data)} registros da página {page}")

                # Delay entre requests para evitar sobrecarga
                time.sleep(settings.scraper_delay)

                page += 1

            except requests.RequestException as e:
                print(f"[Hockey] Erro ao acessar página {page}: {e}")
                break

        print(f"[Hockey] Total coletado: {len(all_data)} registros")
        return all_data

    def close(self) -> None:
        """
        Fecha a sessão HTTP e libera recursos.

        Example:
            >>> scraper = HockeyScraper()
            >>> # ... usar scraper ...
            >>> scraper.close()
        """
        self.session.close()


def scrape_hockey_data() -> List[Dict[str, Any]]:
    """
    Função auxiliar para executar scraping de Hockey.

    Cria um scraper, coleta todos os dados e fecha a sessão.

    Returns:
        List[Dict[str, Any]]: Dados coletados

    Example:
        >>> data = scrape_hockey_data()
        >>> print(f"Coletados {len(data)} times")
    """
    scraper = HockeyScraper()
    try:
        data = scraper.scrape_all_pages()
        return data
    finally:
        scraper.close()
