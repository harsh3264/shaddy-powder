import sys
import os
import mysql.connector
import requests

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the necessary modules
from python_api.get_secrets import rapid_api_key, db_parameters
from python_api.rapid_apis import PLAYERS_URL

# MySQL database configuration
db_config = {
    'user': db_parameters['username'],
    'password': db_parameters['password'],
    'host': db_parameters['host'],
    'database': 'base_data_apis'
}


def insert_fixture_player_stats(cursor, fixture_id, player_stats):
    sql = """
        INSERT INTO fixture_player_stats (player_id, fixture_id, team_id, minutes_played, rating, captain, offsides, shots_total, shots_on_target, goals_total, goals_conceded, assists, saves, passes_total, passes_key, passes_accuracy, tackles_total, tackles_blocks, tackles_interceptions, duels_total, duels_won, dribbles_attempts, dribbles_success, dribbles_past, fouls_drawn, fouls_committed, cards_yellow, cards_red, penalty_won, penalty_committed, penalty_scored, penalty_missed, penalty_saved)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE player_id=player_id
    """

    for stat in player_stats:
        team_id = stat['team']['id']
        for inside_stat in stat['players']:
            player_id = inside_stat['player']['id']
            minutes_played = inside_stat['statistics'][0]['games']['minutes']
            rating = inside_stat['statistics'][0]['games']['rating']
            captain = inside_stat['statistics'][0]['games']['captain']
            offsides = inside_stat['statistics'][0]['offsides']
            shots_total = inside_stat['statistics'][0]['shots']['total']
            shots_on_target = inside_stat['statistics'][0]['shots']['on']
            goals_total = inside_stat['statistics'][0]['goals']['total']
            goals_conceded = inside_stat['statistics'][0]['goals']['conceded']
            assists = inside_stat['statistics'][0]['goals']['assists']
            saves = inside_stat['statistics'][0]['goals']['saves']
            passes_total = inside_stat['statistics'][0]['passes']['total']
            passes_key = inside_stat['statistics'][0]['passes']['key']
            passes_accuracy = inside_stat['statistics'][0]['passes']['accuracy']
            tackles_total = inside_stat['statistics'][0]['tackles']['total']
            tackles_blocks = inside_stat['statistics'][0]['tackles']['blocks']
            tackles_interceptions = inside_stat['statistics'][0]['tackles']['interceptions']
            duels_total = inside_stat['statistics'][0]['duels']['total']
            duels_won = inside_stat['statistics'][0]['duels']['won']
            dribbles_attempts = inside_stat['statistics'][0]['dribbles']['attempts']
            dribbles_success = inside_stat['statistics'][0]['dribbles']['success']
            dribbles_past = inside_stat['statistics'][0]['dribbles']['past']
            fouls_drawn = inside_stat['statistics'][0]['fouls']['drawn']
            fouls_committed = inside_stat['statistics'][0]['fouls']['committed']
            yellow_cards = inside_stat['statistics'][0]['cards']['yellow']
            red_cards = inside_stat['statistics'][0]['cards']['red']
            penalties_won = inside_stat['statistics'][0]['penalty']['won']
            penalties_committed = inside_stat['statistics'][0]['penalty']['commited']
            penalties_scored = inside_stat['statistics'][0]['penalty']['scored']
            penalties_missed = inside_stat['statistics'][0]['penalty']['missed']
            penalties_saved = inside_stat['statistics'][0]['penalty']['saved']

            params = (
                player_id, fixture_id, team_id, minutes_played, rating, captain, offsides, shots_total, shots_on_target,
                goals_total, goals_conceded, assists, saves, passes_total, passes_key, passes_accuracy,
                tackles_total, tackles_blocks, tackles_interceptions, duels_total, duels_won, dribbles_attempts,
                dribbles_success, dribbles_past, fouls_drawn, fouls_committed, yellow_cards, red_cards,
                penalties_won, penalties_committed, penalties_scored, penalties_missed, penalties_saved
            )

            cursor.execute(sql, params)

# Connect to MySQL database
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Query to get fixture IDs without player stats
query = """
    SELECT DISTINCT f.fixture_id
    FROM fixtures f
    WHERE 
        1 = 1
        AND f.season_year = 2022
        # AND f.league_id = 39
        AND NOT EXISTS (
            SELECT 1
            FROM fixture_player_stats fps
            WHERE f.fixture_id = fps.fixture_id
        )
        AND EXISTS (
            SELECT 1
            FROM fixture_lineups fl
            WHERE f.fixture_id = fl.fixture_id
        )
"""

# Execute the query
cursor.execute(query)
fixtures = cursor.fetchall()


# Iterate over fixtures
for fixture in fixtures:
    fixture_id = fixture[0]
    
    params = {"fixture": fixture_id}
    
    # Fetch player stats data
    response = requests.get(PLAYERS_URL, headers={"X-RapidAPI-Key": rapid_api_key}, params=params)
    player_stats_data = response.json()
    
    # print(player_stats_data)
    
    try:
        player_stats_data = player_stats_data['response']
    except KeyError:
        player_stats_data = []
        
    # print(player_stats_data)
    
    # Insert player stats for the fixture
    insert_fixture_player_stats(cursor, fixture_id, player_stats_data)

# Commit the changes and close the connection
conn.commit()
cursor.close()
conn.close()
