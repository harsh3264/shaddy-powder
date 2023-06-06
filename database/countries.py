import sys
import os

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the necessary modules
from python_api.get_secrets import rapid_api_key, db_parameters
from python_api.rapid_apis import COUNTRIES_URL
import mysql.connector
import requests

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
response = requests.get(COUNTRIES_URL, headers=headers)
data = response.json()["response"]

# Prepare the SQL query
query = "INSERT INTO countries (name, code, flag) VALUES (%s, %s, %s)"

# Insert each country's data into the table
for country in data:
    name = country.get('name', '')
    code = country.get('code')
    flag = country.get('flag')
    values = (name, code, flag)

    # Execute the query with the country's data
    cursor.execute(query, values)

# Commit the changes to the database
connection.commit()

# Close the cursor and the database connection
cursor.close()
connection.close()
