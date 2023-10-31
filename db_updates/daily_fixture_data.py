# Import the MySQL connector
import mysql.connector
# from mysql.connector import errorcode
import os
import sys

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the necessary modules
from python_api.get_secrets import db_parameters

db_config = {
    'user': db_parameters['username'],
    'password': db_parameters['password'],
    'host': db_parameters['host'],
    'database': 'base_data_apis'
}

# SQL statements to execute
sql_statements = [
    '''
    DROP TABLE IF EXISTS top_leagues
    ;
    ''',
    '''
    CREATE TABLE top_leagues AS
    SELECT league_id,
           COUNT(DISTINCT team_id) AS teams
    FROM team_league_season
    WHERE 1 = 1
    AND ((team_id IN (SELECT home_team_id
                     FROM fixtures
                     WHERE league_id IN (2, 3)
                       AND season_year = 2023)
            OR
         team_id IN (SELECT home_team_id
                     FROM fixtures
                     WHERE league_id IN (1))
        )
             OR
         league_id IN (40, 41, 71, 188, 253))
    AND season_year >= 2022
    GROUP BY 1
    HAVING teams > 3
    ORDER BY 2 DESC
    ;
    ''',
    '''
    DROP TABLE IF EXISTS today_fixture
    ;
    ''',
    '''
    CREATE TABLE today_fixture
    AS
    SELECT
        f.fixture_id,
        f.season_year,
        l.league_id,
        l.name,
        l.country_name,
        f.fixture_date,
        f.home_team_id,
        f.away_team_id,
        f.timestamp,
        DATE_FORMAT(CONVERT_TZ(FROM_UNIXTIME(f.timestamp), 'UTC', 'Europe/London'), '%H:%i') AS match_time,
        t1.name AS home_team,
        t2.name AS away_team,
        f.referee,
        cr.cleaned_referee_name,
        CONCAT(t1.name, ' vs ', t2.name) AS fixt
    FROM fixtures f
    JOIN leagues l ON f.league_id = l.league_id
    JOIN teams t1 ON f.home_team_id = t1.team_id
    JOIN teams t2 ON f.away_team_id = t2.team_id
    JOIN top_leagues tl on f.league_id = tl.league_id
    LEFT JOIN cleaned_referees cr ON f.referee = cr.original_referee_name
    WHERE 1 = 1
    AND fixture_date BETWEEN CURDATE() AND CURDATE() + INTERVAL 1 DAY
    GROUP BY 1
    ORDER BY f.timestamp
    ;
    '''
]


db_conn = mysql.connector.connect(**db_config)
cursor = db_conn.cursor()

# Execute each SQL statement
for sql in sql_statements:
    # print(sql)
    cursor.execute(sql)
    # referee_data = cursor.fetchall()
    # print(referee_data)
    
db_conn.commit()
cursor.close()
db_conn.close()

# # Function to execute SQL statements
# def execute_sql(sql_statements, db_config):
#     try:
#         # Connect to the database
#         db_conn = mysql.connector.connect(**db_config)
#         cursor = db_conn.cursor()

#         # Execute each SQL statement
#         for sql in sql_statements:
#             print(sql)
#             cursor.execute(sql, multi=True)
        
#         db_conn.commit()
#         cursor.close()
#         db_conn.close()

#         print("SQL statements executed successfully.")
#     except mysql.connector.Error as err:
#         if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
#             print("Access denied: Check your database username and password.")
#         elif err.errno == errorcode.ER_BAD_DB_ERROR:
#             print("Database does not exist.")
#         else:
#             print(f"Error: {err}")

# if __name__ == "__main__":
#     execute_sql(sql_statements, db_config)
