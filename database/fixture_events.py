import sys
import os
import mysql.connector
import requests
import uuid

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the necessary modules
from python_api.get_secrets import rapid_api_key, db_parameters
from python_api.rapid_apis import EVENTS_URL

# MySQL database configuration
db_config = {
    'user': db_parameters['username'],
    'password': db_parameters['password'],
    'host': db_parameters['host'],
    'database': 'base_data_apis'
}

def insert_fixture_events(cur, event_id, fixture_id, team_id, player_id, type, detail, comments, minute, extra_minute, result, assist_id):
    sql = """
        INSERT INTO fixture_events (event_id, fixture_id, team_id, player_id, type, detail, comments, minute, extra_minute, result, assist_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE event_id=event_id
    """
    cur.execute(sql, (event_id, fixture_id, team_id, player_id, type, detail, comments, minute, extra_minute, result, assist_id))

def load_fixture_events(query):
    # Connect to MySQL database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Execute the query
    cursor.execute(query)
    fixtures = cursor.fetchall()

    # Iterate over fixtures
    for fixture in fixtures:
        fixture_id = fixture[0]
        # print(fixture_id)
        
        params = {"fixture": fixture_id}

        # Fetch fixture event data
        response = requests.get(EVENTS_URL, headers={"X-RapidAPI-Key": rapid_api_key}, params=params)
        event_data = response.json()

        try:
            event_data = event_data['response']
        except KeyError:
            event_data = []

        # Store fixture events in the database
        for index, event in enumerate(event_data, start=1):
            # fixture_id = event['fixture_id']
            sequential_number = index

            # Generate the event ID by combining the fixture ID and sequential number
            event_id = f"{fixture_id}{sequential_number}" # Generate a unique event_id using UUID
            team_id = event['team']['id']
            type = event['type']
            detail = event['detail']
            comments = event['comments']

            player_id = None
            assist_id = None

            if 'player' in event:
                player_id = event['player']['id']

            if 'assist' in event:
                assist_id = event['assist']['id']

            minute = event['time']['elapsed']
            extra_minute = event['time'].get('extra', None)
            result = None

            # Insert fixture event
            insert_fixture_events(cursor, event_id, fixture_id, team_id, player_id, type, detail, comments, minute, extra_minute, result, assist_id)

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()
