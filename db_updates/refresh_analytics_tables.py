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
    TRUNCATE analytics.fixture_stats_compile
    ;
    ''',
    '''
    INSERT INTO analytics.fixture_stats_compile
    SELECT
       DISTINCT
       fs.fixture_id,
       l.league_id,
       l.name,
       f.season_year,
       f.fixture_date,
       fs.team_name,
       fc.coach_name,
       fc.formation AS formation,
       fs.against_team_name,
       fc2.coach_name AS against_coach_name,
       fc2.formation AS against_formation,
       fs.is_home,
       CASE WHEN fs.is_home = 1 THEN f.total_home_goals ELSE f.total_away_goals END AS team_goals,
       CASE WHEN fs.is_home = 1 THEN f.total_away_goals ELSE f.total_home_goals END AS against_team_goals,
       'Draw' AS result,
       0 AS btts,
       fs.shots_on_goal,
       fs.shots_off_goal,
       fs.total_shots,
       fs.blocked_shots,
       fs.shots_inside_box,
       fs.shots_outside_box,
       fs.fouls,
       0 AS tackles,
       fs.corner_kicks,
       fs.offsides,
       0 AS penalty_won,
       fs.ball_possession,
       fs.yellow_cards,
       fs.red_cards,
       fs.goalkeeper_saves,
       fs.total_passes,
       fs.passes_accurate,
       fs.passes_percentage,
       fs.against_shots_on_goal,
       fs.against_shots_off_goal,
       fs.against_total_shots,
       fs.against_blocked_shots,
       fs.against_shots_inside_box,
       fs.against_shots_outside_box,
       fs.against_fouls,
       0 AS against_tackles,
       fs.against_corner_kicks,
       fs.against_offsides,
       0 AS against_penalty_won,
       fs.against_ball_possession,
       fs.against_yellow_cards,
       fs.against_red_cards,
       fs.against_goalkeeper_saves,
       fs.against_total_passes,
       fs.against_passes_accurate,
       fs.against_passes_percentage,
       fs.expected_goals,
       fs.against_expected_goals,
       fs.team_id,
       fs.against_team_id,
       cr.cleaned_referee_name,
       RANK() over (partition by cr.cleaned_referee_name ORDER BY f.timestamp DESC) AS refree_r,
       RANK() over (partition by cr.cleaned_referee_name, f.league_id ORDER BY f.timestamp DESC) AS refree_league_r,
       RANK() over (partition by fc.team_id ORDER BY f.timestamp DESC) AS team_r,
       RANK() over (partition by fc.team_id, f.league_id ORDER BY f.timestamp DESC) AS team_league_r
    FROM base_data_apis.fixtures_stats fs
    LEFT JOIN base_data_apis.fixtures f on fs.fixture_id = f.fixture_id
    LEFT JOIN base_data_apis.fixture_coach fc on f.fixture_id = fc.fixture_id AND fs.team_id = fc.team_id
    LEFT JOIN base_data_apis.fixture_coach fc2 on f.fixture_id = fc2.fixture_id AND fs.against_team_id = fc2.team_id
    LEFT JOIN base_data_apis.leagues l on f.league_id = l.league_id
    LEFT JOIN base_data_apis.cleaned_referees cr ON f.referee = cr.original_referee_name
    WHERE
    1 = 1
    ;
    ''',
    '''
    UPDATE analytics.fixture_stats_compile AS fsc
    SET fsc.result = CASE WHEN team_goals > against_team_goals THEN 'Win'
                          WHEN against_team_goals > team_goals THEN 'Loss'
                          ELSE 'Draw' END,
        fsc.btts = CASE WHEN team_goals > 0 AND against_team_goals > 0 THEN 1
                    ELSE 0 END
    WHERE 1 = 1
    ;
    ''',
    '''
    TRUNCATE analytics.tackle_pens_update
    ;
    ''',
    '''
    INSERT INTO analytics.tackle_pens_update
    SELECT
    fixture_id,
    team_id,
    SUM(tackles_total) AS tackles,
    SUM(penalty_won) AS penalty_won
    FROM base_data_apis.fixture_player_stats
    WHERE team_id IS NOT NULL
    GROUP BY 1,2
    ;
    ''',
    '''
    UPDATE analytics.fixture_stats_compile AS fsc
    JOIN analytics.tackle_pens_update AS tpu ON fsc.fixture_id = tpu.fixture_id AND fsc.team_id = tpu.team_id
    SET fsc.tackles = tpu.tackles,
        fsc.penalty_won = tpu.penalty_won
    WHERE 1 = 1
    AND tpu.team_id IS NOT NULL
    ;
    ''',
    '''
    UPDATE analytics.fixture_stats_compile AS fsc
    JOIN analytics.tackle_pens_update AS tpu ON fsc.fixture_id = tpu.fixture_id AND fsc.against_team_id = tpu.team_id
    SET fsc.against_tackles = tpu.tackles,
        fsc.against_penalty_won = tpu.penalty_won
    WHERE 1 = 1
    AND tpu.team_id IS NOT NULL
    ;
    ''',
    '''
    DROP TABLE IF EXISTS analytics.event_level_card_info;
    ''',
    '''
    CREATE TABLE analytics.event_level_card_info AS
    SELECT
    player_id,
    fixture_id,
    comments,
    minute
    FROM base_data_apis.fixture_events
    WHERE type = 'Card'
    AND minute is not null
    GROUP BY 1,2
    ORDER BY event_id DESC
    ;
    ''',
    '''
    DROP TABLE IF EXISTS analytics.fixture_player_stats_compile;
    ''',
    '''
    CREATE TABLE analytics.fixture_player_stats_compile
    AS
    SELECT
      ps.player_id,
      p.name AS player_name,
      p.nationality,
      COALESCE(fl.is_substitute, 1) AS is_substitute,
      ps.fixture_id,
      fsc.season_year,
      fsc.fixture_date,
      f.referee,
      fsc.league_id,
      fsc.league_name,
      fsc.team_name,
      fsc.against_team_name,
      fsc.team_goals,
      fsc.against_team_goals,
      fsc.result,
      ps.minutes_played,
      ps.fouls_committed,
      ps.fouls_drawn,
      ps.offsides,
      ps.shots_total,
      ps.shots_on_target,
      ps.tackles_total,
      ps.duels_total,
      ps.duels_won,
      ps.dribbles_attempts,
      ps.dribbles_success,
      ps.dribbles_past,
      ps.cards_yellow,
      ps.cards_red,
      elci.minute AS card_minute,
      elci.comments AS card_reason,
      ps.team_id
    FROM base_data_apis.fixture_player_stats ps
    LEFT JOIN base_data_apis.players p ON ps.player_id = p.player_id
    LEFT JOIN base_data_apis.fixtures f ON ps.fixture_id = f.fixture_id
    LEFT JOIN base_data_apis.fixture_lineups fl on ps.player_id = fl.player_id AND ps.fixture_id = fl.fixture_id
    LEFT JOIN analytics.fixture_stats_compile fsc on ps.fixture_id = fsc.fixture_id AND ps.team_id = fsc.team_id
    LEFT JOIN analytics.event_level_card_info elci on ps.fixture_id = elci.fixture_id AND ps.player_id = elci.player_id
    WHERE 1 = 1
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
