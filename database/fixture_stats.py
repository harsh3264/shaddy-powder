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
from python_api.rapid_apis import FIXTURE_STATS_URL

# MySQL database configuration
db_config = {
    'user': db_parameters['username'],
    'password': db_parameters['password'],
    'host': db_parameters['host'],
    'database': 'base_data_apis'
}

headers = {
    "x-rapidapi-key": rapid_api_key,
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
}

def insert_fixture_stats(fixture_id, team_id, team_name, against_team_id, against_team_name, stats_dict, against_stats_dict, is_home):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Extract the expected goals values or set them to None if not present
    expected_goals = stats_dict.get("expected_goals")
    against_expected_goals = against_stats_dict.get("expected_goals")

    # Set the expected goals fields to None if not present
    if expected_goals is None:
        expected_goals = None
    if against_expected_goals is None:
        against_expected_goals = None

    insert_query = '''
        INSERT INTO fixtures_stats (fixture_id, team_id, team_name, against_team_id, against_team_name, is_home, 
        shots_on_goal, shots_off_goal, total_shots, blocked_shots, shots_inside_box, shots_outside_box, 
        fouls, corner_kicks, offsides, ball_possession, yellow_cards, red_cards, goalkeeper_saves, total_passes,
        passes_accurate, passes_percentage, against_shots_on_goal, against_shots_off_goal, against_total_shots,
        against_blocked_shots, against_shots_inside_box, against_shots_outside_box, against_fouls,
        against_corner_kicks, against_offsides, against_ball_possession, against_yellow_cards,
        against_red_cards, against_goalkeeper_saves, against_total_passes, against_passes_accurate,
        against_passes_percentage, expected_goals, against_expected_goals)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        shots_on_goal = VALUES(shots_on_goal),
        shots_off_goal = VALUES(shots_off_goal),
        total_shots = VALUES(total_shots),
        blocked_shots = VALUES(blocked_shots),
        shots_inside_box = VALUES(shots_inside_box),
        shots_outside_box = VALUES(shots_outside_box),
        fouls = VALUES(fouls),
        corner_kicks = VALUES(corner_kicks),
        offsides = VALUES(offsides),
        ball_possession = VALUES(ball_possession),
        yellow_cards = VALUES(yellow_cards),
        red_cards = VALUES(red_cards),
        goalkeeper_saves = VALUES(goalkeeper_saves),
        total_passes = VALUES(total_passes),
        passes_accurate = VALUES(passes_accurate),
        passes_percentage = VALUES(passes_percentage),
        against_shots_on_goal = VALUES(against_shots_on_goal),
        against_shots_off_goal = VALUES(against_shots_off_goal),
        against_total_shots = VALUES(against_total_shots),
        against_blocked_shots = VALUES(against_blocked_shots),
        against_shots_inside_box = VALUES(against_shots_inside_box),
        against_shots_outside_box = VALUES(against_shots_outside_box),
        against_fouls = VALUES(against_fouls),
        against_corner_kicks = VALUES(against_corner_kicks),
        against_offsides = VALUES(against_offsides),
        against_ball_possession = VALUES(against_ball_possession),
        against_yellow_cards = VALUES(against_yellow_cards),
        against_red_cards = VALUES(against_red_cards),
        against_goalkeeper_saves = VALUES(against_goalkeeper_saves),
        against_total_passes = VALUES(against_total_passes),
        against_passes_accurate = VALUES(against_passes_accurate),
        against_passes_percentage = VALUES(against_passes_percentage),
        expected_goals = VALUES(expected_goals),
        against_expected_goals = VALUES(against_expected_goals)
    '''

    cursor.execute(insert_query, (
        fixture_id, team_id, team_name, against_team_id, against_team_name, is_home, 
        stats_dict.get("shots on goal"), stats_dict.get("shots off goal"),
        stats_dict.get("total shots"), stats_dict.get("blocked shots"), stats_dict.get("shots insidebox"),
        stats_dict.get("shots outsidebox"), stats_dict.get("fouls"), stats_dict.get("corner kicks"),
        stats_dict.get("offsides"), stats_dict.get("ball possession"), stats_dict.get("yellow cards"),
        stats_dict.get("red cards"), stats_dict.get("goalkeeper saves"), stats_dict.get("total passes"),
        stats_dict.get("passes accurate"), stats_dict.get("passes percentage"), against_stats_dict.get("shots on goal"),
        against_stats_dict.get("shots off goal"), against_stats_dict.get("total shots"),
        against_stats_dict.get("blocked shots"), against_stats_dict.get("shots insidebox"),
        against_stats_dict.get("shots outsidebox"), against_stats_dict.get("fouls"),
        against_stats_dict.get("corner kicks"), against_stats_dict.get("offsides"),
        against_stats_dict.get("ball possession"), against_stats_dict.get("yellow cards"),
        against_stats_dict.get("red cards"), against_stats_dict.get("goalkeeper saves"),
        against_stats_dict.get("total passes"), against_stats_dict.get("passes accurate"),
        against_stats_dict.get("passes percentage"), expected_goals, against_expected_goals
    ))

    conn.commit()
    cursor.close()
    conn.close()


def get_completed_fixtures(season_year):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    query = '''
        SELECT
            DISTINCT fixture_id
        FROM fixtures 
        WHERE season_year = %s
        AND elapsed >= 90
        AND fixture_date >= CURRENT_DATE - 7
        # AND fixture_id NOT IN (SELECT fixture_id FROM fixtures_stats)
        AND (home_team_id IN (SELECT home_team_id FROM fixtures WHERE league_id IN (39, 135, 140, 61, 188))
            OR
             away_team_id IN (SELECT away_team_id FROM fixtures WHERE league_id IN (39, 135, 140, 61, 188))
            )
    '''

    cursor.execute(query, (season_year,))
    completed_fixtures_list = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return completed_fixtures_list

def fetch_fixture_stats(fixture_id):
    fixture_string = {"fixture": str(fixture_id)}
    fixt_response = requests.get(FIXTURE_STATS_URL, headers=headers, params=fixture_string)

    if fixt_response.status_code == 200:
        fixt_data = fixt_response.json()
        if fixt_data["response"]:
            # Insert or update the fixture stats in the database
            home_team = fixt_data["response"][0]["team"]["name"]
            home_team_id = fixt_data["response"][0]["team"]["id"]
            away_team = fixt_data["response"][1]["team"]["name"]
            away_team_id = fixt_data["response"][1]["team"]["id"]
            stats_dict_home = {}
            stats_dict_away = {}
    
            # Create a dictionary of stats for home team
            for item in fixt_data["response"][0]["statistics"]:
                stats_dict_home[item["type"].lower()] = item["value"]
    
            # Create a dictionary of stats for away team
            for item in fixt_data["response"][1]["statistics"]:
                stats_dict_away[item["type"].lower()] = item["value"]
                
            
            # print(stats_dict_home)
            # print(stats_dict_away)
    
            # Insert stats for home team
            insert_fixture_stats(fixture_id, home_team_id, home_team, away_team_id, away_team, stats_dict_home, stats_dict_away, 1)
    
            # Insert stats for away team
            insert_fixture_stats(fixture_id, away_team_id, away_team, home_team_id, home_team, stats_dict_away, stats_dict_home, 0)
            
        else:
            pass
            # print("No fixture stats found for fixture ID:", fixture_id)

        time.sleep(0.5)

def load_fixture_stats(season_year):
    completed_fixtures = get_completed_fixtures(season_year)

    for fixture_id in completed_fixtures:
        fetch_fixture_stats(fixture_id)

load_fixture_stats(2022)

