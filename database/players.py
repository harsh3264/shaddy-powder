import sys
import os
import mysql.connector
import requests
import time

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the necessary modules
from python_api.get_secrets import rapid_api_key, db_parameters
from python_api.rapid_apis import PLAYER_INFO_URL

# MySQL database configuration
db_config = {
    'user': db_parameters['username'],
    'password': db_parameters['password'],
    'host': db_parameters['host'],
    'database': 'base_data_apis'
}

def insert_player_info(cur, player_id, name, first_name, last_name, nationality, age, height, weight, photo):
    sql = """
        INSERT INTO players (player_id, name, first_name, last_name, nationality, age, height, weight, photo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE player_id=player_id
    """
    cur.execute(sql, (player_id, name, first_name, last_name, nationality, age, height, weight, photo))

def load_player_info(query):
    # Connect to MySQL database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Execute the query
    cursor.execute(query)
    player_data = cursor.fetchall()

    # Iterate over player data
    for player_id, season_year in player_data:
        params = {"id": player_id, "season": season_year}

        # Fetch player information
        response = requests.get(PLAYER_INFO_URL, headers={"X-RapidAPI-Key": rapid_api_key}, params=params)
        player_info = response.json()

        try:
            player_info = player_info['response'][0]
        except (KeyError, IndexError):
            continue

        # Extract player details
        name = player_info['player']['name']
        first_name = player_info['player'].get('firstname', '')
        last_name = player_info['player'].get('lastname', '')
        nationality = player_info['player'].get('nationality', '')
        age = player_info['player'].get('age', '')
        height = player_info['player'].get('height', '')
        weight = player_info['player'].get('weight', '')
        photo = player_info['player'].get('photo', '')

        # Insert player information into the database
        insert_player_info(cursor, player_id, name, first_name, last_name, nationality, age, height, weight, photo)

        time.sleep(0.3)
        
    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()