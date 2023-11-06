import sys
import os
import mysql.connector
import requests

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the necessary modules
from python_api.get_secrets import rapid_api_key, db_parameters
from python_api.rapid_apis import BOOKMAKERS_URL

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
response = requests.get(BOOKMAKERS_URL, headers=headers)
data = response.json()

# Prepare the SQL query to insert bookie data
insert_query = '''
INSERT INTO bookmakers (bookmaker_id, bookmaker_name)
VALUES (%s, %s)
ON DUPLICATE KEY UPDATE
bookmaker_name = VALUES(bookmaker_name)
'''

# Insert data for each bookie
for bookmaker_data in data['response']:
    bookmaker_id = bookmaker_data.get('id')
    bookmaker_name = bookmaker_data.get('name', '')

    values = (bookmaker_id, bookmaker_name)

    # Execute the query with the bookie's data
    cursor.execute(insert_query, values)

# Commit the changes to the database
connection.commit()

# Close the cursor and the database connection
cursor.close()
connection.close()
