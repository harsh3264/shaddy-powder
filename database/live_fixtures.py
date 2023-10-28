import sys
import os
import mysql.connector
import requests
import datetime
import time
import pytz

# Get the current timestamp in seconds
current_timestamp = int(time.time())

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

# Function to insert or update fixture data into the "live_fixtures" table
def upsert_live_fixture(cursor, fixture):
    fixture_id = fixture['fixture']['id']
    referee = fixture['fixture']['referee']
    fixture_date = fixture['fixture']['date'].split('T')[0]
    venue_id = fixture['fixture']['venue']['id']
    status = fixture['fixture']['status']['short']
    elapsed = fixture['fixture']['status']['elapsed']
    season_year = fixture['league']['season']
    home_team_id = fixture['teams']['home']['id']
    away_team_id = fixture['teams']['away']['id']
    league_id = fixture['league']['id']
    league_round = fixture['league']['round']
    total_home_goals = fixture['goals']['home'] if 'goals' in fixture and 'home' in fixture['goals'] else None
    ht_home_goals = fixture['score']['halftime']['home'] if 'score' in fixture and 'fulltime' in fixture['score'] else None
    ft_home_goals = fixture['score']['fulltime']['home'] if 'score' in fixture and 'fulltime' in fixture['score'] else None
    et_home_goals = fixture['score']['extratime']['home'] if 'score' in fixture and 'extratime' in fixture['score'] else None
    pt_home_goals = fixture['score']['penalty']['home'] if 'score' in fixture and 'penalty' in fixture['score'] else None
    total_away_goals = fixture['goals']['away'] if 'goals' in fixture and 'away' in fixture['goals'] else None
    ht_away_goals = fixture['score']['halftime']['away'] if 'score' in fixture and 'fulltime' in fixture['score'] else None
    ft_away_goals = fixture['score']['fulltime']['away'] if 'score' in fixture and 'fulltime' in fixture['score'] else None
    et_away_goals = fixture['score']['extratime']['away'] if 'score' in fixture and 'extratime' in fixture['score'] else None
    pt_away_goals = fixture['score']['penalty']['away'] if 'score' in fixture and 'penalty' in fixture['score'] else None
    timestamp = fixture['fixture']['timestamp']

    # Get the current timestamp for London time
    london_timezone = pytz.timezone('Europe/London')
    current_script_timestamp = datetime.datetime.now(london_timezone).strftime('%Y-%m-%d %H:%M:%S')


    # Prepare the SQL query for upsert with ON DUPLICATE KEY UPDATE clause
    upsert_query = '''
    INSERT INTO live_updates.live_fixtures
    (fixture_id, referee, fixture_date, venue_id, status, elapsed, season_year, home_team_id, away_team_id, league_id, league_round,
    total_home_goals, ht_home_goals, ft_home_goals, et_home_goals, pt_home_goals, total_away_goals, ht_away_goals, ft_away_goals, et_away_goals, pt_away_goals, `timestamp`, london_update_time)
    VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    referee = VALUES(referee),
    fixture_date = VALUES(fixture_date),
    venue_id = VALUES(venue_id),
    status = VALUES(status),
    elapsed = VALUES(elapsed),
    season_year = VALUES(season_year),
    home_team_id = VALUES(home_team_id),
    away_team_id = VALUES(away_team_id),
    league_id = VALUES(league_id),
    league_round = VALUES(league_round),
    total_home_goals = VALUES(total_home_goals),
    ht_home_goals = VALUES(ht_home_goals),
    ft_home_goals = VALUES(ft_home_goals),
    et_home_goals = VALUES(et_home_goals),
    pt_home_goals = VALUES(pt_home_goals),
    total_away_goals = VALUES(total_away_goals),
    ht_away_goals = VALUES(ht_away_goals),
    ft_away_goals = VALUES(ft_away_goals),
    et_away_goals = VALUES(et_away_goals),
    pt_away_goals = VALUES(pt_away_goals),
    `timestamp` = VALUES(`timestamp`),
    london_update_time = VALUES(london_update_time)
    '''

    # Execute the SQL query with the appropriate values for insert/update
    values = (
        fixture_id, referee, fixture_date, venue_id, status,
        elapsed, season_year, home_team_id, away_team_id, league_id, league_round,
        total_home_goals, ht_home_goals, ft_home_goals, et_home_goals, pt_home_goals,
        total_away_goals, ht_away_goals, ft_away_goals, et_away_goals, pt_away_goals,
        timestamp, current_script_timestamp  # Include the current script runtime timestamp
    )
    cursor.execute(upsert_query, values)

# Establish a connection to the MySQL database
db_conn = mysql.connector.connect(**db_config)
cursor = db_conn.cursor()

# Truncate the live_fixtures table to delete all existing data
truncate_query = "TRUNCATE TABLE live_updates.live_fixtures"
cursor.execute(truncate_query)

# Fetch the league and season data from the database
query = '''
    SELECT DISTINCT f.league_id, season_year
    FROM fixtures f
    INNER JOIN top_leagues tl on f.league_id = tl.league_id
    WHERE 1 = 1
    # AND fixture_date = CURDATE()
    AND timestamp > UNIX_TIMESTAMP(NOW()  - INTERVAL 120 MINUTE)
    AND timestamp < UNIX_TIMESTAMP(NOW()  + INTERVAL 60 MINUTE);
'''
cursor.execute(query)
league_season_data = cursor.fetchall()

# Iterate over the league and season data
for league_id, season_year in league_season_data:
    params = {"season": season_year, "league": league_id}

    # Fetch the API data
    headers = {
        'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
        'x-rapidapi-key': rapid_api_key
    }

    # Make the API request to fetch fixtures data
    response = requests.get(FIXTURES_URL, headers=headers, params=params)
    fixtures = response.json()["response"]

    # Filter out fixtures older than 7 days
    current_date = datetime.date.today()

    filtered_fixtures = [fixture for fixture in fixtures if (
        (current_date - datetime.datetime.strptime(fixture['fixture']['date'].split('T')[0], '%Y-%m-%d').date()).days <= 2
        or (current_date - datetime.datetime.strptime(fixture['fixture']['date'].split('T')[0], '%Y-%m-%d').date()).days < 0)
    ]

    # # Iterate over the fixtures data
    for fixture in filtered_fixtures:
        status = fixture['fixture']['status']['short']
        timestamp = fixture['fixture']['timestamp']
        if (
            status in ('2H', '1H', 'HT', 'ET') or
            (status == 'NS' and timestamp >= current_timestamp and timestamp <= current_timestamp + 3600)
        ):
            upsert_live_fixture(cursor, fixture)

# Commit the changes and close the database connection
db_conn.commit()
cursor.close()
db_conn.close()
