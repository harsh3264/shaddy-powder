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
from python_api.rapid_apis import FIXTURES_URL

# Replace the placeholders with your MySQL database credentials
db_config = {
    'user': db_parameters['username'],
    'password': db_parameters['password'],
    'host': db_parameters['host'],
    'database': 'base_data_apis'  # Use the live_updates database
}

# Establish a connection to the MySQL database
db_conn = mysql.connector.connect(**db_config)
cursor = db_conn.cursor()

# Fetch the league and season data from the database
query = '''
    SELECT fl.fixture_id,
           fl.team_id,
           fc.formation,
           fl.player_id,
           fl.player_pos,
           fl.grid
    FROM live_updates.live_fixture_lineups fl
    JOIN live_updates.live_fixture_coach fc on fl.fixture_id = fc.fixture_id AND fl.team_id = fc.team_id;
'''
cursor.execute(query)
league_season_data = cursor.fetchall()

def allocate_new_grid_and_insert_db(cursor, fixture_data):
    fixture_id, team_id, formation, player_id, player_pos, grid = fixture_data

    new_grid_size = 61
    new_grid = [[None] * new_grid_size for _ in range(new_grid_size)]

    # Count players in each row (X) based on frm
    frm_list = [int(num) for num in formation.split('-')]
    frm_layers = len(frm_list)

    old_x, old_y = map(int, grid.split(':'))

    if player_pos != 'G':  # Skip the goalkeeper
        if frm_layers == 4:
            new_x = {1: 0, 2: 8, 3: 23, 4: 38, 5: 53}[old_x]
        elif frm_layers == 3:
            new_x = {1: 0, 2: 11, 3: 31, 4: 51}[old_x]

        if frm_list[old_x - 2] == 1:
            new_y = 31
        elif frm_list[old_x - 2] == 2:
            new_y = {1: 21, 2: 41}[old_y]
        elif frm_list[old_x - 2] == 3:
            new_y = {1: 16, 2: 31, 3: 45}[old_y]
        elif frm_list[old_x - 2] == 4:
            new_y = {1: 12, 2: 24, 3: 37, 4: 49}[old_y]
        else:
            new_y = {1: 10, 2: 20, 3: 31, 4: 42, 5: 52}[old_y]

        new_grid[new_x][new_y] = player_id

        # Insert new_grid into the database
        for x in range(new_grid_size):
            for y in range(new_grid_size):
                if new_grid[x][y] is not None:
                    player_id = new_grid[x][y]
                    new_x, new_y = x, y
                    insert_query = f"INSERT INTO temp.new_grid_map (fixture_id, team_id, player_id, new_grid, x_grid, y_grid) " \
                                    f"VALUES ({fixture_id}, {team_id}, {player_id}, '{new_x}:{new_y}', {new_x}, {new_y}) " \
                                    f"ON DUPLICATE KEY UPDATE new_grid = VALUES(new_grid), x_grid = VALUES(x_grid), y_grid = VALUES(y_grid)"
                    cursor.execute(insert_query)
                    
# Iterate through the fetched data and call allocate_new_grid_and_insert_db for each fixture and team combination
for fixture_data in league_season_data:
    allocate_new_grid_and_insert_db(cursor, fixture_data)

# Commit the changes and close the database connection
db_conn.commit()
cursor.close()
db_conn.close()
