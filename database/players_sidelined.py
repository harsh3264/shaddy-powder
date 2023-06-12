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
from python_api.rapid_apis import PLAYERS_SIDELINED_URL

# MySQL database configuration
db_config = {
    'user': db_parameters['username'],
    'password': db_parameters['password'],
    'host': db_parameters['host'],
    'database': 'base_data_apis'
}

def insert_players_sidelined_info(cur, player_id, event_type, start_date, end_date):
    sql = """
        INSERT INTO players_sidelined (player_id, event_type, start_date, end_date)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE player_id=player_id
    """
    cur.execute(sql, (player_id, event_type, start_date, end_date))

def load_players_sidelined_info(query):
    # Connect to MySQL database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Execute the query to fetch player IDs
    cursor.execute(query)
    player_ids = cursor.fetchall()

    # Iterate over player IDs
    for player_id in player_ids:
        player_id = player_id[0]  # Extract the player ID from the tuple
        
        # print(player_id)


        # Fetch player sidelined data
        params = {"player": str(player_id)}
        response = requests.get(PLAYERS_SIDELINED_URL, headers={"X-RapidAPI-Key": rapid_api_key}, params=params)
        player_sidelined_data = response.json()

        
        # print(player_sidelined_data)

        try:
            player_sidelined_data = player_sidelined_data['response']
        except KeyError:
            player_sidelined_data = []
            
        # print(player_sidelined_data)

        # Store player sidelined info in the database
        for sidelined in player_sidelined_data:
            event_type = sidelined['type']
            start_date = sidelined['start']
            end_date = sidelined['end']
            
            # print(event_type)

            # Insert or update player sidelined info
            insert_players_sidelined_info(cursor, player_id, event_type, start_date, end_date)
        time.sleep(0.3)

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()
