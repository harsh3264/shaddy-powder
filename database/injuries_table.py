import sys
import os
import mysql.connector
import requests
import uuid
from datetime import datetime

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the necessary modules
from python_api.get_secrets import rapid_api_key, db_parameters
from python_api.rapid_apis import INJURIES_URL


# MySQL database configuration
db_config = {
    'user': db_parameters['username'],
    'password': db_parameters['password'],
    'host': db_parameters['host'],
    'database': 'base_data_apis'
}

def insert_injury_data(cur, player_id, fixture_id, league_id, team_id, injury_type, reason):
    sql = """
        INSERT INTO injuries (player_id, fixture_id, league_id, team_id, type, reason)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE type=VALUES(type), reason=VALUES(reason)
    """
    cur.execute(sql, (player_id, fixture_id, league_id, team_id, injury_type, reason))

def fetch_and_insert_injuries():
    # Connect to MySQL database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Get the current date in the desired format
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Set the current date as a parameter
    params = {'date': current_date}
    
    # Fetch the API data
    headers = {
        'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
        'x-rapidapi-key': rapid_api_key
    }

    # Fetch injuries data from the API
    response = requests.get(INJURIES_URL, headers=headers, params=params)
    injuries_data = response.json().get('response', [])

    # Iterate over injuries data and insert into the database
    for injury in injuries_data:
        player = injury.get('player', {})
        team = injury.get('team', {})
        fixture = injury.get('fixture', {})
        league = injury.get('league', {})

        player_id = player.get('id')
        team_id = team.get('id')
        league_id = league.get('id')
        fixture_id = fixture.get('id')  # Add fixture_id
        injury_type = player.get('type')
        reason = player.get('reason')

        # Insert injury data into the database with ON DUPLICATE KEY UPDATE
        insert_injury_data(cursor, player_id, fixture_id, league_id, team_id, injury_type, reason)

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()


