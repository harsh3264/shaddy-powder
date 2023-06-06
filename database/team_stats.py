import sys
import os
import mysql.connector
import requests
import time

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the necessary modules
from python_api.get_secrets import rapid_api_key, db_parameters
from python_api.rapid_apis import TEAM_STATS_URL

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

# Retrieve team_league_season data from the database
cursor.execute("""
SELECT
    DISTINCT
    tls.team_id,
    tls.league_id,
    tls.season_year,
    l.name,
    l.country_name
FROM team_league_season tls
JOIN leagues l ON tls.league_id = l.league_id
AND tls.season_year = l.season_year
JOIN teams t ON tls.team_id = t.team_id
WHERE season_coverage_fixtures_statistics_fixtures = 1
AND season_coverage_fixtures_statistics_players = 1
AND tls.season_year = 2022
AND (tls.team_id, tls.league_id) NOT IN (
    SELECT team_id, league_id
    FROM team_stats
    WHERE season_year = 2022)
""")
team_league_season_data = cursor.fetchall()

# Prepare the SQL query for insert
insert_query = '''
INSERT INTO team_stats (
    team_id, league_id, season_year, form, played_home, played_away, played_total,
    wins_home, wins_away, wins_total, draws_home, draws_away, draws_total,
    loses_home, loses_away, loses_total, goals_for_home, goals_for_away,
    goals_for_total, goals_against_home, goals_against_away, goals_against_total,
    biggest_wins_home, biggest_wins_away, biggest_loses_home, biggest_loses_away, penalty_scored,
    penalty_missed, clean_sheet_home, clean_sheet_away, clean_sheet_total,
    failed_to_score_home, failed_to_score_away, failed_to_score_total,
    yellow_cards_total, red_cards_total, goals_0_15, goals_16_30, goals_31_45,
    goals_46_60, goals_61_75, goals_76_90, goals_91_105, goals_106_120,
    yellow_cards_0_15, yellow_cards_16_30, yellow_cards_31_45, yellow_cards_46_60,
    yellow_cards_61_75, yellow_cards_76_90, yellow_cards_91_105, yellow_cards_106_120,
    red_cards_0_15, red_cards_16_30, red_cards_31_45, red_cards_46_60,
    red_cards_61_75, red_cards_76_90, red_cards_91_105, red_cards_106_120
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s
)
'''

# Prepare the SQL query for updating team stats
update_query = '''
UPDATE team_stats
SET form = %s, played_home = %s, played_away = %s, played_total = %s,
    wins_home = %s, wins_away = %s, wins_total = %s,
    draws_home = %s, draws_away = %s, draws_total = %s,
    loses_home = %s, loses_away = %s, loses_total = %s,
    goals_for_home = %s, goals_for_away = %s, goals_for_total = %s,
    goals_against_home = %s, goals_against_away = %s, goals_against_total = %s,
    biggest_wins_home = %s, biggest_wins_away = %s, biggest_loses_home = %s,
    biggest_loses_away = %s, penalty_scored = %s, penalty_missed = %s,
    clean_sheet_home = %s, clean_sheet_away = %s, clean_sheet_total = %s,
    failed_to_score_home = %s, failed_to_score_away = %s, failed_to_score_total = %s,
    yellow_cards_total = %s, red_cards_total = %s,
    goals_0_15 = %s, goals_16_30 = %s, goals_31_45 = %s,
    goals_46_60 = %s, goals_61_75 = %s, goals_76_90 = %s,
    goals_91_105 = %s, goals_106_120 = %s,
    yellow_cards_0_15 = %s, yellow_cards_16_30 = %s, yellow_cards_31_45 = %s,
    yellow_cards_46_60 = %s, yellow_cards_61_75 = %s, yellow_cards_76_90 = %s,
    yellow_cards_91_105 = %s, yellow_cards_106_120 = %s,
    red_cards_0_15 = %s, red_cards_16_30 = %s, red_cards_31_45 = %s,
    red_cards_46_60 = %s, red_cards_61_75 = %s, red_cards_76_90 = %s,
    red_cards_91_105 = %s, red_cards_106_120 = %s
WHERE team_id = %s AND league_id = %s AND season_year = %s
'''


# Process the response data and insert into the database
for tls_data in team_league_season_data:
    team_id = tls_data[0]
    league_id = tls_data[1]
    season_year = tls_data[2]
    league_name = tls_data[3]
    country = tls_data[4]

    params = {
        'league': league_id,
        'team': team_id,
        'season': season_year
    }
    response = requests.get(TEAM_STATS_URL, headers=headers, params=params)
    
    data = response.json()["response"]

    # Extract the stats data from the response
    fixtures = data.get('fixtures', {})
    goals = data.get('goals', {})
    biggest = data.get('biggest', {})
    clean_sheet = data.get('clean_sheet', {})
    failed_to_score = data.get('failed_to_score', {})
    penalty = data.get('penalty', {})
    cards = data.get('cards', {})
    
    form = data.get('form', '')
    played_home = fixtures.get('played', {}).get('home', 0)
    played_away = fixtures.get('played', {}).get('away', 0)
    played_total = fixtures.get('played', {}).get('total', 0)
    wins_home = fixtures.get('wins', {}).get('home', 0)
    wins_away = fixtures.get('wins', {}).get('away', 0)
    wins_total = fixtures.get('wins', {}).get('total', 0)
    draws_home = fixtures.get('draws', {}).get('home', 0)
    draws_away = fixtures.get('draws', {}).get('away', 0)
    draws_total = fixtures.get('draws', {}).get('total', 0)
    loses_home = fixtures.get('loses', {}).get('home', 0)
    loses_away = fixtures.get('loses', {}).get('away', 0)
    loses_total = fixtures.get('loses', {}).get('total', 0)
    goals_for_home = goals.get('for', {}).get('total', {}).get('home', 0)
    goals_for_away = goals.get('for', {}).get('total', {}).get('away', 0)
    goals_for_total = goals.get('for', {}).get('total', {}).get('total', 0)
    goals_against_home = goals.get('against', {}).get('total', {}).get('home', 0)
    goals_against_away = goals.get('against', {}).get('total', {}).get('away', 0)
    goals_against_total = goals.get('against', {}).get('total', {}).get('total', 0)
    biggest_wins_home = biggest.get('wins', {}).get('home', 0)
    biggest_wins_away = biggest.get('wins', {}).get('away', 0)
    biggest_loses_home = biggest.get('loses', {}).get('home', 0)
    biggest_loses_away = biggest.get('loses', {}).get('away', 0)
    penalty_scored = penalty.get('scored', {}).get('total', 0)
    penalty_missed = penalty.get('missed', {}).get('total', 0)
    clean_sheet_home = clean_sheet.get('home', 0)
    clean_sheet_away = clean_sheet.get('away', 0)
    clean_sheet_total = clean_sheet.get('total', 0)
    failed_to_score_home = failed_to_score.get('home', 0)
    failed_to_score_away = failed_to_score.get('away', 0)
    failed_to_score_total = failed_to_score.get('total', 0)
    
    goals_0_15 = goals.get('for', {}).get('minute', {}).get('0-15', {}).get('total', 0)
    goals_16_30 = goals.get('for', {}).get('minute', {}).get('16-30', {}).get('total', 0)
    goals_31_45 = goals.get('for', {}).get('minute', {}).get('31-45', {}).get('total', 0)
    goals_46_60 = goals.get('for', {}).get('minute', {}).get('46-60', {}).get('total', 0)
    goals_61_75 = goals.get('for', {}).get('minute', {}).get('61-75', {}).get('total', 0)
    goals_76_90 = goals.get('for', {}).get('minute', {}).get('76-90', {}).get('total', 0)
    goals_91_105 = goals.get('for', {}).get('minute', {}).get('91-105', {}).get('total', 0)
    goals_106_120 = goals.get('for', {}).get('minute', {}).get('106-120', {}).get('total', 0)
    
    yellow_cards_0_15 = cards.get('yellow', {}).get('0-15', {}).get('total', 0) or 0
    yellow_cards_16_30 = cards.get('yellow', {}).get('16-30', {}).get('total', 0) or 0
    yellow_cards_31_45 = cards.get('yellow', {}).get('31-45', {}).get('total', 0) or 0
    yellow_cards_46_60 = cards.get('yellow', {}).get('46-60', {}).get('total', 0) or 0
    yellow_cards_61_75 = cards.get('yellow', {}).get('61-75', {}).get('total', 0) or 0
    yellow_cards_76_90 = cards.get('yellow', {}).get('76-90', {}).get('total', 0) or 0
    yellow_cards_91_105 = cards.get('yellow', {}).get('91-105', {}).get('total', 0) or 0
    yellow_cards_106_120 = cards.get('yellow', {}).get('106-120', {}).get('total', 0) or 0
    
    yellow_cards_total = (
        yellow_cards_0_15 +
        yellow_cards_16_30 +
        yellow_cards_31_45 +
        yellow_cards_46_60 +
        yellow_cards_61_75 +
        yellow_cards_76_90 +
        yellow_cards_91_105 +
        yellow_cards_106_120
    )
    
    red_cards_0_15 = cards.get('red', {}).get('0-15', {}).get('total', 0) or 0
    red_cards_16_30 = cards.get('red', {}).get('16-30', {}).get('total', 0) or 0
    red_cards_31_45 = cards.get('red', {}).get('31-45', {}).get('total', 0) or 0
    red_cards_46_60 = cards.get('red', {}).get('46-60', {}).get('total', 0) or 0
    red_cards_61_75 = cards.get('red', {}).get('61-75', {}).get('total', 0) or 0
    red_cards_76_90 = cards.get('red', {}).get('76-90', {}).get('total', 0) or 0
    red_cards_91_105 = cards.get('red', {}).get('91-105', {}).get('total', 0) or 0
    red_cards_106_120 = cards.get('red', {}).get('106-120', {}).get('total', 0) or 0
    
    
    red_cards_total = (
        red_cards_0_15 +
        red_cards_16_30 +
        red_cards_31_45 +
        red_cards_46_60 +
        red_cards_61_75 +
        red_cards_76_90 +
        red_cards_91_105 +
        red_cards_106_120
    )
    
    
    # Execute the SQL query
    values = (
        team_id, league_id, season_year, form, played_home, played_away, played_total,
        wins_home, wins_away, wins_total, draws_home, draws_away, draws_total,
        loses_home, loses_away, loses_total, goals_for_home, goals_for_away,
        goals_for_total, goals_against_home, goals_against_away, goals_against_total,
        biggest_wins_home, biggest_wins_away, biggest_loses_home, biggest_loses_away, penalty_scored,
        penalty_missed, clean_sheet_home, clean_sheet_away, clean_sheet_total,
        failed_to_score_home, failed_to_score_away, failed_to_score_total,
        yellow_cards_total, red_cards_total, goals_0_15, goals_16_30, goals_31_45,
        goals_46_60, goals_61_75, goals_76_90, goals_91_105, goals_106_120, 
        yellow_cards_0_15, yellow_cards_16_30, yellow_cards_31_45, yellow_cards_46_60, 
        yellow_cards_61_75, yellow_cards_76_90, yellow_cards_91_105, yellow_cards_106_120, 
        red_cards_0_15, red_cards_16_30, red_cards_31_45, red_cards_46_60, 
        red_cards_61_75, red_cards_76_90, red_cards_91_105, red_cards_106_120
    )
    

    cursor.execute(insert_query, values)
    connection.commit()
    
    # Add a time delay of 1 second
    time.sleep(1)

# Close the database connection
cursor.close()
connection.close()
