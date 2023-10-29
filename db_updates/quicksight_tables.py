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
    UPDATE today_fixture AS tf
    JOIN live_updates.live_fixtures AS lf ON tf.fixture_id = lf.fixture_id
    SET tf.referee = lf.referee
    WHERE tf.referee IS NULL
    ;
    ''',
    '''
    UPDATE today_fixture AS tf
    JOIN cleaned_referees AS cr ON tf.referee = cr.original_referee_name
    SET tf.cleaned_referee_name = cr.cleaned_referee_name
    WHERE tf.cleaned_referee_name IS NULL
    ;
    ''',
    '''
    DROP TABLE IF EXISTS quicksight.referee_dashboard;
    ''',
    '''
    CREATE TABLE quicksight.referee_dashboard
    AS
    SELECT
    tf.fixt,
    tf.name AS league,
    tf.match_time,
    tf.fixture_date,
    tf.fixture_id,
    mrv.cleaned_referee_name,
    mrv.total_matches,
    mrv.avg_yc_total,
    mrv.last5_yc,
    mrv.fouls_per_yc,
    mrv.last5_fouls_per_yc,
    mrv.`0_card_matches`,
    mrv.season_avg_yc,
    mrv.season_0_card_matches,
    mrv.league_avg_yc,
    mrv.avg_rc_total,
    mrv.last5_rc,
    mrv.argue_yc_pct,
    mrv.tw_yc_pct,
    mrv.r_0_30_total,
    mrv.r_31_45_total,
    mrv.r_46_75_total,
    mrv.r_76_90_total
    FROM today_fixture tf
    LEFT JOIN master_referee_view mrv on mrv.fixture_id = tf.fixture_id
    WHERE 1 = 1
    # AND tf.cleaned_referee_name IS NOT NULL
    # AND LOWER(mrv.cleaned_referee_name) LIKE '%king%'
    ORDER BY tf.timestamp, tf.league_id;
    ''',
    '''
    DROP TABLE IF EXISTS quicksight.teams_yc_dashboard;
    ;
    ''',
    '''
    CREATE TABLE quicksight.teams_yc_dashboard
    AS
    SELECT
    DISTINCt
    tf.fixt,
    tf.name AS league,
    tf.match_time,
    tf.fixture_date,
    tf.fixture_id,
    mrv.cleaned_referee_name,
    mrv.avg_yc_total,
    mrv.last5_yc,
    mrv.`0_card_matches`,
    mrv.season_avg_yc,
    mrv.season_0_card_matches,
    mrv.last5_rc,
    mrv.last5_fouls_per_yc,
    t.name AS team_name,
    mtv.last5_fouls AS team_l5_fouls,
    mtv.last5_yc AS l5_yc,
    mtv.season_avg_fouls AS team_season_fouls,
    mtv.league_avg_fouls AS team_league_fouls,
    mtv.season_avg_yc AS team_season_yc,
    mtv.league_avg_yc AS team_league_yc,
    mtv.last5_fouls_drawn AS team_l5_fouls_against,
    mtv.last5_yc_against AS l5_yc_against,
    mtv.league_avg_fouls AS team_season_fouls_against,
    mtv.league_avg_against_fouls AS team_league_fouls_against,
    mtv.season_avg_yc_against AS team_season_yc_against,
    mtv.league_avg_yc_against AS team_league_yc_against
    FROM today_fixture tf
    LEFT JOIN master_referee_view mrv on mrv.fixture_id = tf.fixture_id
    LEFT JOIN master_teams_view mtv on tf.fixture_id = mtv.fixture_id
    INNER JOIN teams t on mtv.team_id = t.team_id
    WHERE 1 = 1
    # AND tf.cleaned_referee_name IS NOT NULL
    # AND LOWER(mrv.cleaned_referee_name) LIKE '%king%'
    ORDER BY tf.timestamp, tf.league_id
    ;
    ''',
    '''
    DROP TABLE IF EXISTS quicksight.teams_dashboard;
    ;
    ''',
    '''
    CREATE TABLE quicksight.teams_dashboard
    AS
    SELECT
    DISTINCT
    tf.fixt,
    tf.name AS league,
    tf.match_time,
    tf.fixture_date,
    t.name AS team_name,
    CASE WHEN mtv.team_id = tf.home_team_id THEN 'H' ELSE 'A' END AS home_away,
    mtv.*
    FROM today_fixture tf
    LEFT JOIN master_teams_view mtv on tf.fixture_id = mtv.fixture_id
    INNER JOIN teams t on mtv.team_id = t.team_id
    WHERE 1 = 1
    ORDER BY tf.timestamp, tf.league_id, home_away DESC;
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
