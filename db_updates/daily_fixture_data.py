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
    AND fixture_date = CURDATE()
    GROUP BY 1
    ORDER BY f.timestamp
    ;
    ''',
    '''
    DROP TABLE IF EXISTS refree_base_data;
    ;
    ''',
    '''
    CREATE TABLE refree_base_data AS
    SELECT
        cr.cleaned_referee_name,
        tf.fixture_id,
        tf.fixt,
        tf.season_year AS tf_season,
        tf.match_time,
        tf.name AS tf_league,
        fpsc.league_name,
        fpsc.season_year,
        COUNT(DISTINCT fpsc.fixture_id) AS matches,
        SUM(fouls_committed) AS fouls,
        SUM(CASE WHEN card_minute < 31 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '00-30',
        SUM(CASE WHEN card_minute BETWEEN 31 AND 45 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '31-45',
        SUM(CASE WHEN card_minute BETWEEN 46 AND 75 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '46-75',
        SUM(CASE WHEN card_minute BETWEEN 76 AND 90 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '76-90',
        IFNULL(SUM(cards_yellow + cards_red), 0) AS 'TOTAL',
        SUM(CASE WHEN lower(card_reason) like '%foul%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'foul_yc',
        SUM(CASE WHEN lower(card_reason) like '%argument%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'argue_yc',
        SUM(CASE WHEN lower(card_reason) like '%wasting%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'tw_yc',
        SUM(CASE WHEN lower(card_reason) like '%handball%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'hand_yc'
    FROM analytics.fixture_player_stats_compile fpsc
    LEFT JOIN cleaned_referees cr
    ON fpsc.referee = cr.original_referee_name
    INNER JOIN today_fixture tf on cr.cleaned_referee_name = tf.cleaned_referee_name
    WHERE 1 = 1
    AND league_name IS NOT NULL
    # AND tf.timestamp > UNIX_TIMESTAMP(NOW() - INTERVAL 60 MINUTE)
    # AND season_year > 2021
    # AND cr.cleaned_referee_name IN (SELECT cleaned_referee_name FROM TODAY_FIXTURE)
    GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
    HAVING matches > 1
    AND TOTAL > 1
    ;
    ''',
    '''
    DROP TABLE IF EXISTS refree_data_agg
    ;
    ''',
    '''
    CREATE TABLE refree_data_agg AS
    SELECT
    fixture_id,
    cleaned_referee_name,
    IFNULL(SUM(CASE WHEN fouls > 0 THEN fouls END) / (SUM(CASE WHEN fouls > 0 THEN TOTAL END) - SUM(CASE WHEN fouls > 0 THEN argue_yc END) - SUM(CASE WHEN fouls > 0 THEN tw_yc END)), 0) AS yc_per_foul,
    IFNULL(SUM(argue_yc) / SUM(TOTAL), 0) AS argue_yc_pct,
    IFNULL(SUM(tw_yc) / SUM(matches), 0) AS tw_yc_pct,
    IFNULL(SUM(TOTAL) / SUM(matches), 0) AS avg_yc_total,
    IFNULL(SUM(CASE WHEN season_year = tf_season THEN TOTAL END) / SUM(CASE WHEN season_year = YEAR(CURRENT_DATE()) THEN matches END), 0) AS season_avg_yc,
    IFNULL(SUM(CASE WHEN league_name = tf_league THEN TOTAL END) / SUM(CASE WHEN league_name = tf_league THEN matches END), 0) AS league_avg_yc
    FROM refree_base_data
    WHERE 1 = 1
    # AND cleaned_referee_name = 'J. Iglesias'
    GROUP BY 1, 2
    ;
    ''',
    '''
    DROP TABLE IF EXISTS teams_base_data
    ;
    ''',
    '''
    CREATE TABLE teams_base_data AS
    SELECT
        fpsc.team_id,
        fpsc.team_name,
        tf.fixture_id,
        tf.fixt,
        tf.season_year AS tf_season,
        tf.match_time,
        tf.name AS tf_league,
        fpsc.league_name,
        fpsc.season_year,
        COUNT(DISTINCT fpsc.fixture_id) AS matches,
        SUM(fouls_committed) AS fouls,
        SUM(fouls_drawn) AS fouls_drawn,
        SUM(CASE WHEN card_minute < 31 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '00-30',
        SUM(CASE WHEN card_minute BETWEEN 31 AND 45 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '31-45',
        SUM(CASE WHEN card_minute BETWEEN 46 AND 75 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '46-75',
        SUM(CASE WHEN card_minute BETWEEN 76 AND 90 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '76-90',
        IFNULL(SUM(cards_yellow + cards_red), 0) AS 'TOTAL',
        SUM(CASE WHEN lower(card_reason) like '%foul%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'foul_yc',
        SUM(CASE WHEN lower(card_reason) like '%argument%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'argue_yc',
        SUM(CASE WHEN lower(card_reason) like '%wasting%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'tw_yc',
        SUM(CASE WHEN lower(card_reason) like '%handball%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'hand_yc'
    FROM analytics.fixture_player_stats_compile fpsc
    INNER JOIN today_fixture tf on fpsc.team_id = tf.home_team_id
    WHERE 1 = 1
    AND league_name IS NOT NULL
    GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9
    HAVING matches > 1
    AND TOTAL > 1
    ;
    ''',
    '''
    INSERT INTO teams_base_data
    SELECT
        fpsc.team_id,
        fpsc.team_name,
        tf.fixture_id,
        tf.fixt,
        tf.season_year AS tf_season,
        tf.match_time,
        tf.name AS tf_league,
        fpsc.league_name,
        fpsc.season_year,
        COUNT(DISTINCT fpsc.fixture_id) AS matches,
        SUM(fouls_committed) AS fouls,
        SUM(fouls_drawn) AS fouls_drawn,
        SUM(CASE WHEN card_minute < 31 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '00-30',
        SUM(CASE WHEN card_minute BETWEEN 31 AND 45 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '31-45',
        SUM(CASE WHEN card_minute BETWEEN 46 AND 75 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '46-75',
        SUM(CASE WHEN card_minute BETWEEN 76 AND 90 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '76-90',
        IFNULL(SUM(cards_yellow + cards_red), 0) AS 'TOTAL',
        SUM(CASE WHEN lower(card_reason) like '%foul%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'foul_yc',
        SUM(CASE WHEN lower(card_reason) like '%argument%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'argue_yc',
        SUM(CASE WHEN lower(card_reason) like '%wasting%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'tw_yc',
        SUM(CASE WHEN lower(card_reason) like '%handball%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'hand_yc'
    FROM analytics.fixture_player_stats_compile fpsc
    INNER JOIN today_fixture tf on fpsc.team_id = tf.away_team_id
    WHERE 1 = 1
    AND league_name IS NOT NULL
    GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9
    HAVING matches > 1
    AND TOTAL > 1
    ;
    ''',
    '''
    DROP TABLE IF EXISTS team_data_agg
    ;
    ''',
    '''
    CREATE TABLE team_data_agg AS
    SELECT
    fixture_id,
    team_id,
    IFNULL(SUM(TOTAL) / SUM(matches), 0) AS avg_yc_total,
    IFNULL(SUM(CASE WHEN season_year = tf_season THEN TOTAL END) / SUM(CASE WHEN season_year = YEAR(CURRENT_DATE()) THEN matches END), 0) AS season_avg_yc,
    IFNULL(SUM(CASE WHEN league_name = tf_league THEN TOTAL END) / SUM(CASE WHEN league_name = tf_league THEN matches END), 0) AS league_avg_yc,
    IFNULL(SUM(CASE WHEN fouls > 0 AND season_year = tf_season THEN fouls END) / SUM(CASE WHEN fouls > 0 AND season_year = tf_season THEN matches END), 0) AS avg_fouls_season,
    IFNULL(SUM(CASE WHEN fouls_drawn > 0 AND season_year = tf_season THEN fouls_drawn END) / SUM(CASE WHEN fouls_drawn > 0 AND season_year = tf_season THEN matches END), 0) AS avg_fouls_drawn_season
    FROM teams_base_data
    WHERE 1 = 1
    # AND cleaned_referee_name = 'J. Iglesias'
    GROUP BY 1, 2
    ;
    ;
    ''',
    '''
    DROP TABLE IF EXISTS today_fixture_card_view
    ;
    ''',
    '''
    CREATE TABLE today_fixture_card_view AS
    SELECT
    DISTINCT
    tf.fixture_id,
    tf.fixt,
    tf.match_time,
    IFNULL(tf.cleaned_referee_name, tf.referee) AS refree,
    ROUND(rda.avg_yc_total, 2) AS ref_avg_yc,
    ROUND(rda.league_avg_yc, 2) AS ref_league_yc,
    ROUND(rda.season_avg_yc, 2) AS ref_season_yc,
    ROUND(rda.yc_per_foul, 2) AS ref_yc_per_foul,
    ROUND(rda.argue_yc_pct, 2) AS argue_yc_pct,
    ROUND(rda.tw_yc_pct, 2) AS tw_yc_pct,
    tf.home_team,
    ROUND(tda1.avg_yc_total, 2) AS h_yc_total,
    ROUND(tda1.league_avg_yc, 2) AS h_yc_league,
    ROUND(tda1.season_avg_yc, 2) AS h_yc_season,
    ROUND(tda1.avg_fouls_season, 2) AS h_fouls,
    ROUND(tda1.avg_fouls_drawn_season, 2) AS h_fouls_drawn,
    tf.away_team,
    ROUND(tda2.avg_yc_total, 2) AS a_yc_total,
    ROUND(tda2.league_avg_yc, 2) AS a_yc_league,
    ROUND(tda2.season_avg_yc, 2) AS a_yc_season,
    ROUND(tda2.avg_fouls_season, 2) AS a_fouls,
    ROUND(tda2.avg_fouls_drawn_season, 2) AS a_fouls_drawn,
    ROUND(((tda1.avg_fouls_season /  rda.yc_per_foul) + (tda2.avg_fouls_drawn_season / rda.yc_per_foul))/2, 2) AS h_exp_yc,
    ROUND(((tda2.avg_fouls_season /  rda.yc_per_foul) + (tda1.avg_fouls_drawn_season / rda.yc_per_foul))/2, 2) AS a_exp_yc,
    ROUND(((tda1.avg_fouls_season /  rda.yc_per_foul) + (tda2.avg_fouls_drawn_season / rda.yc_per_foul))/2, 2) + ROUND(((tda2.avg_fouls_season /  rda.yc_per_foul) + (tda1.avg_fouls_drawn_season / rda.yc_per_foul))/2, 2) AS total_exp_yc
    FROM today_fixture tf
    LEFT JOIN refree_data_agg rda on tf.fixture_id = rda.fixture_id
    LEFT JOIN team_data_agg tda1 on tf.fixture_id = tda1.fixture_id
    AND tf.home_team_id = tda1.team_id
    LEFT JOIN team_data_agg tda2 on tf.fixture_id = tda2.fixture_id
    AND tf.away_team_id = tda2.team_id
    ;
    ''',
    '''
    DROP TABLE IF EXISTS players_base_data
    ;
    ''',
    '''
    DROP TABLE IF EXISTS player_latest_club
    ;
    ''',
    '''
    CREATE TABLE player_latest_club AS
    SELECT * FROM
    (SELECT player_id, team_name, team_id,
           ROW_NUMBER() over (partition by player_id ORDER BY fixture_date DESC) AS r
    FROM analytics.fixture_player_stats_compile
    WHERE team_name <> nationality
    )A
    WHERE 1 = 1
    AND r = 1;
    ;
    ''',
    '''
    DROP TABLE IF EXISTS player_last_5_data
    ;
    ''',
    '''
    CREATE TABLE player_last_5_data
    AS
    SELECT
    player_id,
    GROUP_CONCAT(IF(is_substitute = 0, IFNULL(fouls_committed, 0), '') ORDER BY fixture_date DESC SEPARATOR '') AS last5_start_foul,
    GROUP_CONCAT(CASE WHEN is_substitute = 1 THEN IFNULL(fouls_committed, 0) END ORDER BY fixture_date DESC SEPARATOR '') AS last5_sub_foul,
    GROUP_CONCAT(CASE WHEN is_substitute = 0 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END ORDER BY fixture_date DESC SEPARATOR '') AS last5_start_yc,
    GROUP_CONCAT(CASE WHEN is_substitute = 1 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END ORDER BY fixture_date DESC SEPARATOR '') AS last5_sub_yc
    FROM analytics.fixture_player_stats_compile
    WHERE 1 = 1
    AND player_rnk_sub <= 5
    GROUP BY 1
    ;
    ''',
    '''
    CREATE TABLE players_base_data AS
    SELECT
        fpsc.player_id,
        fpsc.player_name,
        fpsc.is_substitute,
        tf.fixture_id,
        tf.season_year AS tf_season,
        plc.team_id AS tf_team,
        fpsc.team_id,
        fpsc.season_year,
        COUNT(DISTINCT fpsc.fixture_id) AS matches,
        SUM(fouls_committed) AS fouls,
        SUM(fouls_drawn) AS fouls_drawn,
        COUNT(DISTINCT CASE WHEN fouls_committed IS NOT NULL AND fouls_committed > 0 THEN fpsc.fixture_id END) AS fouled_matches,
        SUM(CASE WHEN card_minute < 31 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '00-30',
        SUM(CASE WHEN card_minute BETWEEN 31 AND 45 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '31-45',
        SUM(CASE WHEN card_minute BETWEEN 46 AND 75 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '46-75',
        SUM(CASE WHEN card_minute BETWEEN 76 AND 90 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '76-90',
        IFNULL(SUM(cards_yellow + cards_red), 0) AS 'TOTAL',
        SUM(CASE WHEN lower(card_reason) like '%foul%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'foul_yc',
        SUM(CASE WHEN lower(card_reason) like '%argument%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'argue_yc',
        SUM(CASE WHEN lower(card_reason) like '%wasting%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'tw_yc',
        SUM(CASE WHEN lower(card_reason) like '%handball%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'hand_yc'
    FROM analytics.fixture_player_stats_compile fpsc
    LEFT JOIN player_latest_club plc
    ON fpsc.player_id = plc.player_id
    INNER JOIN today_fixture tf on plc.team_id = tf.home_team_id
    WHERE 1 = 1
    AND league_name IS NOT NULL
    AND fpsc.player_id <> 0
    GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
    HAVING matches > 1
    ;
    ''',
    '''
    INSERT INTO players_base_data
    SELECT
        fpsc.player_id,
        fpsc.player_name,
        fpsc.is_substitute,
        tf.fixture_id,
        tf.season_year AS tf_season,
        plc.team_id AS tf_team,
        fpsc.team_id,
        fpsc.season_year,
        COUNT(DISTINCT fpsc.fixture_id) AS matches,
        SUM(fouls_committed) AS fouls,
        SUM(fouls_drawn) AS fouls_drawn,
        COUNT(DISTINCT CASE WHEN fouls_committed IS NOT NULL AND fouls_committed > 0 THEN fpsc.fixture_id END) AS fouled_matches,
        SUM(CASE WHEN card_minute < 31 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '00-30',
        SUM(CASE WHEN card_minute BETWEEN 31 AND 45 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '31-45',
        SUM(CASE WHEN card_minute BETWEEN 46 AND 75 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '46-75',
        SUM(CASE WHEN card_minute BETWEEN 76 AND 90 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '76-90',
        IFNULL(SUM(cards_yellow + cards_red), 0) AS 'TOTAL',
        SUM(CASE WHEN lower(card_reason) like '%foul%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'foul_yc',
        SUM(CASE WHEN lower(card_reason) like '%argument%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'argue_yc',
        SUM(CASE WHEN lower(card_reason) like '%wasting%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'tw_yc',
        SUM(CASE WHEN lower(card_reason) like '%handball%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'hand_yc'
    FROM analytics.fixture_player_stats_compile fpsc
    LEFT JOIN player_latest_club plc
    ON fpsc.player_id = plc.player_id
    INNER JOIN today_fixture tf on plc.team_id = tf.away_team_id
    WHERE 1 = 1
    AND league_name IS NOT NULL
    AND fpsc.player_id <> 0
    GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
    HAVING matches > 1
    ;
    ''',
    '''
    DROP TABLE IF EXISTS player_data_agg
    ;
    ''',
    '''
    CREATE TABLE player_data_agg AS
    SELECT
    fixture_id,
    pbd.player_id,
    tf_team AS team_id,
    player_name,
    last5_start_foul,
    last5_sub_foul,
    last5_start_yc,
    last5_sub_yc,
    SUM(matches) AS total_matches,
    IFNULL(SUM(CASE WHEN is_substitute = 0 THEN fouled_matches END) / SUM(CASE WHEN is_substitute = 0 THEN matches END), 0) AS foul_match_pct,
    IFNULL(SUM(CASE WHEN is_substitute = 1 THEN fouled_matches END) / SUM(CASE WHEN is_substitute = 1 THEN matches END), 0) AS foul_match_sub,
    IFNULL(SUM(CASE WHEN is_substitute = 0 THEN fouls END) / SUM(CASE WHEN is_substitute = 0 THEN matches END), 0) AS avg_fouls_total,
    IFNULL(SUM(CASE WHEN is_substitute = 0 THEN TOTAL END) / SUM(CASE WHEN is_substitute = 0 THEN matches END), 0) AS avg_yc_total,
    SUM(CASE WHEN season_year = tf_season THEN matches END) AS season_matches,
    IFNULL(SUM(CASE WHEN fouls > 0 AND is_substitute = 0 AND season_year = tf_season THEN fouled_matches END) / SUM(CASE WHEN fouls_drawn > 0 AND is_substitute = 0 AND season_year = tf_season THEN matches END), 0) AS season_foul_match_pct,
    IFNULL(SUM(CASE WHEN fouls > 0 AND is_substitute = 0 AND season_year = tf_season THEN fouls END) / SUM(CASE WHEN fouls > 0 AND is_substitute = 0 AND season_year = tf_season THEN matches END), 0) AS season_avg_fouls,
    IFNULL(SUM(CASE WHEN season_year = tf_season AND is_substitute = 0 THEN TOTAL END) / SUM(CASE WHEN season_year = YEAR(CURRENT_DATE()) AND is_substitute = 0 THEN matches END), 0) AS season_avg_yc,
    IFNULL(SUM(CASE WHEN team_id = tf_team THEN TOTAL END) / SUM(CASE WHEN team_id = tf_team THEN matches END), 0) AS team_avg_yc
    FROM players_base_data pbd
    INNER JOIN player_last_5_data pl5d
    ON pbd.player_id = pl5d.player_id
    WHERE 1 = 1
    GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
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
