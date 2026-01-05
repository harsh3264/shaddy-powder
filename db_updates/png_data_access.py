# data_access.py
import os
import mysql.connector

# Secrets come from your existing module
from python_api.get_secrets import db_parameters

def get_db():
    cfg = {
        "user": db_parameters["username"],
        "password": db_parameters["password"],
        "host": db_parameters["host"],
        "database": "base_data_apis",
    }
    return mysql.connector.connect(**cfg)

def pick_fixture(cursor):
    """
    Pick one fixture automatically from today's fixtures (any league).
    Prefers fixtures with both teams and league logos available.
    """
    cursor.execute(
        """
        SELECT fixture_id, fixt
        FROM today_fixture
        WHERE 1 = 1
        AND fixture_id = 1501838
        # AND fixture_id IN (SELECT fixture_id FROM temp.new_tele_fixtures)
        GROUP BY 1, 2
        ORDER BY fixture_id DESC
        ;
        """
    )
    return cursor.fetchall()


def get_ref_info(cursor, fixture_id):
    cursor.execute(
        """
        SELECT cleaned_referee_name, avg_yc_total, last5_yc
        FROM temp.referee_q
        WHERE fixture_id = %s
        LIMIT 1;
        """,
        (fixture_id,),
    )
    return cursor.fetchone() or {}

def get_fix_assets(cursor, fixture_id):
    cursor.execute(
        """
        SELECT fixt, home_team_photo, away_team_photo, league_photo
        FROM today_fixture
        WHERE fixture_id = %s
        LIMIT 1;
        """,
        (fixture_id,),
    )
    return cursor.fetchone() or {}

def get_top_foulers(cursor, fixture_id, limit=5):
    cursor.execute(
        f"""
        SELECT
            player_name  AS name,
            player_pos   AS pos,
            team_name    AS team_name,
            last5_start_foul AS metric,
            player_id,
            rnk
        FROM temp.raw_ffh
        WHERE fixture_id = %s
        ORDER BY rnk
        LIMIT {int(limit)};
        """,
        (fixture_id,),
    )
    return cursor.fetchall() or []

def get_top_foul_drawers(cursor, fixture_id, limit=5):
    cursor.execute(
        f"""
        SELECT
            player_name  AS name,
            position     AS pos,
            team_name    AS team_name,
            last5_start_fouls_drawn AS metric,
            player_id,
            rnk
        FROM temp.raw_fld
        WHERE fixture_id = %s
        ORDER BY rnk
        LIMIT {int(limit)};
        """,
        (fixture_id,),
    )
    return cursor.fetchall() or []


def get_top_shooters(cursor, fixture_id, limit=5):
    cursor.execute(
        f"""
        SELECT
            player_name       AS name,
            position          AS pos,
            team_name         AS team_name,
            last5_shots_total AS metric,
            player_id,
            rnk
        FROM temp.raw_sfh
        WHERE fixture_id = %s
        ORDER BY rnk
        LIMIT {int(limit)};
        """,
        (fixture_id,),
    )
    return cursor.fetchall() or []

def get_top_yellows(cursor, fixture_id, limit=3):
    # includes extra fields season_league_cards + avg_fouls_total
    cursor.execute(
        f"""
        SELECT
            player_name            AS name,
            team_name              AS team_name,
            SUBSTRING(last5_start_yc, 1, LENGTH(last5_start_yc) - 1)         AS metric,
            season_league_cards    AS season_league_cards,
            ROUND(avg_fouls_total, 1)        AS avg_fouls_total,
            ROUND(argue_yc_pct, 1)        AS argument_related_yc,
            ROUND(tw_yc_pct, 1)        AS time_wasting_related_yc,
            a.player_id,
            b.position AS pos,
            rnk
        FROM temp.player_q a
        LEFT JOIN (SELECT player_id, position FROM temp.raw_sfh) b 
        ON a.player_id = b.player_id
        WHERE fixture_id = %s
        ORDER BY rnk
        LIMIT {int(limit)};
        """,
        (fixture_id,),
    )
    return cursor.fetchall() or []
