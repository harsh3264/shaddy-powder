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

# Specify the relative path to 'fixtures.py' from the current directory
fixtures_script_path = '/home/ec2-user/environment/shaddypowder/database/fixtures.py'

# Run the fixtures script using exec
with open(fixtures_script_path) as f:
    code = compile(f.read(), fixtures_script_path, 'exec')
    exec(code)

# Modify the query dynamically
query = '''
SELECT DISTINCT f.fixture_id
    FROM fixtures f
    LEFT JOIN leagues l ON f.league_id = l.league_id AND f.season_year = l.season_year
    # LEFT JOIN fixture_events fe ON f.fixture_id = fe.fixture_id
    LEFT JOIN fixture_player_stats fps ON f.fixture_id = fps.fixture_id
    WHERE 1 = 1
      AND f.elapsed >= 90
      AND f.fixture_date >= CURRENT_DATE - 2
    #   AND f.season_year > 2021
      AND l.season_coverage_fixtures_statistics_fixtures = 1
      AND l.season_coverage_fixtures_statistics_players = 1
      AND l.league_id NOT IN (10, 667)
    #   AND l.league_id IN (2, 3, 39, 78, 135, 140, 61, 94, 203, 848)
      AND (f.league_id IN (SELECT DISTINCT league_id
                           FROM team_league_season
                           WHERE team_id IN
                                 (SELECT home_team_id
                                  FROM fixtures
                                  WHERE league_id IN (2, 3)
                                    AND season_year = 2023)
                             AND season_year >= 2022)
        OR
           f.league_id IN (SELECT DISTINCT league_id
                           FROM team_league_season
                           WHERE team_id IN
                                 (SELECT home_team_id
                                  FROM fixtures
                                  WHERE league_id IN (1))
                             AND season_year >= 2022)
        OR f.league_id IN (40, 41, 71, 188)
        )
      AND fps.fixture_id IS NULL
    #   AND f.fixture_id IN (SELECT fixture_id FROM fixtures_stats)
    ORDER BY fixture_date DESC
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