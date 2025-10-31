import sys
import os
import subprocess
import time
# Other necessary imports

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the load_fixture_stats function from fixture_stats module
from database.players import load_player_info
from database.injuries_table import fetch_and_insert_injuries

# Modify the query dynamically
query1 = '''
    SELECT
    fps.player_id AS player_id,
    MAX(IFNULL(tf1.season_year, tf2.season_year)) AS season_year
    FROM analytics.fixture_player_stats_compile fps
    INNER JOIN base_data_apis.players_latest_club plc
    ON fps.player_id = plc.player_id
    LEFT JOIN today_fixture tf1
    ON plc.team_id = tf1.home_team_id
    LEFT JOIN today_fixture tf2
    ON plc.team_id = tf2.away_team_id
    WHERE 1 = 1
    AND (tf1.fixt IS NOT NULL OR tf2.fixt IS NOT NULL)
    AND fps.player_id NOT IN (SELECT player_id FROM players)
    GROUP BY 1
    ;
'''


# query2 = '''
#     SELECT
#     fps.player_id
#     FROM fixture_player_stats fps
#     INNER JOIN base_data_apis.player_latest_club plc
#     ON fps.player_id = plc.player_id
#     LEFT JOIN today_fixture tf1
#     ON plc.team_id = tf1.home_team_id
#     LEFT JOIN today_fixture tf2
#     ON plc.team_id = tf2.away_team_id
#     WHERE 1 = 1
#     AND (tf1.fixt IS NOT NULL OR tf2.fixt IS NOT NULL)
#     GROUP BY 1
#     ;
# '''

load_player_info(query1)

# fetch_and_insert_injuries()
    