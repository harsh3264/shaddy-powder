import sys
import os
import mysql.connector
import requests

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

# Fetch the API data
headers = {
    'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
    'x-rapidapi-key': rapid_api_key
}

# Retrieve countries from the database
cursor.execute("SELECT name FROM countries")
country_names = cursor.fetchall()

# Prepare the SQL query for insert
# ...

# Prepare the SQL queries
insert_query = '''
INSERT INTO teams (
    team_id, name, country, logo, founded,
    national, venue_id, venue_name,
    venue_address, venue_city, venue_capacity,
    venue_surface, venue_image
)
VALUES (
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s
)
'''

update_query = '''
UPDATE teams
SET name = %s, country = %s, logo = %s, founded = %s,
    national = %s, venue_id = %s, venue_name = %s,
    venue_address = %s, venue_city = %s, venue_capacity = %s,
    venue_surface = %s, venue_image = %s
WHERE team_id = %s
'''

# Insert or update data for each country's teams
for country_name in country_names:
    params = {
        'country': country_name[0]  # Extract the country name from the fetched result
    }
    response = requests.get(TEAMS_URL, headers=headers, params=params)
    data = response.json()["response"]

    # Insert or update data for each team
    for team_data in data:
        team = team_data.get('team')

        team_id = team.get('id')
        name = team.get('name', '')
        country = team.get('country', '')
        logo = team.get('logo', '')
        founded = team.get('founded')
        national = team.get('national')

        venue = team_data.get('venue', {})   # Access venue information from team_data

        # Check if venue information is available
        if venue:
            venue_id = venue.get('id')
            venue_name = venue.get('name', '')
            venue_address = venue.get('address', '')
            venue_city = venue.get('city', '')
            venue_capacity = venue.get('capacity')
            venue_surface = venue.get('surface', '')
            venue_image = venue.get('image', '')
        else:
            venue_id = None
            venue_name = None
            venue_address = None
            venue_city = None
            venue_capacity = None
            venue_surface = None
            venue_image = None

        values = (
            name, country, logo, founded,
            national, venue_id, venue_name,
            venue_address, venue_city, venue_capacity,
            venue_surface, venue_image, team_id
        )

        try:
            # Try to execute the INSERT query
            cursor.execute(insert_query, values)
        except mysql.connector.errors.IntegrityError:
            # If the INSERT fails due to duplicate entry, execute the UPDATE query
            cursor.execute(update_query, values)

# Commit the changes to the database
connection.commit()

# Close the cursor and the database connection
cursor.close()
connection.close()
