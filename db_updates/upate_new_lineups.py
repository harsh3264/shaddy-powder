import sys
import os
import subprocess
import time
# Other necessary imports

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the load_fixture_stats function from fixture_stats module
from database.fixture_lineups import load_fixture_lineups

# Modify the query dynamically
query = '''
    SELECT
        DISTINCT fixture_id
    FROM fixtures
    WHERE
    1 = 1
    # AND season_year >= 2022
    # AND elapsed >= 90
    # AND (home_team_id IN (3, 9, 768, 1118, 1090) OR away_team_id IN (3, 9, 768, 1118, 1090))
    AND league_id = 71
    AND fixture_date = CURRENT_DATE 
    # AND fixture_id IN (SELECT fixture_id FROM fixtures_stats)
    AND fixture_id NOT IN (SELECT fixture_id FROM fixture_lineups)
    # AND fixture_id IN (678995)
    # LIMIT 2200
'''


# Call the function to update fixture lineups and pass the fixture IDs
load_fixture_lineups(query)
