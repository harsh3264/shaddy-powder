import sys
import os
import mysql.connector
import requests

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import the necessary modules
from python_api.get_secrets import rapid_api_key, db_parameters
from python_api.rapid_apis import STANDINGS_URL

# MySQL database configuration
db_config = {
    'user': db_parameters['username'],
    'password': db_parameters['password'],
    'host': db_parameters['host'],
    'database': 'base_data_apis'
}

def insert_league_standings(cur, league_id, season_year, team_id, rank_t, points, goals_diff, group_name, form,
                            status_t, description_t, played, win, draw, lose, goals_for, goals_against, home_played,
                            home_win, home_draw, home_lose, home_goals_for, home_goals_against, away_played,
                            away_win, away_draw, away_lose, away_goals_for, away_goals_against, last_update):
    sql = """
        INSERT INTO league_standings (league_id, season_year, team_id, rank_t, points, goals_diff, group_name, form,
                                      status_t, description_t, played, win, draw, lose, goals_for, goals_against,
                                      home_played, home_win, home_draw, home_lose, home_goals_for,
                                      home_goals_against, away_played, away_win, away_draw, away_lose,
                                      away_goals_for, away_goals_against, last_update)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE rank_t=VALUES(rank_t), points=VALUES(points), goals_diff=VALUES(goals_diff),
                                group_name=VALUES(group_name), form=VALUES(form), status_t=VALUES(status_t),
                                description_t=VALUES(description_t), played=VALUES(played), win=VALUES(win),
                                draw=VALUES(draw), lose=VALUES(lose), goals_for=VALUES(goals_for),
                                goals_against=VALUES(goals_against), home_played=VALUES(home_played),
                                home_win=VALUES(home_win), home_draw=VALUES(home_draw), home_lose=VALUES(home_lose),
                                home_goals_for=VALUES(home_goals_for), home_goals_against=VALUES(home_goals_against),
                                away_played=VALUES(away_played), away_win=VALUES(away_win), away_draw=VALUES(away_draw),
                                away_lose=VALUES(away_lose), away_goals_for=VALUES(away_goals_for),
                                away_goals_against=VALUES(away_goals_against), last_update=VALUES(last_update)
    """
    cur.execute(sql, (league_id, season_year, team_id, rank_t, points, goals_diff, group_name, form, status_t,
                      description_t, played, win, draw, lose, goals_for, goals_against, home_played, home_win,
                      home_draw, home_lose, home_goals_for, home_goals_against, away_played, away_win, away_draw,
                      away_lose, away_goals_for, away_goals_against, last_update))

def load_league_standings(query):
    # Connect to MySQL database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Execute the query to fetch league IDs and season years
    cursor.execute(query)
    leagues = cursor.fetchall()
    
    # print(leagues)

    # Iterate over league IDs and season years
    for league_id, season_year in leagues:
        # Fetch league standings data
        params = {"league": str(league_id), "season": str(season_year)}
        
        # print(params)
        response = requests.get(STANDINGS_URL, headers={"X-RapidAPI-Key": rapid_api_key}, params=params)
        standings_data = response.json()

        # Fetch league standings data
        standings_data = response.json()
        
        # Check if the response contains data
        if 'response' in standings_data and standings_data['response']:
            standings_list = standings_data['response'][0]['league']['standings']
        
            # Iterate through each standings entry
            for standings in standings_list:
                # Process the standings data
        
                # Iterate over teams in the standings
                for team in standings:
                    team_id = team['team']['id']
                    rank_t = team['rank']
                    points = team['points']
                    goals_diff = team['goalsDiff']
                    group_name = team['group']
                    form = team['form']
                    status_t = team['status']
                    description_t = team['description']
                    played = team['all']['played']
                    win = team['all']['win']
                    draw = team['all']['draw']
                    lose = team['all']['lose']
                    goals_for = team['all']['goals']['for']
                    goals_against = team['all']['goals']['against']
                    home_played = team['home']['played']
                    home_win = team['home']['win']
                    home_draw = team['home']['draw']
                    home_lose = team['home']['lose']
                    home_goals_for = team['home']['goals']['for']
                    home_goals_against = team['home']['goals']['against']
                    away_played = team['away']['played']
                    away_win = team['away']['win']
                    away_draw = team['away']['draw']
                    away_lose = team['away']['lose']
                    away_goals_for = team['away']['goals']['for']
                    away_goals_against = team['away']['goals']['against']
                    last_update = team['update']
        
                    # Insert or update league standings info
                    insert_league_standings(cursor, league_id, season_year, team_id, rank_t, points, goals_diff, group_name, form,
                                            status_t, description_t, played, win, draw, lose, goals_for, goals_against,
                                            home_played, home_win, home_draw, home_lose, home_goals_for, home_goals_against,
                                            away_played, away_win, away_draw, away_lose, away_goals_for, away_goals_against,
                                            last_update)
                                    
        else:
            # No standings data available
            print("No standings data for this entry")
        
        # print(standings)


    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()
