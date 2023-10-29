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
    DROP TABLE IF EXISTS players_latest_club
    ;
    ''',
    '''
    CREATE TABLE players_latest_club AS
    SELECT * FROM
    (SELECT player_id, team_name, team_id, season_year,
           ROW_NUMBER() over (partition by player_id ORDER BY fixture_date DESC) AS r
    FROM analytics.fixture_player_stats_compile
    WHERE team_name <> nationality
    )A
    WHERE 1 = 1
    AND r = 1
    AND season_year > YEAR(current_date) - 2
    ;
    ''',
    '''
    DROP TABLE IF EXISTS players_last_5_data
    ;
    ''',
    '''
    CREATE TABLE players_last_5_data AS
    SELECT
        player_id,
        GROUP_CONCAT(CASE WHEN is_substitute = 0 AND player_rnk_sub <= 5 THEN IFNULL(goals, 0) END ORDER BY fixture_date DESC SEPARATOR '') AS last5_start_goal,
        GROUP_CONCAT(CASE WHEN is_substitute = 0 AND player_rnk_sub <= 5 THEN IFNULL(fouls_committed, 0) END ORDER BY fixture_date DESC SEPARATOR '') AS last5_start_foul,
        GROUP_CONCAT(CASE WHEN is_substitute = 1 AND player_rnk_sub <= 5 THEN IFNULL(fouls_committed, 0) END ORDER BY fixture_date DESC SEPARATOR '') AS last5_sub_foul,
        REPLACE(
            SUBSTRING_INDEX(
                GROUP_CONCAT(
                    CASE WHEN is_substitute = 1 AND LEFT(result, 1) = 'W' THEN IFNULL(fouls_committed, 0) END ORDER BY fixture_date DESC
                ),
                ',', 5
            ),
            ',',
            ''
        ) AS last5_win_sub_foul,
        REPLACE(
            SUBSTRING_INDEX(
                GROUP_CONCAT(
                    CASE WHEN is_substitute = 1 AND LEFT(result, 1) = 'L' THEN IFNULL(fouls_committed, 0) END ORDER BY fixture_date DESC
                ),
                ',', 5
            ),
            ',',
            ''
        ) AS last5_loss_sub_foul,
        REPLACE(
            SUBSTRING_INDEX(
                GROUP_CONCAT(
                    CASE WHEN is_substitute = 1 AND LEFT(result, 1) = 'D' THEN IFNULL(fouls_committed, 0) END ORDER BY fixture_date DESC
                ),
                ',', 5
            ),
            ',',
            ''
        ) AS last5_draw_sub_foul,
        GROUP_CONCAT(CASE WHEN is_substitute = 0 AND player_rnk_sub <= 5 THEN IFNULL(minutes_played, 0) END ORDER BY fixture_date DESC SEPARATOR '|') AS last5_start_mins,
        GROUP_CONCAT(CASE WHEN is_substitute = 1 AND player_rnk_sub <= 5 THEN IFNULL(minutes_played, 0) END ORDER BY fixture_date DESC SEPARATOR '|') AS last5_sub_mins,
        GROUP_CONCAT(CASE WHEN is_substitute = 0 AND player_rnk_sub <= 5 THEN IFNULL(LEFT(result,1), 0) END ORDER BY fixture_date DESC SEPARATOR '|') AS last5_start_result,
        GROUP_CONCAT(CASE WHEN is_substitute = 1 AND player_rnk_sub <= 5 THEN IFNULL(LEFT(result,1), 0) END ORDER BY fixture_date DESC SEPARATOR '|') AS last5_sub_result,
        GROUP_CONCAT(CASE WHEN is_substitute = 0 AND player_rnk_sub <= 5 THEN IFNULL(fouls_drawn, 0) END ORDER BY fixture_date DESC SEPARATOR '') AS last5_fouls_drawn,
        GROUP_CONCAT(CASE WHEN is_substitute = 0 AND player_rnk_sub <= 5 THEN IFNULL(shots_total, 0) END ORDER BY fixture_date DESC SEPARATOR '') AS last5_shots_total,
        GROUP_CONCAT(CASE WHEN is_substitute = 0 AND player_rnk_sub <= 5 THEN IFNULL(shots_on_target, 0) END ORDER BY fixture_date DESC SEPARATOR '') AS last5_sot_total,
        GROUP_CONCAT(CASE WHEN is_substitute = 0 AND player_rnk_sub <= 5 THEN IFNULL(offsides, 0) END ORDER BY fixture_date DESC SEPARATOR '') AS last5_offsides,
        GROUP_CONCAT(CASE WHEN is_substitute = 0 AND player_rnk_sub <= 5 THEN IFNULL(tackles_total, 0) END ORDER BY fixture_date DESC SEPARATOR '') AS last5_tackles_total,
        GROUP_CONCAT(CASE WHEN is_substitute = 0 AND player_rnk_sub <= 5 THEN
            CASE
                WHEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) > 1 THEN '1'
                ELSE CAST(IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) AS CHAR)
            END
        END ORDER BY fixture_date DESC SEPARATOR '') AS last5_start_yc,
        GROUP_CONCAT(CASE WHEN is_substitute = 1 AND player_rnk_sub <= 5 THEN
            CASE
                WHEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) > 1 THEN '1'
                ELSE CAST(IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) AS CHAR)
            END
        END ORDER BY fixture_date DESC SEPARATOR '') AS last5_sub_yc
    FROM analytics.fixture_player_stats_compile
    WHERE 1 = 1
        AND player_rnk_sub <= 100
    GROUP BY player_id
    ;
    ''',
    '''
    DROP TABLE IF EXISTS players_base_data
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
        SUM(IFNULL(goals,0)) AS goals,
        COUNT(DISTINCT CASE WHEN IFNULL(goals,0) > 0 THEN fpsc.fixture_id END) AS goal_matches,
        SUM(IFNULL(shots_total,0)) AS shots,
        COUNT(DISTINCT CASE WHEN IFNULL(shots_total,0) > 0 THEN fpsc.fixture_id END) AS shot_matches,
        SUM(IFNULL(shots_on_target,0)) AS sot,
        COUNT(DISTINCT CASE WHEN IFNULL(shots_on_target,0) > 0 THEN fpsc.fixture_id END) AS sot_matches,
        SUM(IFNULL(offsides,0)) AS offsides,
        COUNT(DISTINCT CASE WHEN IFNULL(offsides,0) > 0 THEN fpsc.fixture_id END) AS offside_matches,
        SUM(IFNULL(tackles_total,0)) AS tackles,
        COUNT(DISTINCT CASE WHEN IFNULL(tackles_total,0) > 0 THEN fpsc.fixture_id END) AS tackled_matches,
        SUM(IFNULL(fouls_committed,0)) AS fouls,
        COUNT(DISTINCT CASE WHEN IFNULL(fouls_committed,0) > 0 THEN fpsc.fixture_id END) AS fouled_matches,
        SUM(IFNULL(fouls_drawn,0)) AS fouls_drawn,
        SUM(CASE WHEN card_minute < 31 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '00-30',
        SUM(CASE WHEN card_minute BETWEEN 31 AND 45 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '31-45',
        SUM(CASE WHEN card_minute BETWEEN 46 AND 75 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '46-75',
        SUM(CASE WHEN card_minute BETWEEN 76 AND 90 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '76-90',
        COUNT(DISTINCT CASE WHEN IFNULL(cards_yellow,0) + IFNULL(cards_red,0) > 0 THEN fpsc.fixture_id END) AS card,
        SUM(CASE WHEN lower(card_reason) like '%foul%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS foul_yc,
        SUM(CASE WHEN lower(card_reason) like '%argument%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS argue_yc,
        SUM(CASE WHEN lower(card_reason) like '%wasting%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS tw_yc,
        SUM(CASE WHEN lower(card_reason) like '%handball%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS hand_yc
    FROM analytics.fixture_player_stats_compile fpsc
    LEFT JOIN players_latest_club plc
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
        SUM(IFNULL(goals,0)) AS goals,
        COUNT(DISTINCT CASE WHEN IFNULL(goals,0) > 0 THEN fpsc.fixture_id END) AS goal_matches,
        SUM(IFNULL(shots_total,0)) AS shots,
        COUNT(DISTINCT CASE WHEN IFNULL(shots_total,0) > 0 THEN fpsc.fixture_id END) AS shot_matches,
        SUM(IFNULL(shots_on_target,0)) AS sot,
        COUNT(DISTINCT CASE WHEN IFNULL(shots_on_target,0) > 0 THEN fpsc.fixture_id END) AS sot_matches,
        SUM(IFNULL(offsides,0)) AS offsides,
        COUNT(DISTINCT CASE WHEN IFNULL(offsides,0) > 0 THEN fpsc.fixture_id END) AS offside_matches,
        SUM(IFNULL(tackles_total,0)) AS tackles,
        COUNT(DISTINCT CASE WHEN IFNULL(tackles_total,0) > 0 THEN fpsc.fixture_id END) AS tackled_matches,
        SUM(IFNULL(fouls_committed,0)) AS fouls,
        COUNT(DISTINCT CASE WHEN IFNULL(fouls_committed,0) > 0 THEN fpsc.fixture_id END) AS fouled_matches,
        SUM(IFNULL(fouls_drawn,0)) AS fouls_drawn,
        SUM(CASE WHEN card_minute < 31 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '00-30',
        SUM(CASE WHEN card_minute BETWEEN 31 AND 45 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '31-45',
        SUM(CASE WHEN card_minute BETWEEN 46 AND 75 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '46-75',
        SUM(CASE WHEN card_minute BETWEEN 76 AND 90 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '76-90',
        COUNT(DISTINCT CASE WHEN IFNULL(cards_yellow,0) + IFNULL(cards_red,0) > 0 THEN fpsc.fixture_id END) AS card,
        SUM(CASE WHEN lower(card_reason) like '%foul%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS foul_yc,
        SUM(CASE WHEN lower(card_reason) like '%argument%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS argue_yc,
        SUM(CASE WHEN lower(card_reason) like '%wasting%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS tw_yc,
        SUM(CASE WHEN lower(card_reason) like '%handball%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS hand_yc
    FROM analytics.fixture_player_stats_compile fpsc
    LEFT JOIN players_latest_club plc
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
    INSERT INTO players_base_data
    SELECT
        fpsc.player_id,
        fpsc.player_name,
        fpsc.is_substitute,
        0 AS fixture_id,
        max_season AS tf_season,
        plc.team_id AS tf_team,
        fpsc.team_id,
        fpsc.season_year,
        COUNT(DISTINCT fpsc.fixture_id) AS matches,
        SUM(IFNULL(goals,0)) AS goals,
        COUNT(DISTINCT CASE WHEN IFNULL(goals,0) > 0 THEN fpsc.fixture_id END) AS goal_matches,
        SUM(IFNULL(shots_total,0)) AS shots,
        COUNT(DISTINCT CASE WHEN IFNULL(shots_total,0) > 0 THEN fpsc.fixture_id END) AS shot_matches,
        SUM(IFNULL(shots_on_target,0)) AS sot,
        COUNT(DISTINCT CASE WHEN IFNULL(shots_on_target,0) > 0 THEN fpsc.fixture_id END) AS sot_matches,
        SUM(IFNULL(offsides,0)) AS offsides,
        COUNT(DISTINCT CASE WHEN IFNULL(offsides,0) > 0 THEN fpsc.fixture_id END) AS offside_matches,
        SUM(IFNULL(tackles_total,0)) AS tackles,
        COUNT(DISTINCT CASE WHEN IFNULL(tackles_total,0) > 0 THEN fpsc.fixture_id END) AS tackled_matches,
        SUM(IFNULL(fouls_committed,0)) AS fouls,
        COUNT(DISTINCT CASE WHEN IFNULL(fouls_committed,0) > 0 THEN fpsc.fixture_id END) AS fouled_matches,
        SUM(IFNULL(fouls_drawn,0)) AS fouls_drawn,
        SUM(CASE WHEN card_minute < 31 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '00-30',
        SUM(CASE WHEN card_minute BETWEEN 31 AND 45 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '31-45',
        SUM(CASE WHEN card_minute BETWEEN 46 AND 75 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '46-75',
        SUM(CASE WHEN card_minute BETWEEN 76 AND 90 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '76-90',
        COUNT(DISTINCT CASE WHEN IFNULL(cards_yellow,0) + IFNULL(cards_red,0) > 0 THEN fpsc.fixture_id END) AS card,
        SUM(CASE WHEN lower(card_reason) like '%foul%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS foul_yc,
        SUM(CASE WHEN lower(card_reason) like '%argument%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS argue_yc,
        SUM(CASE WHEN lower(card_reason) like '%wasting%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS tw_yc,
        SUM(CASE WHEN lower(card_reason) like '%handball%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS hand_yc
    FROM analytics.fixture_player_stats_compile fpsc
    INNER JOIN (SELECT player_id, MAX(season_year) AS max_season FROM analytics.fixture_player_stats_compile GROUP BY 1) As max
    ON fpsc.player_id = max.player_id
    LEFT JOIN players_latest_club plc
    ON fpsc.player_id = plc.player_id
    WHERE 1 = 1
    AND league_name IS NOT NULL
    AND fpsc.player_id <> 0
    AND fpsc.player_id NOT IN (SELECT player_id FROM players_base_data)
    GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
    HAVING matches > 1
    ;
    ''',
    '''
    DROP TABLE IF EXISTS players_data_agg
    ;
    ''',
    '''
    CREATE TABLE players_data_agg AS
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
    SUM(CASE WHEN season_year = tf_season THEN matches END) AS season_matches,
    
    -- Foul and YC metrics
    IFNULL(SUM(CASE WHEN is_substitute = 0 THEN fouled_matches END) / SUM(CASE WHEN is_substitute = 0 THEN matches END), 0) AS foul_match_pct,
    IFNULL(SUM(CASE WHEN is_substitute = 0 THEN fouls END) / SUM(CASE WHEN is_substitute = 0 THEN matches END), 0) AS avg_fouls_total,
    IFNULL(SUM(CASE WHEN is_substitute = 0 THEN card END) / SUM(CASE WHEN is_substitute = 0 THEN matches END), 0) AS avg_yc_total,
    IFNULL(SUM(CASE WHEN fouls > 0 AND is_substitute = 0 AND season_year = tf_season THEN fouled_matches END) / SUM(CASE WHEN is_substitute = 0 AND season_year = tf_season THEN matches END), 0) AS season_foul_match_pct,
    IFNULL(SUM(CASE WHEN fouls > 0 AND is_substitute = 0 AND season_year = tf_season THEN fouls END) / SUM(CASE WHEN is_substitute = 0 AND season_year = tf_season THEN matches END), 0) AS season_avg_fouls,
    IFNULL(SUM(CASE WHEN season_year = tf_season AND is_substitute = 0 THEN card END) / SUM(CASE WHEN season_year = tf_season AND is_substitute = 0 THEN matches END), 0) AS season_avg_yc,
    
    -- Shot, SOT, Goal metrics
    IFNULL(SUM(CASE WHEN is_substitute = 0 THEN shot_matches END) / SUM(CASE WHEN is_substitute = 0 THEN matches END), 0) AS shot_match_pct,
    IFNULL(SUM(CASE WHEN is_substitute = 0 THEN shots END) / SUM(CASE WHEN is_substitute = 0 THEN matches END), 0) AS avg_shots_total,
    IFNULL(SUM(CASE WHEN is_substitute = 0 THEN sot_matches END) / SUM(CASE WHEN is_substitute = 0 THEN matches END), 0) AS sot_match_pct,
    IFNULL(SUM(CASE WHEN is_substitute = 0 THEN sot END) / SUM(CASE WHEN is_substitute = 0 THEN matches END), 0) AS avg_sot_total,
    IFNULL(SUM(CASE WHEN is_substitute = 0 THEN goal_matches END) / SUM(CASE WHEN is_substitute = 0 THEN matches END), 0) AS goal_match_pct,
    IFNULL(SUM(CASE WHEN is_substitute = 0 THEN goals END) / SUM(CASE WHEN is_substitute = 0 THEN matches END), 0) AS avg_goals_total,
    IFNULL(SUM(CASE WHEN shots > 0 AND is_substitute = 0 AND season_year = tf_season THEN shot_matches END) / SUM(CASE WHEN is_substitute = 0 AND season_year = tf_season THEN matches END), 0) AS season_shot_match_pct,
    IFNULL(SUM(CASE WHEN shots > 0 AND is_substitute = 0 AND season_year = tf_season THEN shots END) / SUM(CASE WHEN is_substitute = 0 AND season_year = tf_season THEN matches END), 0) AS season_avg_shots,
    IFNULL(SUM(CASE WHEN sot > 0 AND is_substitute = 0 AND season_year = tf_season THEN sot_matches END) / SUM(CASE WHEN is_substitute = 0 AND season_year = tf_season THEN matches END), 0) AS season_sot_match_pct,
    IFNULL(SUM(CASE WHEN sot > 0 AND is_substitute = 0 AND season_year = tf_season THEN sot END) / SUM(CASE WHEN is_substitute = 0 AND season_year = tf_season THEN matches END), 0) AS season_avg_sot,
    IFNULL(SUM(CASE WHEN goals > 0 AND is_substitute = 0 AND season_year = tf_season THEN goal_matches END) / SUM(CASE WHEN is_substitute = 0 AND season_year = tf_season THEN matches END), 0) AS season_goal_match_pct,
    IFNULL(SUM(CASE WHEN goals > 0 AND is_substitute = 0 AND season_year = tf_season THEN goals END) / SUM(CASE WHEN is_substitute = 0 AND season_year = tf_season THEN matches END), 0) AS season_avg_goals,
    
    -- Offside metrics
    IFNULL(SUM(CASE WHEN is_substitute = 0 THEN offside_matches END) / SUM(CASE WHEN is_substitute = 0 THEN matches END), 0) AS offside_match_pct,
    IFNULL(SUM(CASE WHEN is_substitute = 0 THEN offsides END) / SUM(CASE WHEN is_substitute = 0 THEN matches END), 0) AS avg_offsides_total,
    IFNULL(SUM(CASE WHEN offsides > 0 AND is_substitute = 0 AND season_year = tf_season THEN offside_matches END) / SUM(CASE WHEN is_substitute = 0 AND season_year = tf_season THEN matches END), 0) AS season_offside_match_pct,
    IFNULL(SUM(CASE WHEN offsides > 0 AND is_substitute = 0 AND season_year = tf_season THEN offsides END) / SUM(CASE WHEN is_substitute = 0 AND season_year = tf_season THEN matches END), 0) AS season_avg_offsides,
    
    -- Tackle metrics
    IFNULL(SUM(CASE WHEN is_substitute = 0 THEN tackled_matches END) / SUM(CASE WHEN is_substitute = 0 THEN matches END), 0) AS tackle_match_pct,
    IFNULL(SUM(CASE WHEN is_substitute = 0 THEN tackles END) / SUM(CASE WHEN is_substitute = 0 THEN matches END), 0) AS avg_tackles_total,
    IFNULL(SUM(CASE WHEN tackles > 0 AND is_substitute = 0 AND season_year = tf_season THEN tackled_matches END) / SUM(CASE WHEN is_substitute = 0 AND season_year = tf_season THEN matches END), 0) AS season_tackle_match_pct,
    IFNULL(SUM(CASE WHEN tackles > 0 AND is_substitute = 0 AND season_year = tf_season THEN tackles END) / SUM(CASE WHEN is_substitute = 0 AND season_year = tf_season THEN matches END), 0) AS season_avg_tackles
    
    FROM players_base_data pbd
    INNER JOIN players_last_5_data pl5d
    ON pbd.player_id = pl5d.player_id
    WHERE 1 = 1
    GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
    ;
    ''',
    '''
    DROP TABLE IF EXISTS master_players_view
    ;
    ''',
    '''
    CREATE TABLE master_players_view AS
        SELECT
        DISTINCT
        pda.fixture_id,
        pda.team_id,
        pda.player_id,
        -- foul and YC metrics --
        pda.avg_fouls_total,
        pda.season_avg_fouls,
        pl5d.last5_start_foul,
        1 - pda.foul_match_pct AS zero_foul_match_pct,
        1 - pda.season_foul_match_pct AS zero_foul_shot_match_pct,
        pda.avg_yc_total,
        pda.season_avg_yc,
        pl5d.last5_start_yc,
    
        -- shots, sot, goals metrics --
        pda.avg_shots_total,
        pda.season_avg_shots,
        pl5d.last5_shots_total,
        1 - pda.shot_match_pct AS zero_shot_match_pct,
        1 - pda.season_shot_match_pct AS zero_season_shot_match_pct,
        pda.avg_sot_total,
        pda.season_avg_sot,
        pl5d.last5_sot_total,
        1 - pda.sot_match_pct AS zero_sot_match_pct,
        1 - pda.season_sot_match_pct AS zero_season_sot_match_pct,
        pda.avg_goals_total,
        pda.season_avg_goals,
        pl5d.last5_start_goal,
        1 - pda.goal_match_pct AS zero_goal_match_pct,
        1 - pda.season_goal_match_pct AS zero_season_goal_match_pct,
    
        -- Offside metrics --
        pda.avg_offsides_total,
        pda.season_avg_offsides,
        pl5d.last5_offsides,
        1 - pda.offside_match_pct AS zero_offside_match_pct,
        1 - pda.season_offside_match_pct AS zero_season_offside_match_pct,
    
        -- Tackle metrics --
        pda.avg_tackles_total,
        pda.season_avg_tackles,
        pl5d.last5_tackles_total,
        1 - pda.tackle_match_pct AS zero_tackle_match_pct,
        1 - pda.season_tackle_match_pct AS zero_season_tackle_match_pct,
    
        -- Extra metrics --
        pl5d.last5_sub_foul,
        pl5d.last5_sub_yc,
        pl5d.last5_sub_mins,
        pl5d.last5_sub_result,
        pl5d.last5_win_sub_foul,
        pl5d.last5_loss_sub_foul,
        pl5d.last5_draw_sub_foul,
        pl5d.last5_start_result
        FROM players_data_agg pda
        JOIN players_last_5_data pl5d on pda.player_id = pl5d.player_id
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
