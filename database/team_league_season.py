import sys
import os
import requests
import mysql.connector
import time

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the necessary modules
from python_api.get_secrets import rapid_api_key, db_parameters
from python_api.rapid_apis import TEAMS_URL

# Replace the placeholders with your MySQL database credentials
db_config = {
    'user': db_parameters['username'],
    'password': db_parameters['password'],
    'host': db_parameters['host'],
    'database': 'base_data_apis'
}

# Establish a connection to the MySQL database
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

# Fetch the distinct season_year and league_id combinations from the leagues table
query = "SELECT DISTINCT season_year, league_id FROM leagues WHERE season_year >= 2022"
cursor.execute(query)
combinations = cursor.fetchall()

# Prepare the SQL queries for insertion and update
insert_query = "INSERT INTO team_league_season (team_id, league_id, season_year, team_code) VALUES (%s, %s, %s, %s)"
update_query = "UPDATE team_league_season SET team_code = %s WHERE team_id = %s AND season_year = %s AND league_id = %s"

# Iterate over each combination of season_year and league_id
for combination in combinations:
    season_year = combination[0]
    league_id = combination[1]
    # print(f"Processing combination: season_year={season_year}, league_id={league_id}")

    # Make a request to the teams API for the given season_year and league_id
    headers = {
        'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
        'x-rapidapi-key': rapid_api_key
    }
    querystring = {
        'season': season_year,
        'league': league_id
    }
    response = requests.get(TEAMS_URL, headers=headers, params=querystring)
    data = response.json()

    # Extract the team IDs and team codes from the response
    teams = data.get('response', [])
    team_data = [(team.get('team', {}).get('id'), team.get('team', {}).get('code')) for team in teams]

    # Check if the team IDs already exist in the team_league_season table
    cursor.execute("SELECT team_id FROM team_league_season WHERE season_year = %s AND league_id = %s",
                   (season_year, league_id))
    existing_teams = set(row[0] for row in cursor.fetchall())

    # Insert or update team codes in the team_league_season table
    for team_id, team_code in team_data:
        if team_id in existing_teams:
            cursor.execute(update_query, (team_code, team_id, season_year, league_id))
            # print(f"Updating team: team_id={team_id}, team_code={team_code}")
        else:
            cursor.execute(insert_query, (team_id, league_id, season_year, team_code))
            # print(f"Inserting team: team_id={team_id}, team_code={team_code}")

    # Add a time delay of 1 second
    time.sleep(1)

# Commit the changes to the database
connection.commit()

# Close the cursor and the database connection
cursor.close()
connection.close()
