
DROP TABLE IF EXISTS teams_base_data
;


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
SUM(team_goals) AS goals,
COUNT(DISTINCT CASE WHEN IFNULL(team_goals, 0) > 0 THEN fpsc.fixture_id END) AS goals_matches,
SUM(against_team_goals) AS goals_against,
COUNT(DISTINCT CASE WHEN IFNULL(against_team_goals, 0) > 0 THEN fpsc.fixture_id END) AS against_goal_matches,
COUNT(DISTINCT CASE WHEN btts > 0 THEN fpsc.fixture_id END) AS btts,
SUM(fouls) AS fouls,
SUM(against_fouls) AS fouls_drawn,
SUM(total_shots) AS shots,
SUM(against_total_shots) AS shots_concede,
SUM(IFNULL(corner_kicks, 0)) AS corners,
COUNT(DISTINCT CASE WHEN IFNULL(corner_kicks, 0) > 0 THEN fpsc.fixture_id END) AS corner_matches,
SUM(IFNULL(against_corner_kicks, 0)) AS corners_against,
COUNT(DISTINCT CASE WHEN IFNULL(against_corner_kicks, 0) > 0 THEN fpsc.fixture_id END) AS against_corner_matches,
SUM(IFNULL(offsides, 0)) AS offsides,
COUNT(DISTINCT CASE WHEN IFNULL(offsides, 0) > 0 THEN fpsc.fixture_id END) AS offside_matches,
SUM(IFNULL(against_offsides, 0)) AS offsides_against,
COUNT(DISTINCT CASE WHEN IFNULL(against_offsides, 0) > 0 THEN fpsc.fixture_id END) AS against_offside_matches,
SUM(tackles) AS tackles,
SUM(against_tackles) AS tackles_concede,
SUM(IFNULL(yellow_cards, 0)) AS yc,
COUNT(DISTINCT CASE WHEN IFNULL(yellow_cards, 0) > 0 THEN fpsc.fixture_id END) AS yc_matches,
SUM(IFNULL(against_yellow_cards, 0)) AS yc_against,
COUNT(DISTINCT CASE WHEN IFNULL(against_yellow_cards, 0) > 0 THEN fpsc.fixture_id END) AS yc_against_matches
FROM analytics.fixture_stats_compile fpsc
INNER JOIN today_fixture tf on fpsc.team_id = tf.home_team_id
WHERE 1 = 1
AND league_name IS NOT NULL
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9
HAVING matches > 1
;


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
SUM(team_goals) AS goals,
COUNT(DISTINCT CASE WHEN IFNULL(team_goals, 0) > 0 THEN fpsc.fixture_id END) AS goals_matches,
SUM(against_team_goals) AS goals_against,
COUNT(DISTINCT CASE WHEN IFNULL(against_team_goals, 0) > 0 THEN fpsc.fixture_id END) AS against_goal_matches,
COUNT(DISTINCT CASE WHEN btts > 0 THEN fpsc.fixture_id END) AS btts,
SUM(fouls) AS fouls,
SUM(against_fouls) AS fouls_drawn,
SUM(total_shots) AS shots,
SUM(against_total_shots) AS shots_concede,
SUM(IFNULL(corner_kicks, 0)) AS corners,
COUNT(DISTINCT CASE WHEN IFNULL(corner_kicks, 0) > 0 THEN fpsc.fixture_id END) AS corner_matches,
SUM(IFNULL(against_corner_kicks, 0)) AS corners_against,
COUNT(DISTINCT CASE WHEN IFNULL(against_corner_kicks, 0) > 0 THEN fpsc.fixture_id END) AS against_corner_matches,
SUM(IFNULL(offsides, 0)) AS offsides,
COUNT(DISTINCT CASE WHEN IFNULL(offsides, 0) > 0 THEN fpsc.fixture_id END) AS offside_matches,
SUM(IFNULL(against_offsides, 0)) AS offsides_against,
COUNT(DISTINCT CASE WHEN IFNULL(against_offsides, 0) > 0 THEN fpsc.fixture_id END) AS against_offside_matches,
SUM(tackles) AS tackles,
SUM(against_tackles) AS tackles_concede,
SUM(IFNULL(yellow_cards, 0)) AS yc,
COUNT(DISTINCT CASE WHEN IFNULL(yellow_cards, 0) > 0 THEN fpsc.fixture_id END) AS yc_matches,
SUM(IFNULL(against_yellow_cards, 0)) AS yc_against,
COUNT(DISTINCT CASE WHEN IFNULL(against_yellow_cards, 0) > 0 THEN fpsc.fixture_id END) AS yc_against_matches
FROM analytics.fixture_stats_compile fpsc
INNER JOIN today_fixture tf on fpsc.team_id = tf.away_team_id
WHERE 1 = 1
AND league_name IS NOT NULL
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9
HAVING matches > 1
;


INSERT INTO teams_base_data
SELECT
fpsc.team_id,
fpsc.team_name,
0,
'X-Y',
tls.max_season AS tf_season,
'00:00',
'XXX' AS tf_league,
fpsc.league_name,
fpsc.season_year,
COUNT(DISTINCT fpsc.fixture_id) AS matches,
SUM(team_goals) AS goals,
COUNT(DISTINCT CASE WHEN IFNULL(team_goals, 0) > 0 THEN fpsc.fixture_id END) AS goals_matches,
SUM(against_team_goals) AS goals_against,
COUNT(DISTINCT CASE WHEN IFNULL(against_team_goals, 0) > 0 THEN fpsc.fixture_id END) AS against_goal_matches,
COUNT(DISTINCT CASE WHEN btts > 0 THEN fpsc.fixture_id END) AS btts,
SUM(fouls) AS fouls,
SUM(against_fouls) AS fouls_drawn,
SUM(total_shots) AS shots,
SUM(against_total_shots) AS shots_concede,
SUM(IFNULL(corner_kicks, 0)) AS corners,
COUNT(DISTINCT CASE WHEN IFNULL(corner_kicks, 0) > 0 THEN fpsc.fixture_id END) AS corner_matches,
SUM(IFNULL(against_corner_kicks, 0)) AS corners_against,
COUNT(DISTINCT CASE WHEN IFNULL(against_corner_kicks, 0) > 0 THEN fpsc.fixture_id END) AS against_corner_matches,
SUM(IFNULL(offsides, 0)) AS offsides,
COUNT(DISTINCT CASE WHEN IFNULL(offsides, 0) > 0 THEN fpsc.fixture_id END) AS offside_matches,
SUM(IFNULL(against_offsides, 0)) AS offsides_against,
COUNT(DISTINCT CASE WHEN IFNULL(against_offsides, 0) > 0 THEN fpsc.fixture_id END) AS against_offside_matches,
SUM(tackles) AS tackles,
SUM(against_tackles) AS tackles_concede,
SUM(IFNULL(yellow_cards, 0)) AS yc,
COUNT(DISTINCT CASE WHEN IFNULL(yellow_cards, 0) > 0 THEN fpsc.fixture_id END) AS yc_matches,
SUM(IFNULL(against_yellow_cards, 0)) AS yc_against,
COUNT(DISTINCT CASE WHEN IFNULL(against_yellow_cards, 0) > 0 THEN fpsc.fixture_id END) AS yc_against_matches
FROM analytics.fixture_stats_compile fpsc
INNER JOIN (SELECT team_id, MAX(season_year) AS max_season FROM team_league_season GROUP BY 1) tls
ON fpsc.team_id = tls.team_id
# LEFT JOIN today_fixture tf on fpsc.team_id = tf.away_team_id
WHERE 1 = 1
AND league_name IS NOT NULL
AND fpsc.team_id NOT IN (SELECT team_id FROM teams_base_data)
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9
HAVING matches > 1
;


DROP TABLE IF EXISTS teams_data_agg
;


CREATE TABLE teams_data_agg AS
SELECT
fixture_id,
team_id,
    -- Goals metrics
IFNULL(SUM(CASE WHEN season_year = tf_season THEN goals_matches END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_goal_match_pct,
IFNULL(SUM(CASE WHEN season_year = tf_season THEN goals END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_avg_goals,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN goals_matches END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_goal_match_pct,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN goals END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_avg_goals,
IFNULL(SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN goals END) / SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN matches END), 0) AS league_avg_goals,

    -- Goals Against metrics
IFNULL(SUM(CASE WHEN season_year = tf_season THEN against_goal_matches END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_goal_against_match_pct,
IFNULL(SUM(CASE WHEN season_year = tf_season THEN goals_against END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_avg_goals_against,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN against_goal_matches END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_goal_against_match_pct,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN goals_against END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_avg_goals_against,
IFNULL(SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN goals_against END) / SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN matches END), 0) AS league_avg_goals_against,

    -- BTTS metrics
IFNULL(SUM(CASE WHEN season_year = tf_season THEN btts END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_btts_pct,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN btts END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_btts_pct,
IFNULL(SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN btts END) / SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN matches END), 0) AS league_btts_pct,

-- Yellow Cards (yc) metrics
IFNULL(SUM(CASE WHEN season_year = tf_season THEN yc_matches END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_yc_match_pct,
IFNULL(SUM(CASE WHEN season_year = tf_season THEN yc END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_avg_yc,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN yc_matches END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_yc_match_pct,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN yc END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_avg_yc,
IFNULL(SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN yc END) / SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN matches END), 0) AS league_avg_yc,

-- Against Yellow Cards (against_yc) metrics
IFNULL(SUM(CASE WHEN season_year = tf_season THEN yc_against_matches END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_yc_against_match_pct,
IFNULL(SUM(CASE WHEN season_year = tf_season THEN yc_against END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_avg_yc_against,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN yc_against_matches END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_yc_against_match_pct,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN yc_against END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_avg_yc_against,
IFNULL(SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN yc_against END) / SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN matches END), 0) AS league_avg_yc_against,

-- Offsides metrics
IFNULL(SUM(CASE WHEN season_year = tf_season THEN offside_matches END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_offsides_match_pct,
IFNULL(SUM(CASE WHEN season_year = tf_season THEN offsides END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_avg_offsides,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN offside_matches END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_offsides_match_pct,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN offsides END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_avg_offsides,
IFNULL(SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN offsides END) / SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN matches END), 0) AS league_avg_offsides,

-- Against Offsides metrics
IFNULL(SUM(CASE WHEN season_year = tf_season THEN against_offside_matches END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_offsides_against_match_pct,
IFNULL(SUM(CASE WHEN season_year = tf_season THEN offsides_against END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_avg_offsides_against,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN against_offside_matches END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_offsides_against_match_pct,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN offsides_against END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_avg_offsides_against,
IFNULL(SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN offsides_against END) / SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN matches END), 0) AS league_avg_offsides_against,

-- Corners metrics
IFNULL(SUM(CASE WHEN season_year = tf_season THEN corner_matches END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_corners_match_pct,
IFNULL(SUM(CASE WHEN season_year = tf_season THEN corners END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_avg_corners,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN corner_matches END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_corners_match_pct,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN corners END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_avg_corners,
IFNULL(SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN corners END) / SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN matches END), 0) AS league_avg_corners,

-- Against Corners metrics
IFNULL(SUM(CASE WHEN season_year = tf_season THEN against_corner_matches END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_against_corners_match_pct,
IFNULL(SUM(CASE WHEN season_year = tf_season THEN corners_against END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_avg_against_corners,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN against_corner_matches END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_against_corners_match_pct,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN corners_against END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_avg_against_corners,
IFNULL(SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN corners_against END) / SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN matches END), 0) AS league_avg_against_corners,

-- Fouls metrics
IFNULL(SUM(CASE WHEN season_year = tf_season THEN fouls END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_avg_fouls,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN fouls END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_avg_fouls,
IFNULL(SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN fouls END) / SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN matches END), 0) AS league_avg_fouls,

-- Against Fouls metrics
IFNULL(SUM(CASE WHEN season_year = tf_season THEN found_rows() END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_avg_against_fouls,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN fouls_drawn END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_avg_against_fouls,
IFNULL(SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN fouls_drawn END) / SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN matches END), 0) AS league_avg_against_fouls,

-- Total Shots metrics
IFNULL(SUM(CASE WHEN season_year = tf_season THEN shots END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_avg_shots,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN shots END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_avg_shots,
IFNULL(SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN shots END) / SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN matches END), 0) AS league_avg_shots,

-- Against Total Shots metrics
IFNULL(SUM(CASE WHEN season_year = tf_season THEN shots_concede END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_avg_against_shots,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN shots_concede END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_avg_against_shots,
IFNULL(SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN shots_concede END) / SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN matches END), 0) AS league_avg_against_shots,

-- Tackles metrics
IFNULL(SUM(CASE WHEN season_year = tf_season THEN tackles END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_avg_tackles,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN tackles END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_avg_tackles,
IFNULL(SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN tackles END) / SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN matches END), 0) AS league_avg_tackles,

-- Against Tackles metrics
IFNULL(SUM(CASE WHEN season_year = tf_season THEN tackles_concede END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_avg_against_tackles,
IFNULL(SUM(CASE WHEN season_year = tf_season - 1 THEN tackles_concede END) / SUM(CASE WHEN season_year = tf_season - 1 THEN matches END), 0) AS py_season_avg_against_tackles,
IFNULL(SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN tackles_concede END) / SUM(CASE WHEN season_year = tf_season AND league_name = tf_league THEN matches END), 0) AS league_avg_against_tackles

FROM teams_base_data
WHERE 1 = 1
GROUP BY 1, 2
;


DROP TABLE IF EXISTS teams_last_5_data
;


CREATE TABLE teams_last_5_data AS
SELECT
team_id,
SUBSTRING_INDEX(GROUP_CONCAT(IFNULL(LEFT(result,1), 0) ORDER BY team_r ASC SEPARATOR '|'), '|', 5) AS last5_results,
SUBSTRING_INDEX(GROUP_CONCAT(IFNULL(team_goals, 0) ORDER BY team_r ASC SEPARATOR '|'), '|', 5) AS last5_goals,
SUBSTRING_INDEX(GROUP_CONCAT(IFNULL(against_team_goals, 0) ORDER BY team_r ASC SEPARATOR '|'), '|', 5) AS last5_goals_against,
SUBSTRING_INDEX(GROUP_CONCAT(IFNULL(btts, 0) ORDER BY team_r ASC SEPARATOR '|'), '|', 5) AS last5_btts,
SUBSTRING_INDEX(GROUP_CONCAT(IFNULL(fouls, 0) ORDER BY team_r ASC SEPARATOR '|'), '|', 5) AS last5_fouls,
SUBSTRING_INDEX(GROUP_CONCAT(IFNULL(against_fouls, 0) ORDER BY team_r ASC SEPARATOR '|'), '|', 5) AS last5_fouls_drawn,
SUBSTRING_INDEX(GROUP_CONCAT(IFNULL(yellow_cards, 0) ORDER BY team_r ASC SEPARATOR '|'), '|', 5) AS last5_yc,
SUBSTRING_INDEX(GROUP_CONCAT(IFNULL(against_yellow_cards, 0) ORDER BY team_r ASC SEPARATOR '|'), '|', 5) AS last5_yc_against,
SUBSTRING_INDEX(GROUP_CONCAT(IFNULL(total_shots, 0) ORDER BY team_r ASC SEPARATOR '|'), '|', 5) AS last5_shots,
SUBSTRING_INDEX(GROUP_CONCAT(IFNULL(against_total_shots, 0) ORDER BY team_r ASC SEPARATOR '|'), '|', 5) AS last5_shots_against,
SUBSTRING_INDEX(GROUP_CONCAT(IFNULL(corner_kicks, 0) ORDER BY team_r ASC SEPARATOR '|'), '|', 5) AS last5_corners,
SUBSTRING_INDEX(GROUP_CONCAT(IFNULL(against_corner_kicks, 0) ORDER BY team_r ASC SEPARATOR '|'), '|', 5) AS last5_corners_against,
SUBSTRING_INDEX(GROUP_CONCAT(IFNULL(offsides, 0) ORDER BY team_r ASC SEPARATOR '|'), '|', 5) AS last5_offsides,
SUBSTRING_INDEX(GROUP_CONCAT(IFNULL(against_offsides, 0) ORDER BY team_r ASC SEPARATOR '|'), '|', 5) AS last5_offsides_against,
SUBSTRING_INDEX(GROUP_CONCAT(IFNULL(tackles, 0) ORDER BY team_r ASC SEPARATOR '|'), '|', 5) AS last5_tackles,
SUBSTRING_INDEX(GROUP_CONCAT(IFNULL(against_tackles, 0) ORDER BY team_r ASC SEPARATOR '|'), '|', 5) AS last5_tackles_against
FROM analytics.fixture_stats_compile
WHERE 1 = 1
AND team_r <= 5
GROUP BY team_id
;


DROP TABLE IF EXISTS master_teams_view
;


CREATE TABLE master_teams_view AS
SELECT DISTINCT
tda.fixture_id,
tda.team_id,
tl5d.last5_results,

-- goals metrics --
tda.season_avg_goals,
tda.py_season_avg_goals,
tl5d.last5_goals,
tda.league_avg_goals,
1 - tda.season_goal_match_pct AS zero_goal_match_pct,
1 - tda.py_season_goal_match_pct AS zero_goal_match_pct_py,
tda.season_avg_goals_against,
tda.py_season_avg_goals_against,
tl5d.last5_goals_against,
tda.league_avg_goals_against,
1 - tda.season_goal_against_match_pct AS zero_goal_against_match_pct,
1 - tda.py_season_goal_against_match_pct AS zero_goal_against_match_pct_py,

-- btts metrics --
tda.season_btts_pct,
tda.py_season_btts_pct,
tl5d.last5_btts,
tda.league_btts_pct,

-- yc metrics --
tda.season_avg_yc,
tda.py_season_avg_yc,
tl5d.last5_yc,
tda.league_avg_yc,
1 - season_yc_match_pct AS zero_card_matches,
1 - py_season_yc_match_pct AS zero_card_matches_py,
tda.season_avg_yc_against,
tda.py_season_avg_yc_against,
tl5d.last5_yc_against,
tda.league_avg_yc_against,
1 - season_yc_against_match_pct AS zero_against_card_matches,
1 - py_season_yc_against_match_pct AS zero_against_card_matches_py,

-- offsides metrics --
tda.season_avg_offsides,
tda.py_season_avg_offsides,
tl5d.last5_offsides,
tda.league_avg_offsides,
1 - tda.season_offsides_match_pct AS zero_offsides_matches,
1 - tda.py_season_offsides_match_pct AS zero_offsides_matches_py,
tda.season_avg_offsides_against,
tda.py_season_avg_offsides_against,
tl5d.last5_offsides_against,
tda.league_avg_offsides_against,
1 - tda.season_offsides_against_match_pct AS zero_against_offsides_matches,
1 - tda.py_season_offsides_against_match_pct AS zero_against_offsides_matches_py,

-- corners metrics --
tda.season_avg_corners,
tda.py_season_avg_corners,
tl5d.last5_corners,
tda.league_avg_corners,
1 - tda.season_corners_match_pct AS zero_corners_matches,
1 - tda.py_season_corners_match_pct AS zero_corners_matches_py,
tda.season_avg_against_corners,
tda.py_season_avg_against_corners,
tl5d.last5_corners_against,
tda.league_avg_against_corners,
1 - tda.season_against_corners_match_pct AS zero_against_corners_matches,
1 - tda.py_season_against_corners_match_pct AS zero_against_corners_matches_py,

-- shots metrics --
tda.season_avg_shots,
tda.py_season_avg_shots,
tl5d.last5_shots,
tda.league_avg_shots,
tda.season_avg_against_shots,
tda.py_season_avg_against_shots,
tl5d.last5_shots_against,
tda.league_avg_against_shots,

-- fouls metrics --
tda.season_avg_fouls,
tda.py_season_avg_fouls,
tl5d.last5_fouls,
tda.league_avg_fouls,
tda.season_avg_against_fouls,
tda.py_season_avg_against_fouls,
tl5d.last5_fouls_drawn,
tda.league_avg_against_fouls,

-- tackles metrics --
tda.season_avg_tackles,
tda.py_season_avg_tackles,
tl5d.last5_tackles,
tda.league_avg_tackles,
tda.season_avg_against_tackles,
tda.py_season_avg_against_tackles,
tl5d.last5_tackles_against,
tda.league_avg_against_tackles
FROM teams_data_agg tda
JOIN teams_last_5_data tl5d on tda.team_id = tl5d.team_id
;
