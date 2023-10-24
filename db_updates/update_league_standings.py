import sys
import os
import subprocess
import time
# Other necessary imports

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the load_fixture_stats function from fixture_stats module
from database.league_standings import load_league_standings

league_standings_query = """
    SELECT f.league_id, MAX(f.season_year) AS season_year
    FROM fixtures_stats fs
    JOIN fixtures f ON fs.fixture_id = f.fixture_id
    WHERE 1 = 1
    AND league_id IN (SELECT league_id FROM today_fixture)
    GROUP BY 1
    ;
"""

load_league_standings(league_standings_query)