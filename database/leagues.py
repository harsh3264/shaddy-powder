import sys
import os

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the necessary modules
from python_api.get_secrets import rapid_api_key, db_parameters
from python_api.rapid_apis import LEAGUES_URL
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
response = requests.get(LEAGUES_URL, headers=headers)
data = response.json()["response"]

# Prepare the SQL query
query = '''
INSERT INTO leagues (
    league_id, name, type, logo,
    country_name, country_code, country_flag,
    season_year, season_start, season_end,
    season_coverage_fixtures_events, season_coverage_fixtures_lineups,
    season_coverage_fixtures_statistics_fixtures, season_coverage_fixtures_statistics_players,
    season_coverage_standings, season_coverage_players,
    season_coverage_top_scorers, season_coverage_top_assists,
    season_coverage_top_cards, season_coverage_injuries,
    season_coverage_predictions, season_coverage_odds
)
VALUES (
    %s, %s, %s, %s,
    %s, %s, %s,
    %s, %s, %s,
    %s, %s, %s, %s,
    %s, %s, %s, %s,
    %s, %s, %s, %s
)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    type = VALUES(type),
    logo = VALUES(logo),
    country_name = VALUES(country_name),
    country_code = VALUES(country_code),
    country_flag = VALUES(country_flag),
    season_start = VALUES(season_start),
    season_end = VALUES(season_end),
    season_coverage_fixtures_events = VALUES(season_coverage_fixtures_events),
    season_coverage_fixtures_lineups = VALUES(season_coverage_fixtures_lineups),
    season_coverage_fixtures_statistics_fixtures = VALUES(season_coverage_fixtures_statistics_fixtures),
    season_coverage_fixtures_statistics_players = VALUES(season_coverage_fixtures_statistics_players),
    season_coverage_standings = VALUES(season_coverage_standings),
    season_coverage_players = VALUES(season_coverage_players),
    season_coverage_top_scorers = VALUES(season_coverage_top_scorers),
    season_coverage_top_assists = VALUES(season_coverage_top_assists),
    season_coverage_top_cards = VALUES(season_coverage_top_cards),
    season_coverage_injuries = VALUES(season_coverage_injuries),
    season_coverage_predictions = VALUES(season_coverage_predictions),
    season_coverage_odds = VALUES(season_coverage_odds)
'''

# Insert data for each league and season
for league_data in data:
    league = league_data.get('league')
    country = league_data.get('country')
    seasons = league_data.get('seasons')
    
    # print(league)

    league_id = league.get('id')
    name = league.get('name', '')
    type = league.get('type', '')
    logo = league.get('logo', '')

    country_name = country.get('name', '')
    country_code = country.get('code')
    country_flag = country.get('flag')

    for season in seasons:
        season_year = season.get('year')
        season_start = season.get('start')
        season_end = season.get('end')
        season_coverage = season.get('coverage', {})

        season_coverage_fixtures_events = season_coverage.get('fixtures', {}).get('events')
        season_coverage_fixtures_lineups = season_coverage.get('fixtures', {}).get('lineups')
        season_coverage_fixtures_statistics_fixtures = season_coverage.get('fixtures', {}).get('statistics_fixtures')
        season_coverage_fixtures_statistics_players = season_coverage.get('fixtures', {}).get('statistics_players')
        season_coverage_standings = season_coverage.get('standings')
        season_coverage_players = season_coverage.get('players')
        season_coverage_top_scorers = season_coverage.get('top_scorers')
        season_coverage_top_assists = season_coverage.get('top_assists')
        season_coverage_top_cards = season_coverage.get('top_cards')
        season_coverage_injuries = season_coverage.get('injuries')
        season_coverage_predictions = season_coverage.get('predictions')
        season_coverage_odds = season_coverage.get('odds')

        values = (
            league_id, name, type, logo,
            country_name, country_code, country_flag,
            season_year, season_start, season_end,
            season_coverage_fixtures_events, season_coverage_fixtures_lineups,
            season_coverage_fixtures_statistics_fixtures, season_coverage_fixtures_statistics_players,
            season_coverage_standings, season_coverage_players,
            season_coverage_top_scorers, season_coverage_top_assists,
            season_coverage_top_cards, season_coverage_injuries,
            season_coverage_predictions, season_coverage_odds
        )

        # Execute the query with the league's data
        cursor.execute(query, values)

# Commit the changes to the database
connection.commit()

# Close the cursor and the database connection
cursor.close()
connection.close()
