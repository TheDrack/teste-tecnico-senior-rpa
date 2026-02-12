"""
Unit tests for HTML parsers.
Validates that scrapers extract correct data from HTML.
"""
import pytest
from bs4 import BeautifulSoup


class TestHockeyParser:
    """Tests for Hockey scraper HTML parsing logic."""
    
    def test_parse_team_row_basic(self, sample_hockey_html):
        """Test parsing a single team row from HTML."""
        soup = BeautifulSoup(sample_hockey_html, "html.parser")
        row = soup.find("tr", class_="team")
        
        assert row is not None
        
        # Test that all required fields are present
        team_name = row.find("td", class_="name")
        year = row.find("td", class_="year")
        wins = row.find("td", class_="wins")
        losses = row.find("td", class_="losses")
        
        assert team_name is not None
        assert year is not None
        assert wins is not None
        assert losses is not None
    
    def test_parse_team_data_extraction(self, sample_hockey_html):
        """Test extracting actual values from team row."""
        soup = BeautifulSoup(sample_hockey_html, "html.parser")
        row = soup.find("tr", class_="team")
        
        # Extract data
        team_name = row.find("td", class_="name").text.strip()
        year = int(row.find("td", class_="year").text.strip())
        wins = int(row.find("td", class_="wins").text.strip())
        losses = int(row.find("td", class_="losses").text.strip())
        ot_losses = int(row.find("td", class_="ot-losses").text.strip())
        
        # Validate extracted values
        assert team_name == "Boston Bruins"
        assert year == 1990
        assert wins == 44
        assert losses == 24
        assert ot_losses == 0
    
    def test_parse_team_statistics(self, sample_hockey_html):
        """Test extracting team statistics (win%, GF, GA, diff)."""
        soup = BeautifulSoup(sample_hockey_html, "html.parser")
        row = soup.find("tr", class_="team")
        
        # Extract statistics
        win_pct = float(row.find("td", class_="pct").text.strip())
        goals_for = int(row.find("td", class_="gf").text.strip())
        goals_against = int(row.find("td", class_="ga").text.strip())
        goal_diff = int(row.find("td", class_="diff").text.strip())
        
        # Validate statistics
        assert win_pct == 0.550
        assert goals_for == 299
        assert goals_against == 264
        assert goal_diff == 35
    
    def test_parse_missing_fields(self):
        """Test handling of missing or malformed data."""
        html = """
        <table class="table">
            <tr class="team">
                <td class="name">Test Team</td>
            </tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        row = soup.find("tr", class_="team")
        
        # Should handle missing fields gracefully
        year_field = row.find("td", class_="year")
        assert year_field is None
    
    def test_parse_multiple_teams(self):
        """Test parsing multiple team rows."""
        html = """
        <table class="table">
            <tr class="team">
                <td class="name">Team A</td>
                <td class="year">2000</td>
            </tr>
            <tr class="team">
                <td class="name">Team B</td>
                <td class="year">2001</td>
            </tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.find_all("tr", class_="team")
        
        assert len(rows) == 2
        assert rows[0].find("td", class_="name").text.strip() == "Team A"
        assert rows[1].find("td", class_="name").text.strip() == "Team B"


class TestOscarParser:
    """Tests for Oscar scraper data parsing logic."""
    
    def test_parse_oscar_data_structure(self, sample_oscar_data):
        """Test that Oscar data has correct structure."""
        data = sample_oscar_data[0]
        
        # Validate required fields
        assert "year" in data
        assert "title" in data
        assert "nominations" in data
        assert "awards" in data
        assert "best_picture" in data
    
    def test_parse_oscar_data_types(self, sample_oscar_data):
        """Test that Oscar data fields have correct types."""
        data = sample_oscar_data[0]
        
        assert isinstance(data["year"], int)
        assert isinstance(data["title"], str)
        assert isinstance(data["nominations"], int)
        assert isinstance(data["awards"], int)
        assert isinstance(data["best_picture"], bool)
    
    def test_parse_oscar_data_values(self, sample_oscar_data):
        """Test that Oscar data contains expected values."""
        winner = sample_oscar_data[0]
        nominee = sample_oscar_data[1]
        
        # Test winner
        assert winner["year"] == 2010
        assert winner["title"] == "The Hurt Locker"
        assert winner["nominations"] == 9
        assert winner["awards"] == 6
        assert winner["best_picture"] is True
        
        # Test nominee
        assert nominee["year"] == 2010
        assert nominee["title"] == "Avatar"
        assert nominee["nominations"] == 9
        assert nominee["awards"] == 3
        assert nominee["best_picture"] is False
    
    def test_parse_multiple_oscar_entries(self, sample_oscar_data):
        """Test parsing multiple Oscar entries."""
        assert len(sample_oscar_data) == 2
        
        # Both from same year
        assert sample_oscar_data[0]["year"] == sample_oscar_data[1]["year"]
        
        # Only one best picture per year
        best_pictures = [d for d in sample_oscar_data if d["best_picture"]]
        assert len(best_pictures) == 1
    
    def test_parse_oscar_awards_validation(self, sample_oscar_data):
        """Test that awards don't exceed nominations."""
        for entry in sample_oscar_data:
            assert entry["awards"] <= entry["nominations"], \
                f"Awards ({entry['awards']}) cannot exceed nominations ({entry['nominations']})"
