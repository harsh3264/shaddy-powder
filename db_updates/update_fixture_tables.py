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

# Other necessary imports

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

import os

# Check if the script is running on Cloud9 (you might need to adjust this check based on your specific environment)
if "C9_PORT" in os.environ:
    # Your Cloud9 environment
    environment_name = "Cloud9"
    user_home = os.path.expanduser("~")
    project_directory = "environment/shaddypowder"
else:
    # Your EC2 environment
    environment_name = "EC2"
    user_home = os.path.expanduser("~")
    project_directory = "shaddy-powder"  # Adjust this to the EC2 directory name

# Common directory structure
script_directory = "database"
script_name = "fixtures.py"

# Construct the absolute path
fixtures_script_path = os.path.abspath(os.path.join(user_home, project_directory, script_directory, script_name))


# Run the fixtures script using exec
with open(fixtures_script_path) as f:
    code = compile(f.read(), fixtures_script_path, 'exec')
    exec(code)

# Modify the query dynamically
query = '''
SELECT DISTINCT f.fixture_id
    FROM fixtures f
    LEFT JOIN leagues l ON f.league_id = l.league_id AND f.season_year = l.season_year
    LEFT JOIN fixture_player_stats fps ON f.fixture_id = fps.fixture_id
    WHERE 1 = 1
      AND f.elapsed >= 90
      AND f.fixture_date >= CURRENT_DATE - 2
    #   AND f.season_year > 2021
      AND l.season_coverage_fixtures_statistics_fixtures = 1
      AND l.season_coverage_fixtures_statistics_players = 1
      AND l.league_id NOT IN (10, 667)
      AND f.league_id IN (SELECT f.league_id FROM top_leagues)
      AND fps.fixture_id IS NULL
    ORDER BY fixture_date DESC
    # LIMIT 2
;
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
            # AND league_id IN (71)
            AND player_id NOT IN (SELECT player_id FROM players)
            AND player_id IN (SELECT player_id FROM fixture_player_stats)
            AND player_id <> 0
            AND season_year <= YEAR(CURDATE())
        GROUP BY 1
        ORDER BY 2 DESC
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

# # # Call the function to update player info 
# update_player_info()