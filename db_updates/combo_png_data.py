import os
import sys
import mysql.connector
import requests

# Add parent dir
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from python_api.get_secrets import db_parameters

def get_db():
    return mysql.connector.connect(
        user=db_parameters["username"],
        password=db_parameters["password"],
        host=db_parameters["host"],
        database="base_data_apis",
    )

def pick_fixtures(cursor):
    cursor.execute("""
        SELECT fixture_id, fixt
        FROM today_fixture
        WHERE fixture_id IN (SELECT fixture_id FROM temp.combo_important_fixtures)
        ORDER BY fixture_id DESC;
    """)
    return cursor.fetchall()

def get_fix_assets(cursor, fixture_id):
    cursor.execute("""
        SELECT fixt, home_team_photo, away_team_photo
        FROM today_fixture
        WHERE fixture_id = %s
        LIMIT 1;
    """, (fixture_id,))
    return cursor.fetchone() or {}

def get_top_yellow(cursor, fixture_id):
    cursor.execute("""
        SELECT
            player_name AS name,
            team_name,
            SUBSTRING(last5_start_yc, 1, LENGTH(last5_start_yc) - 1) AS last5,
            season_league_cards,
            ROUND(avg_fouls_total,1) AS avg_fouls,
            player_id
        FROM temp.player_q
        WHERE fixture_id = %s
        ORDER BY rnk
        LIMIT 1;
    """, (fixture_id,))
    return cursor.fetchone()
