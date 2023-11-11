import sys
import os
import mysql.connector
import requests
import datetime
import time
import pytz

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the necessary modules
from python_api.get_secrets import rapid_api_key, db_parameters
from python_api.rapid_apis import ODDS_URL

# Replace the placeholders with your MySQL database credentials
db_config = {
    'user': db_parameters['username'],
    'password': db_parameters['password'],
    'host': db_parameters['host'],
    'database': 'base_data_apis'
}

# Define the query to select `fixture_id` from the `today_fixture` table
today_fixture_query = "SELECT DISTINCT fixture_id FROM fixtures WHERE fixture_date BETWEEN CURDATE() AND CURDATE() + INTERVAL 2 DAY;"

# Establish a connection to the MySQL database
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

# Fetch the `fixture_id` values from the `today_fixture` table
cursor.execute(today_fixture_query)
today_fixture_ids = [row[0] for row in cursor]

# Get the current timestamp for London time
london_timezone = pytz.timezone('Europe/London')
current_script_timestamp = datetime.datetime.now(london_timezone).strftime('%Y-%m-%d %H:%M:%S')

# Delete existing odds data for `fixture_id` values in the `today_fixture` table
delete_query = "DELETE FROM fixture_odds WHERE fixture_id IN ({})".format(','.join(map(str, today_fixture_ids)))
cursor.execute(delete_query)

# Fetch the API data for odds for each `fixture_id`
headers = {
    'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
    'x-rapidapi-key': rapid_api_key
}

for fixture_id in today_fixture_ids:
    querystring = {"fixture": fixture_id}
    response = requests.get(ODDS_URL, headers=headers, params=querystring)
    data = response.json()

    # Loop through the odds data and extract relevant information
    for fixture_data in data['response']:
        fixture_id = fixture_data['fixture']['id']
        bookmakers = fixture_data.get('bookmakers', [])
        for bookmaker in bookmakers:
            bookmaker_id = bookmaker.get('id')
            bets = bookmaker.get('bets', [])
            for bet in bets:
                bet_type_id = bet.get('id')
                bet_name = bet.get('name')
                odds_values = bet.get('values', [])
                for odd_value in odds_values:
                    value_type = odd_value.get('value')
                    odd = odd_value.get('odd')
                    insert_query = '''
                    INSERT INTO fixture_odds (fixture_id, bookmaker_id, bet_type_id, bet_name, value_type, odd, london_update_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    '''
                    values = (fixture_id, bookmaker_id, bet_type_id, bet_name, value_type, odd, current_script_timestamp)
                    # Execute the query with the odds data
                    cursor.execute(insert_query, values)

# Commit the changes to the database
connection.commit()

# Close the cursor and the database connection
cursor.close()
connection.close()
