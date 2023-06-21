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


-- DROP TABLE IF EXISTS analytics.player_aggregated_stats;

-- CREATE TABLE analytics.player_aggregated_stats (
--   player_id INT,
--   player_name VARCHAR(200) DEFAULT NULL,
--   nationality VARCHAR(200) DEFAULT NULL,
--   is_substitute INT,
--   total_matches INT,
--   total_teams INT,
--   offsides FLOAT,
--   offsides_percentage FLOAT,
--   shots_total FLOAT,
--   shots_total_percentage FLOAT,
--   shots_on_target FLOAT,
--   shots_on_target_percentage FLOAT,
--   goals_total FLOAT,
--   goals_total_percentage FLOAT,
--   goals_conceded FLOAT,
--   goals_conceded_percentage FLOAT,
--   assists FLOAT,
--   assists_percentage FLOAT,
--   saves FLOAT,
--   saves_percentage FLOAT,
--   passes_total FLOAT,
--   passes_total_percentage FLOAT,
--   passes_key FLOAT,
--   passes_key_percentage FLOAT,
--   passes_accuracy FLOAT,
--   passes_accuracy_percentage FLOAT,
--   tackles_total FLOAT,
--   tackles_total_percentage FLOAT,
--   tackles_blocks FLOAT,
--   tackles_blocks_percentage FLOAT,
--   tackles_interceptions FLOAT,
--   tackles_interceptions_percentage FLOAT,
--   duels_total FLOAT,
--   duels_total_percentage FLOAT,
--   duels_won FLOAT,
--   duels_won_percentage FLOAT,
--   dribbles_attempts FLOAT,
--   dribbles_attempts_percentage FLOAT,
--   dribbles_success FLOAT,
--   dribbles_success_percentage FLOAT,
--   dribbles_past FLOAT,
--   dribbles_past_percentage FLOAT,
--   fouls_drawn FLOAT,
--   fouls_drawn_percentage FLOAT,
--   fouls_committed FLOAT,
--   fouls_committed_percentage FLOAT,
--   cards_yellow FLOAT,
--   cards_red FLOAT,
--   penalty_won FLOAT,
--   penalty_won_percentage FLOAT,
--   penalty_committed FLOAT,
--   penalty_committed_percentage FLOAT,
--   penalty_scored FLOAT,
--   penalty_scored_percentage FLOAT,
--   penalty_missed FLOAT,
--   penalty_missed_percentage FLOAT,
--   penalty_saved FLOAT,
--   penalty_saved_percentage FLOAT,
--   PRIMARY KEY (player_id, is_substitute)
-- );

INSERT IGNORE INTO analytics.player_aggregated_stats
SELECT
  ps.player_id,
  p.name AS player_name,
  p.nationality,
  COALESCE(fl.is_substitute, 1) AS is_substitute,
  COUNT(DISTINCT ps.fixture_id) AS total_matches,
  COUNT(DISTINCT ps.team_id) AS total_teams,
  ROUND(SUM(offsides) / COUNT(DISTINCT ps.fixture_id), 2) AS offsides,
  ROUND(SUM(offsides > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS offsides_percentage,
  ROUND(SUM(shots_total) / COUNT(DISTINCT ps.fixture_id), 2)  AS shots_total,
  ROUND(SUM(shots_total > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS shots_total_percentage,
  ROUND(SUM(shots_on_target) / COUNT(DISTINCT ps.fixture_id), 2)  AS shots_on_target,
  ROUND(SUM(shots_on_target > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS shots_on_target_percentage,
  ROUND(SUM(goals_total) / COUNT(DISTINCT ps.fixture_id), 2)  AS goals_total,
  ROUND(SUM(goals_total > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS goals_total_percentage,
  ROUND(SUM(goals_conceded) / COUNT(DISTINCT ps.fixture_id), 2) AS goals_conceded,
  ROUND(SUM(goals_conceded > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS goals_conceded_percentage,
  ROUND(SUM(assists) / COUNT(DISTINCT ps.fixture_id), 2)  AS assists,
  ROUND(SUM(assists > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS assists_percentage,
  ROUND(SUM(saves) / COUNT(DISTINCT ps.fixture_id), 2)  AS saves,
  ROUND(SUM(saves > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS saves_percentage,
  ROUND(SUM(passes_total) / COUNT(DISTINCT ps.fixture_id), 2)  AS passes_total,
  ROUND(SUM(passes_total > 40) / COUNT(DISTINCT ps.fixture_id), 2) AS passes_total_percentage,
  ROUND(SUM(passes_key) / COUNT(DISTINCT ps.fixture_id), 2)  AS passes_key,
  ROUND(SUM(passes_key > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS passes_key_percentage,
  ROUND(SUM(passes_accuracy) / COUNT(DISTINCT ps.fixture_id), 2)  AS passes_accuracy,
  ROUND(SUM(passes_accuracy > 80) / COUNT(DISTINCT ps.fixture_id), 2) AS passes_accuracy_percentage,
  ROUND(SUM(tackles_total) / COUNT(DISTINCT ps.fixture_id), 2) AS tackles_total,
  ROUND(SUM(tackles_total > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS tackles_total_percentage,
  ROUND(SUM(tackles_blocks) / COUNT(DISTINCT ps.fixture_id), 2)  AS tackles_blocks,
  ROUND(SUM(tackles_blocks > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS tackles_blocks_percentage,
  ROUND(SUM(tackles_interceptions) / COUNT(DISTINCT ps.fixture_id), 2)  AS tackles_interceptions,
  ROUND(SUM(tackles_interceptions > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS tackles_interceptions_percentage,
  ROUND(SUM(duels_total) / COUNT(DISTINCT ps.fixture_id), 2) AS duels_total,
  ROUND(SUM(duels_total > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS duels_total_percentage,
  ROUND(SUM(duels_won) / COUNT(DISTINCT ps.fixture_id), 2) AS duels_won,
  ROUND(SUM(duels_won > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS duels_won_percentage,
  ROUND(SUM(dribbles_attempts) / COUNT(DISTINCT ps.fixture_id), 2)  AS dribbles_attempts,
  ROUND(SUM(dribbles_attempts > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS dribbles_attempts_percentage,
  ROUND(SUM(dribbles_success) / COUNT(DISTINCT ps.fixture_id), 2) AS dribbles_success,
  ROUND(SUM(dribbles_success > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS dribbles_success_percentage,
  ROUND(SUM(dribbles_past) / COUNT(DISTINCT ps.fixture_id), 2) AS dribbles_past,
  ROUND(SUM(dribbles_past > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS dribbles_past_percentage,
  ROUND(SUM(fouls_drawn) / COUNT(DISTINCT ps.fixture_id), 2) AS fouls_drawn,
  ROUND(SUM(fouls_drawn > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS fouls_drawn_percentage,
  ROUND(SUM(fouls_committed) / COUNT(DISTINCT ps.fixture_id), 2) AS fouls_committed,
  ROUND(SUM(fouls_committed > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS fouls_committed_percentage,
  ROUND(SUM(cards_yellow) / COUNT(DISTINCT ps.fixture_id), 2) AS cards_yellow,
--   SUM(cards_yellow > 0) / COUNT(DISTINCT ps.fixture_id) AS cards_yellow_percentage,
  ROUND(SUM(cards_red) / COUNT(DISTINCT ps.fixture_id), 2) AS cards_red,
--   SUM(cards_red > 0) / COUNT(DISTINCT ps.fixture_id) AS cards_red_percentage,
  ROUND(SUM(penalty_won) / COUNT(DISTINCT ps.fixture_id), 2) AS penalty_won,
  ROUND(SUM(penalty_won > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS penalty_won_percentage,
  ROUND(SUM(penalty_committed) / COUNT(DISTINCT ps.fixture_id), 2) AS penalty_committed,
  ROUND(SUM(penalty_committed > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS penalty_committed_percentage,
  ROUND(SUM(penalty_scored) / COUNT(DISTINCT ps.fixture_id), 2) AS penalty_scored,
  ROUND(SUM(penalty_scored > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS penalty_scored_percentage,
  ROUND(SUM(penalty_missed) / COUNT(DISTINCT ps.fixture_id), 2) AS penalty_missed,
  ROUND(SUM(penalty_missed > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS penalty_missed_percentage,
  ROUND(SUM(penalty_saved) / COUNT(DISTINCT ps.fixture_id), 2) AS penalty_saved,
  ROUND(SUM(penalty_saved > 0) / COUNT(DISTINCT ps.fixture_id), 2) AS penalty_saved_percentage
FROM fixture_player_stats ps
LEFT JOIN players p ON ps.player_id = p.player_id
LEFT JOIN fixture_lineups fl on ps.player_id = fl.player_id AND ps.fixture_id = fl.fixture_id
WHERE ps.player_id != 0
GROUP BY ps.player_id, is_substitute;



DROP TABLE IF EXISTS event_level_card_info;

CREATE TABLE event_level_card_info AS
SELECT
player_id,
fixture_id,
comments,
minute
FROM fixture_events
WHERE type = 'Card'
AND minute is not null
GROUP BY 1,2
ORDER BY event_id DESC
;


DROP TABLE IF EXISTS analytics.fixture_player_stats_compile;

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
  ps.tackles_total,
  ps.duels_total,
  ps.duels_won,
  ps.dribbles_attempts,
  ps.dribbles_success,
  ps.dribbles_past,
  ps.cards_yellow,
  ps.cards_red,
  elci.minute AS card_minute,
  elci.comments AS card_reason
FROM fixture_player_stats ps
LEFT JOIN players p ON ps.player_id = p.player_id
LEFT JOIN fixture_lineups fl on ps.player_id = fl.player_id AND ps.fixture_id = fl.fixture_id
LEFT JOIN analytics.fixture_stats_compile fsc on ps.fixture_id = fsc.fixture_id AND ps.team_id = fsc.team_id
LEFT JOIN event_level_card_info elci on ps.fixture_id = elci.fixture_id AND ps.player_id = elci.player_id
WHERE 1 = 1
-- AND fixture_id = 1030271
;

DROP TABLE event_level_card_info;





