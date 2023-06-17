USE analytics;

-- DROP TABLE IF EXISTS analytics.fixture_stats_compile;

-- CREATE TABLE analytics.fixture_stats_compile (
--   `fixture_id` int,
--   `team_id` int,
--   `team_name` varchar(60) DEFAULT NULL,
--   `against_team_id` int DEFAULT NULL,
--   `against_team_name` varchar(60) DEFAULT NULL,
--   `is_home` int NOT NULL,
--   `team_goals` int DEFAULT 0,
--   `against_team_goals` int DEFAULT 0,
--   `result` varchar(10) DEFAULT NULL,
--   `btts` int DEFAULT NULL,
--   `shots_on_goal` int DEFAULT NULL,
--   `shots_off_goal` int DEFAULT NULL,
--   `total_shots` int DEFAULT NULL,
--   `blocked_shots` int DEFAULT NULL,
--   `shots_inside_box` int DEFAULT NULL,
--   `shots_outside_box` int DEFAULT NULL,
--   `fouls` int DEFAULT NULL,
--   `tackles` int DEFAULT NULL,
--   `corner_kicks` int DEFAULT NULL,
--   `offsides` int DEFAULT NULL,
--   `penalty_won` int DEFAULT NULL,
--   `ball_possession` int DEFAULT NULL,
--   `yellow_cards` int DEFAULT NULL,
--   `red_cards` int DEFAULT NULL,
--   `goalkeeper_saves` int DEFAULT NULL,
--   `total_passes` int DEFAULT NULL,
--   `passes_accurate` int DEFAULT NULL,
--   `passes_percentage` int DEFAULT NULL,
--   `against_shots_on_goal` int DEFAULT NULL,
--   `against_shots_off_goal` int DEFAULT NULL,
--   `against_total_shots` int DEFAULT NULL,
--   `against_blocked_shots` int DEFAULT NULL,
--   `against_shots_inside_box` int DEFAULT NULL,
--   `against_shots_outside_box` int DEFAULT NULL,
--   `against_fouls` int DEFAULT NULL,
--   `against_tackles` int DEFAULT NULL,
--   `against_corner_kicks` int DEFAULT NULL,
--   `against_offsides` int DEFAULT NULL,
--   `against_penalty_won` int DEFAULT NULL,
--   `against_ball_possession` int DEFAULT NULL,
--   `against_yellow_cards` int DEFAULT NULL,
--   `against_red_cards` int DEFAULT NULL,
--   `against_goalkeeper_saves` int DEFAULT NULL,
--   `against_total_passes` int DEFAULT NULL,
--   `against_passes_accurate` int DEFAULT NULL,
--   `against_passes_percentage` int DEFAULT NULL,
--   `expected_goals` float DEFAULT NULL,
--   `against_expected_goals` float DEFAULT NULL,
--   `season_year` int DEFAULT NULL,
--   `fixture_date` date DEFAULT NULL,
--   `coach_name` varchar(255) DEFAULT NULL,
--   `against_coach_name` varchar(255) DEFAULT NULL,
--   `formation` varchar(255) DEFAULT NULL,
--   `against_formation` varchar(255) DEFAULT NULL,
--   primary key (`fixture_id`, `team_id`)
-- );

INSERT INTO analytics.fixture_stats_compile
SELECT
       DISTINCT
       fs.fixture_id,
       fs.team_id,
       fs.team_name,
       fs.against_team_id,
       fs.against_team_name,
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
       f.season_year,
       f.fixture_date,
       fc.coach_name,
       fc2.coach_name AS against_coach_name,
       fc.formation AS formation,
       fc2.formation AS against_formation
FROM base_data_apis.fixtures_stats fs
    LEFT JOIN base_data_apis.fixtures f on fs.fixture_id = f.fixture_id
    LEFT JOIN base_data_apis.fixture_coach fc on f.fixture_id = fc.fixture_id AND fs.team_id = fc.team_id
    LEFT JOIN base_data_apis.fixture_coach fc2 on f.fixture_id = fc2.fixture_id AND fs.against_team_id = fc2.team_id
    LEFT JOIN base_data_apis.leagues l on f.league_id = l.league_id
WHERE
1 = 1
AND f.fixture_id NOT IN (SELECT fixture_id FROM analytics.fixture_stats_compile)
ORDER BY fixture_date
;

UPDATE analytics.fixture_stats_compile AS fsc
SET fsc.result = CASE WHEN team_goals > against_team_goals THEN 'Win'
                      WHEN against_team_goals > team_goals THEN 'Loss'
                      ELSE 'Draw' END,
    fsc.btts = CASE WHEN team_goals > 0 AND against_team_goals > 0 THEN 1
                ELSE 0 END
WHERE 1 = 1
;

DROP TABLE IF EXISTS tackle_pens_update;

CREATE TABLE tackle_pens_update
AS
SELECT
fixture_id,
team_id,
SUM(tackles_total) AS tackles,
SUM(penalty_won) AS penalty_won
FROM base_data_apis.fixture_player_stats
GROUP BY 1,2
;

UPDATE analytics.fixture_stats_compile AS fsc
JOIN tackle_pens_update AS tpu ON fsc.fixture_id = tpu.fixture_id AND fsc.team_id = tpu.team_id
SET fsc.tackles = tpu.tackles,
    fsc.penalty_won = tpu.penalty_won
WHERE 1 = 1
;

UPDATE analytics.fixture_stats_compile AS fsc
JOIN tackle_pens_update AS tpu ON fsc.fixture_id = tpu.fixture_id AND fsc.against_team_id = tpu.team_id
SET fsc.against_tackles = tpu.tackles,
    fsc.against_penalty_won = tpu.penalty_won
WHERE 1 = 1
;

DROP TABLE tackle_pens_update;

        SELECT
            player_id,
            MAX(season_year) - 1 AS season_year
        FROM fixture_player_stats fps
        LEFT JOIN fixtures f on fps.fixture_id = f.fixture_id
        WHERE
            1 = 1
            # AND league_id IN (88)
            AND player_id NOT IN (SELECT player_id FROM players)
            AND player_id IN (SELECT player_id FROM fixture_player_stats)
            AND player_id <> 0
        GROUP BY 1
        ORDER BY 2 DESC
        ;


DROP TABLE IF EXISTS analytics.player_aggregated_stats;

CREATE TABLE analytics.player_aggregated_stats (
  player_id INT,
  player_name VARCHAR(200) DEFAULT NULL,
  nationality VARCHAR(200) DEFAULT NULL,
  is_substitute INT,
  total_matches INT,
  total_teams INT,
  offsides INT,
  offsides_percentage FLOAT,
  shots_total INT,
  shots_total_percentage FLOAT,
  shots_on_target INT,
  shots_on_target_percentage FLOAT,
  goals_total INT,
  goals_total_percentage FLOAT,
  goals_conceded INT,
  goals_conceded_percentage FLOAT,
  assists INT,
  assists_percentage FLOAT,
  saves INT,
  saves_percentage FLOAT,
  passes_total INT,
  passes_total_percentage FLOAT,
  passes_key INT,
  passes_key_percentage FLOAT,
  passes_accuracy INT,
  passes_accuracy_percentage FLOAT,
  tackles_total INT,
  tackles_total_percentage FLOAT,
  tackles_blocks INT,
  tackles_blocks_percentage FLOAT,
  tackles_interceptions INT,
  tackles_interceptions_percentage FLOAT,
  duels_total INT,
  duels_total_percentage FLOAT,
  duels_won INT,
  duels_won_percentage FLOAT,
  dribbles_attempts INT,
  dribbles_attempts_percentage FLOAT,
  dribbles_success INT,
  dribbles_success_percentage FLOAT,
  dribbles_past INT,
  dribbles_past_percentage FLOAT,
  fouls_drawn INT,
  fouls_drawn_percentage FLOAT,
  fouls_committed INT,
  fouls_committed_percentage FLOAT,
  cards_yellow INT,
  cards_yellow_percentage FLOAT,
  cards_red INT,
  cards_red_percentage FLOAT,
  penalty_won INT,
  penalty_won_percentage FLOAT,
  penalty_committed INT,
  penalty_committed_percentage FLOAT,
  penalty_scored INT,
  penalty_scored_percentage FLOAT,
  penalty_missed INT,
  penalty_missed_percentage FLOAT,
  penalty_saved INT,
  penalty_saved_percentage FLOAT,
  PRIMARY KEY (player_id, is_substitute)
);

INSERT INTO analytics.player_aggregated_stats
SELECT
  ps.player_id,
  p.name AS player_name,
  p.nationality,
  IFNULL(fl.is_substitute, 1) AS is_substitute,
  COUNT(DISTINCT ps.fixture_id) AS total_matches,
  COUNT(DISTINCT ps.team_id) AS total_teams,
  SUM(offsides) AS offsides,
  SUM(offsides > 0) / COUNT(DISTINCT ps.fixture_id) AS offsides_percentage,
  SUM(shots_total) AS shots_total,
  SUM(shots_total > 0) / COUNT(DISTINCT ps.fixture_id) AS shots_total_percentage,
  SUM(shots_on_target) AS shots_on_target,
  SUM(shots_on_target > 0) / COUNT(DISTINCT ps.fixture_id) AS shots_on_target_percentage,
  SUM(goals_total) AS goals_total,
  SUM(goals_total > 0) / COUNT(DISTINCT ps.fixture_id) AS goals_total_percentage,
  SUM(goals_conceded) AS goals_conceded,
  SUM(goals_conceded > 0) / COUNT(DISTINCT ps.fixture_id) AS goals_conceded_percentage,
  SUM(assists) AS assists,
  SUM(assists > 0) / COUNT(DISTINCT ps.fixture_id) AS assists_percentage,
  SUM(saves) AS saves,
  SUM(saves > 0) / COUNT(DISTINCT ps.fixture_id) AS saves_percentage,
  SUM(passes_total) AS passes_total,
  SUM(passes_total > 0) / COUNT(DISTINCT ps.fixture_id) AS passes_total_percentage,
  SUM(passes_key) AS passes_key,
  SUM(passes_key > 0) / COUNT(DISTINCT ps.fixture_id) AS passes_key_percentage,
  SUM(passes_accuracy) AS passes_accuracy,
  SUM(passes_accuracy > 0) / COUNT(DISTINCT ps.fixture_id) AS passes_accuracy_percentage,
  SUM(tackles_total) AS tackles_total,
  SUM(tackles_total > 0) / COUNT(DISTINCT ps.fixture_id) AS tackles_total_percentage,
  SUM(tackles_blocks) AS tackles_blocks,
  SUM(tackles_blocks > 0) / COUNT(DISTINCT ps.fixture_id) AS tackles_blocks_percentage,
  SUM(tackles_interceptions) AS tackles_interceptions,
  SUM(tackles_interceptions > 0) / COUNT(DISTINCT ps.fixture_id) AS tackles_interceptions_percentage,
  SUM(duels_total) AS duels_total,
  SUM(duels_total > 0) / COUNT(DISTINCT ps.fixture_id) AS duels_total_percentage,
  SUM(duels_won) AS duels_won,
  SUM(duels_won > 0) / COUNT(DISTINCT ps.fixture_id) AS duels_won_percentage,
  SUM(dribbles_attempts) AS dribbles_attempts,
  SUM(dribbles_attempts > 0) / COUNT(DISTINCT ps.fixture_id) AS dribbles_attempts_percentage,
  SUM(dribbles_success) AS dribbles_success,
  SUM(dribbles_success > 0) / COUNT(DISTINCT ps.fixture_id) AS dribbles_success_percentage,
  SUM(dribbles_past) AS dribbles_past,
  SUM(dribbles_past > 0) / COUNT(DISTINCT ps.fixture_id) AS dribbles_past_percentage,
  SUM(fouls_drawn) AS fouls_drawn,
  SUM(fouls_drawn > 0) / COUNT(DISTINCT ps.fixture_id) AS fouls_drawn_percentage,
  SUM(fouls_committed) AS fouls_committed,
  SUM(fouls_committed > 0) / COUNT(DISTINCT ps.fixture_id) AS fouls_committed_percentage,
  SUM(cards_yellow) AS cards_yellow,
  SUM(cards_yellow > 0) / COUNT(DISTINCT ps.fixture_id) AS cards_yellow_percentage,
  SUM(cards_red) AS cards_red,
  SUM(cards_red > 0) / COUNT(DISTINCT ps.fixture_id) AS cards_red_percentage,
  SUM(penalty_won) AS penalty_won,
  SUM(penalty_won > 0) / COUNT(DISTINCT ps.fixture_id) AS penalty_won_percentage,
  SUM(penalty_committed) AS penalty_committed,
  SUM(penalty_committed > 0) / COUNT(DISTINCT ps.fixture_id) AS penalty_committed_percentage,
  SUM(penalty_scored) AS penalty_scored,
  SUM(penalty_scored > 0) / COUNT(DISTINCT ps.fixture_id) AS penalty_scored_percentage,
  SUM(penalty_missed) AS penalty_missed,
  SUM(penalty_missed > 0) / COUNT(DISTINCT ps.fixture_id) AS penalty_missed_percentage,
  SUM(penalty_saved) AS penalty_saved,
  SUM(penalty_saved > 0) / COUNT(DISTINCT ps.fixture_id) AS penalty_saved_percentage
FROM fixture_player_stats ps
LEFT JOIN players p ON ps.player_id = p.player_id
LEFT JOIN fixture_lineups fl on ps.player_id = fl.player_id AND ps.fixture_id = fl.fixture_id
GROUP BY ps.player_id, is_substitute;

SELECT * FROM analytics.player_aggregated_stats WHERE
is_substitute = 0;

SELECT *
FROM fixture_player_stats ps
LEFT JOIN players p ON ps.player_id = p.player_id
LEFT JOIN fixture_lineups fl on ps.player_id = fl.player_id AND ps.fixture_id = fl.fixture_id
LEFT JOIN fixtures f on ps.fixture_id = f.fixture_id
WHERE is_substitute IS NULL
AND p.player_id != 0;




-- SELECT * FROM analytics.fixture_stats_compile WHERE team_name IN ('Belgium', 'Norway');









