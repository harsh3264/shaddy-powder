USE analytics;

-- DROP TABLE IF EXISTS analytics.fixture_stats_compile;

-- CREATE TABLE analytics.fixture_stats_compile (
--   `fixture_id` int,
--   `team_id` int,
--   `team_name` varchar(60) DEFAULT NULL,
--   `against_team_id` int DEFAULT NULL,
--   `against_team_name` varchar(60) DEFAULT NULL,
--   `is_home` int NOT NULL,
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
--   `team_goals` int DEFAULT NULL,
--   `against_team_goals` int DEFAULT NULL,
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
       CASE WHEN fs.is_home = 1 THEN f.total_home_goals ELSE f.total_away_goals END AS team_goals,
       CASE WHEN fs.is_home = 1 THEN f.total_away_goals ELSE f.total_home_goals END AS against_team_goals,
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
;

UPDATE analytics.fixture_stats_compile AS fsc
JOIN tackle_pens_update AS tpu ON fsc.fixture_id = tpu.fixture_id AND fsc.against_team_id = tpu.team_id
SET fsc.against_tackles = tpu.tackles,
    fsc.against_penalty_won = tpu.penalty_won
;

DROP TABLE tackle_pens_update;






