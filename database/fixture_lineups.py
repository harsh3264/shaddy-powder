import sys
import os
import mysql.connector
import requests

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the necessary modules
from python_api.get_secrets import rapid_api_key, db_parameters
from python_api.rapid_apis import LINEUP_URL

# MySQL database configuration
db_config = {
    'user': db_parameters['username'],
    'password': db_parameters['password'],
    'host': db_parameters['host'],
    'database': 'base_data_apis'
}

def insert_fixture_info(cur, fixture_id, team_id, is_home, coach_id, coach_name, photo, formation):
    sql = """
        INSERT INTO fixture_coach (fixture_id, team_id, is_home, coach_id, coach_name, photo, formation)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE fixture_id=fixture_id
    """
    cur.execute(sql, (fixture_id, team_id, is_home, coach_id, coach_name, photo, formation))

def insert_player_info(cur, fixture_id, team_id, player_id, player_number, player_pos, grid, is_substitute):
    sql = """
        INSERT INTO fixture_lineups (fixture_id, team_id, player_id, player_number, player_pos, grid, is_substitute)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE fixture_id=fixture_id
    """
    cur.execute(sql, (fixture_id, team_id, player_id, player_number, player_pos, grid, is_substitute))

def load_fixture_lineups(query):
    # Connect to MySQL database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Execute the query
    cursor.execute(query)
    fixtures = cursor.fetchall()

    # Iterate over fixtures
    for fixture in fixtures:
        fixture_id = fixture[0]
        params = {"fixture": fixture_id}

        # Fetch lineup data
        response = requests.get(LINEUP_URL, headers={"X-RapidAPI-Key": rapid_api_key}, params=params)
        lineup_data = response.json()

        try:
            lineup_data = lineup_data['response']
        except KeyError:
            lineup_data = []

        # Store fixture info in the database
        for i, lineup in enumerate(lineup_data):
            team_id = lineup['team']['id']
            is_home = True if i == 0 else False  # First lineup object is home, others are away
            coach_id = lineup['coach']['id']
            coach_name = lineup['coach']['name']
            coach = lineup.get('coach', {})
            photo = coach.get('photo', None)
            formation = lineup['formation']

            # Insert fixture info
            insert_fixture_info(cursor, fixture_id, team_id, is_home, coach_id, coach_name, photo, formation)

            # Insert player info
            for player in lineup['startXI']:
                player_id = player['player']['id']
                player_number = player['player']['number']
                player_pos = player['player']['pos']
                grid = player['player']['grid']
                is_substitute = 0

                insert_player_info(cursor, fixture_id, team_id, player_id, player_number, player_pos, grid, is_substitute)

            # Insert substitute info
            for substitute in lineup['substitutes']:
                if substitute['player'] and substitute['player']['id'] is not None:
                    player_id = substitute['player']['id']
                else:
                    player_id = 0
                player_number = substitute['player']['number']
                player_pos = substitute['player']['pos']
                grid = None
                is_substitute = 1

                insert_player_info(cursor, fixture_id, team_id, player_id, player_number, player_pos, grid, is_substitute)

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()
