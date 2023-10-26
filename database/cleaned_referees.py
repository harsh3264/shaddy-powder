# Import the MySQL connector
import mysql.connector
import os
import sys

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the necessary modules
from python_api.get_secrets import db_parameters

# import re

# def clean_referee(referee):
#     # First Level: Remove country name coming after the last comma
#     cleaned_referee = re.sub(r',\s*[A-Za-z]+$', '', referee)
    
#     # Second Level: Convert special characters to normal
#     cleaned_referee = cleaned_referee.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')

#     # Third Level: Normalize middle names and expansions
#     cleaned_referee = re.sub(r'\b\w\.\s*', '', cleaned_referee)

#     # Fourth Level: Normalize first name with . and full name
#     cleaned_referee = re.sub(r'^(.*?)\s[A-Za-z]+$', r'\1', cleaned_referee)

#     # Fifth Level: Remove any extra spaces
#     cleaned_referee = ' '.join(cleaned_referee.split())

#     # Sixth Level: Extract and format initials
#     name_parts = cleaned_referee.split()
#     if len(name_parts) >= 2:
#         initials = '.'.join(part[0].upper() + '.' for part in name_parts[:-1])
#         cleaned_referee = f'{initials} {name_parts[-1]}'

#     return cleaned_referee.strip()

import re

def clean_referee(referee):
    # First Level: Remove country name coming after the last comma
    cleaned_referee = re.sub(r',\s*[A-Za-z]+$', '', referee)

    # Second Level: Convert special characters to normal
    cleaned_referee = cleaned_referee.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace(
        'ú', 'u')

    # # Third Level: Normalize middle names and expansions
    # cleaned_referee = re.sub(r'\b[A-Z][a-z]+\s*', '', cleaned_referee)

    # Fourth Level: Normalize first name with . and full name
    # cleaned_referee = re.sub(r'^(.*?)\s+[A-Za-z]+,?$', r'\1', cleaned_referee)

    # Fifth Level: Remove any extra spaces
    cleaned_referee = ' '.join(cleaned_referee.split())

    # Sixth Level: Extract and format initials
    name_parts = cleaned_referee.split()

    if len(name_parts) > 1:
        initials = ' '.join(part[0].upper() + '.' for part in name_parts[:-1])
        cleaned_referee = f'{initials} {name_parts[-1]}'
    elif len(name_parts) == 1 and len(name_parts[0]) > 1:
        cleaned_referee = f'{name_parts[0][0].upper()}. {name_parts[0][1:]}'

    parts = cleaned_referee.split()

    # Check if there are more than two parts (initials and last name)
    if len(parts) > 2:
        # Take the first and last initials, and the last part as the last name
        cleaned_referee = f'{parts[0]} {parts[-1]}'
    else:
        # If there are only two parts, assume it's already in the simplified format
        cleaned_referee = cleaned_referee

    return cleaned_referee.strip()

# Replace the placeholders with your MySQL database credentials
db_config = {
    'user': db_parameters['username'],
    'password': db_parameters['password'],
    'host': db_parameters['host'],
    'database': 'base_data_apis'
}

# Function to upsert cleaned referee names into "Cleaned_Referees" table
def upsert_cleaned_referees(cursor, cleaned_referees):
    upsert_query = '''
    INSERT INTO cleaned_referees (original_referee_name, cleaned_referee_name)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE
    cleaned_referee_name = VALUES(cleaned_referee_name)
    '''
    cursor.executemany(upsert_query, cleaned_referees)

# Establish a connection to the MySQL database
db_conn = mysql.connector.connect(**db_config)
cursor = db_conn.cursor()

# Fetch referee names from the "fixtures" table
query = '''
        SELECT
        DISTINCT referee
        FROM fixtures
        WHERE 1 = 1
        # AND season_year > 2021
        # AND league_id IN (39, 40, 135, 140)
        AND referee NOT IN (SELECT original_referee_name FROM cleaned_referees)
'''
cursor.execute(query)
referee_data = cursor.fetchall()

# Debugging: Print referee_data to inspect its structure
# print(referee_data)

# Extract referee names from the tuples
referee_names = [ref[0] for ref in referee_data]

# Debugging: Print referee_names to inspect its content
# print(referee_names)

# Clean the referee names and create cleaned referee data
cleaned_referees = [(original_name, clean_referee(original_name)) for original_name in referee_names if isinstance(original_name, str)]


# Debugging: Print cleaned_referees to inspect its content
# print(cleaned_referees)

# Upsert the cleaned referee data into the "Cleaned_Referees" table
upsert_cleaned_referees(cursor, cleaned_referees)

# Commit the changes and close the database connection
db_conn.commit()
cursor.close()
db_conn.close()
