import sys
import os
import subprocess
import time
# Other necessary imports

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the load_fixture_stats function from fixture_stats module
from database.players_sidelined import load_players_sidelined_info

players_sidelined_query = """
    SELECT DISTINCT fps.player_id
    FROM fixture_player_stats fps
    JOIN fixtures f
    ON fps.fixture_id = f.fixture_id
    WHERE 1 = 1
    # AND (fps.team_id IN (SELECT home_team_id FROM fixtures WHERE fixture_date = CURDATE() AND elapsed IS NULL)
            # OR fps.team_id IN (SELECT away_team_id FROM fixtures WHERE fixture_date = CURDATE() AND elapsed IS NULL))
    AND f.season_year = 2022
    AND player_id NOT IN (SELECT DISTINCT player_id FROM players_sidelined)
    # AND f.league_id = 135
    LIMIT 2500
"""

load_players_sidelined_info(players_sidelined_query)