import sys
import os
import mysql.connector
import requests

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the necessary modules
from python_api.get_secrets import rapid_api_key, db_parameters
from python_api.rapid_apis import BETS_URL

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
response = requests.get(BETS_URL, headers=headers)
data = response.json()

# print(data)

# Prepare the SQL query to insert bet type data
insert_query = '''
INSERT INTO bet_types (bet_type_id, bet_type_name)
VALUES (%s, %s)
ON DUPLICATE KEY UPDATE
bet_type_name = VALUES(bet_type_name);
'''

# Insert data for each bet type
for bet_type_data in data['response']:
    bet_type_id = bet_type_data.get('id')
    bet_type_name = bet_type_data.get('name', '')

    values = (bet_type_id, bet_type_name)

    # Execute the query with the bet type's data
    cursor.execute(insert_query, values)

# Commit the changes to the database
connection.commit()

# Close the cursor and the database connection
cursor.close()
connection.close()
