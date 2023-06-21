import sys
import os
import subprocess
import time
# Other necessary imports

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the load_fixture_stats function from fixture_stats module
from database.fixture_stats import load_fixture_stats
from database.fixture_events import load_fixture_events
from database.fixture_lineups import load_fixture_lineups
from database.fixture_player_stats import load_fixture_player_stats
from database.players import load_player_info

# Modify the query dynamically
query = '''
    SELECT DISTINCT f.fixture_id
    FROM fixtures f
    LEFT JOIN leagues l ON f.league_id = l.league_id AND f.season_year = l.season_year
    # LEFT JOIN fixtures_stats fs ON f.fixture_id = fs.fixture_id
    LEFT JOIN fixture_player_stats fps ON f.fixture_id = fps.fixture_id
    WHERE 1 = 1
      AND f.elapsed >= 90
    #   AND f.fixture_date >= CURRENT_DATE - 2
      AND f.season_year >= 2021
      AND l.season_coverage_fixtures_statistics_fixtures = 1
      AND l.season_coverage_fixtures_statistics_players = 1
    #   AND l.league_id IN (SELECT league_id FROM fixtures WHERE home_team_id = 1 OR away_team_id = 1)
    #   AND l.league_id != 10
    #   AND fs.fixture_id IS NOT NULL
      AND fps.fixture_id IS NULL
    ORDER BY fixture_date DESC
      LIMIT 1500
'''

def update_player_info():
    players_query = """
    SELECT
            player_id,
            MAX(season_year) - 1 AS season_year
        FROM fixture_player_stats fps
        LEFT JOIN fixtures f on fps.fixture_id = f.fixture_id
        WHERE
            1 = 1
            # AND league_id IN (960, 5)
            AND player_id NOT IN (SELECT player_id FROM players)
            AND player_id IN (SELECT player_id FROM fixture_player_stats)
            AND player_id <> 0
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT 6500
    """
    load_player_info(players_query)
    

# Call the function to update fixture stats and store the fixture IDs
load_fixture_stats(query)

# # Call the function to update fixture events and pass the fixture IDs
load_fixture_events(query)

# # Call the function to update fixture lineups and pass the fixture IDs
load_fixture_lineups(query)

# # Call the function to update fixture player stats and pass the fixture IDs
load_fixture_player_stats(query)

# Call the function to update player info 
# update_player_info()