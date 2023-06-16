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
    SELECT
        DISTINCT fixture_id
    FROM fixtures
    WHERE
    1 = 1
    # AND season_year >= 2022
    # AND elapsed >= 90
    AND (home_team_id IN (3, 9, 768, 1118) OR away_team_id IN (3, 9, 768, 1118))
    # AND league_id = 253
    AND fixture_date >= CURRENT_DATE - 2
    # AND fixture_id IN (SELECT fixture_id FROM fixtures_stats)
    AND fixture_id NOT IN (SELECT fixture_id FROM fixture_player_stats)
    # AND fixture_id IN (678995)
    LIMIT 2200
'''

def update_player_info():
    players_query = """
        SELECT
            player_id,
            MAX(season_year) AS season_year
        FROM fixture_player_stats fps
        LEFT JOIN fixtures f on fps.fixture_id = f.fixture_id
        WHERE
            1 = 1
            # AND league_id IN (88)
            AND player_id NOT IN (SELECT player_id FROM players)
            AND player_id IN (SELECT player_id FROM fixture_player_stats)
            AND player_id <> 0
        GROUP BY 1
        # ORDER BY 2 DESC
        LIMIT 2000
    """
    load_player_info(players_query)
    

# Call the function to update fixture stats and store the fixture IDs
load_fixture_stats(query)

# Call the function to update fixture events and pass the fixture IDs
load_fixture_events(query)

# Call the function to update fixture lineups and pass the fixture IDs
load_fixture_lineups(query)

# Call the function to update fixture player stats and pass the fixture IDs
load_fixture_player_stats(query)

# Call the function to update player info 
# update_player_info()