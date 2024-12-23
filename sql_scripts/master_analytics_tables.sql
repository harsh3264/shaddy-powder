
TRUNCATE analytics.fixture_stats_compile_test
;


INSERT INTO analytics.fixture_stats_compile_test
SELECT DISTINCT
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
       fs.goalkeeper_saves,
       fs.against_total_passes,
       fs.against_passes_accurate,
       fs.against_passes_percentage,
       fs.expected_goals,
       fs.against_expected_goals,
       fs.team_id,
       fs.against_team_id,
       cr.cleaned_referee_name
FROM base_data_apis.fixtures_stats fs
    LEFT JOIN base_data_apis.fixtures f on fs.fixture_id = f.fixture_id
    LEFT JOIN base_data_apis.fixture_coach fc on f.fixture_id = fc.fixture_id AND fs.team_id = fc.team_id
    LEFT JOIN base_data_apis.fixture_coach fc2 on f.fixture_id = fc2.fixture_id AND fs.against_team_id = fc2.team_id
    LEFT JOIN base_data_apis.leagues l on f.league_id = l.league_id AND f.season_year = l.season_year
    LEFT JOIN base_data_apis.cleaned_referees cr ON f.referee = cr.original_referee_name
WHERE 1 = 1
;


TRUNCATE analytics.fixture_stats_compile
;


INSERT INTO analytics.fixture_stats_compile
SELECT *,
       DENSE_RANK() over (partition by cleaned_referee_name ORDER BY fixture_date DESC) AS refree_r,
       DENSE_RANK() over (partition by cleaned_referee_name, league_id ORDER BY fixture_date DESC) AS refree_league_r,
       ROW_NUMBER() over (partition by team_id ORDER BY fixture_date DESC) AS team_r,
       ROW_NUMBER() over (partition by team_id, league_id ORDER BY fixture_date DESC) AS team_league_r
FROM analytics.fixture_stats_compile_test fsct
WHERE 1 = 1
;


UPDATE analytics.fixture_stats_compile AS fsc
SET fsc.result = CASE WHEN team_goals > against_team_goals THEN 'Win'
                      WHEN against_team_goals > team_goals THEN 'Loss'
                      ELSE 'Draw' END,
    fsc.btts = CASE WHEN team_goals > 0 AND against_team_goals > 0 THEN 1
                ELSE 0 END
WHERE 1 = 1
;


TRUNCATE analytics.tackle_pens_update
;


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


UPDATE analytics.fixture_stats_compile AS fsc
JOIN analytics.tackle_pens_update AS tpu ON fsc.fixture_id = tpu.fixture_id AND fsc.team_id = tpu.team_id
SET fsc.tackles = tpu.tackles,
    fsc.penalty_won = tpu.penalty_won
WHERE 1 = 1
AND tpu.team_id IS NOT NULL
;


UPDATE analytics.fixture_stats_compile AS fsc
JOIN analytics.tackle_pens_update AS tpu ON fsc.fixture_id = tpu.fixture_id AND fsc.against_team_id = tpu.team_id
SET fsc.against_tackles = tpu.tackles,
    fsc.against_penalty_won = tpu.penalty_won
WHERE 1 = 1
AND tpu.team_id IS NOT NULL
;


DROP TABLE IF EXISTS analytics.event_level_card_info;


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
  f.referee,
  fsc.league_id,
  fsc.league_name,
  fsc.team_name,
  fsc.against_team_name,
  fsc.team_goals,
  fsc.against_team_goals,
  fsc.result,
  ps.goals_total AS goals,
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
  ps.team_id,
  row_number() over (partition by p.player_id order by f.fixture_date DESC) AS player_rnk,
  row_number() over (partition by p.player_id, COALESCE(fl.is_substitute, 1) order by f.fixture_date DESC) AS player_rnk_sub
FROM base_data_apis.fixture_player_stats ps
LEFT JOIN base_data_apis.players p ON ps.player_id = p.player_id
LEFT JOIN base_data_apis.fixtures f ON ps.fixture_id = f.fixture_id
LEFT JOIN base_data_apis.fixture_lineups fl on ps.player_id = fl.player_id AND ps.fixture_id = fl.fixture_id
LEFT JOIN analytics.fixture_stats_compile fsc on ps.fixture_id = fsc.fixture_id AND ps.team_id = fsc.team_id
LEFT JOIN analytics.event_level_card_info elci on ps.fixture_id = elci.fixture_id AND ps.player_id = elci.player_id
WHERE 1 = 1
;
