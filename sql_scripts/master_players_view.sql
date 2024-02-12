-- Country Filter --

UPDATE analytics.fixture_player_stats_compile fpsc
SET nationality = 'Turkey'
WHERE nationality = 'Türkiye'
;

UPDATE players p
SET nationality = 'Turkey'
WHERE nationality = 'Türkiye'
;

UPDATE analytics.fixture_player_stats_compile fpsc
SET nationality = 'Ivory Coast'
WHERE nationality =  'Côte d''Ivoire'
;

UPDATE players p
SET nationality = 'Ivory Coast'
WHERE nationality =  'Côte d''Ivoire'
;

DROP TABLE IF EXISTS country_code;

CREATE TABLE country_code AS
SELECT
team_id AS country_id, team_name AS country
FROM analytics.fixture_player_stats_compile fpsc
WHERE team_name = nationality
GROUP BY 1
;

DROP TABLE IF EXISTS players_country;

CREATE TABLE players_country AS
SELECT *,
       0 AS is_new
       FROM
(SELECT player_id, nationality AS country, team_id AS country_id, season_year,
   ROW_NUMBER() over (partition by player_id ORDER BY fixture_date DESC) AS r
FROM analytics.fixture_player_stats_compile fpsc
WHERE team_name = nationality
)A
WHERE 1 = 1
AND r = 1
AND season_year > YEAR(current_date) - 5
;

INSERT INTO players_country
SELECT
fpsc.player_id,
c.country,
c.country_id,
MAX(season_year) AS season_year,
1 AS rnk,
1 AS is_new
FROM
analytics.fixture_player_stats_compile fpsc
JOIN country_code c on LOWER(fpsc.nationality) = LOWER(c.country)
WHERE 1 = 1
AND fpsc.player_id NOT IN (SELECT player_id FROM players_country)
GROUP BY 1, 2, 3
HAVING season_year > YEAR(current_date) - 2
;


DROP TABLE IF EXISTS players_latest_club
;

CREATE TABLE players_latest_club AS
SELECT * FROM
(SELECT player_id, team_name, team_id, season_year,
   ROW_NUMBER() over (partition by player_id ORDER BY fixture_date DESC) AS r
FROM analytics.fixture_player_stats_compile
WHERE team_name <> nationality
)A
WHERE 1 = 1
AND r = 1
AND season_year > YEAR(current_date) - 3
;

DROP TABLE IF EXISTS players_next_fixtures
;

CREATE TABLE players_next_fixtures AS
SELECT
plc.player_id,
plc.team_id,
tf.fixture_id,
tf.fixture_date,
0 AS is_new
FROM players_latest_club plc
JOIN today_fixture tf on plc.team_id = tf.home_team_id
GROUP BY 1
;

INSERT INTO players_next_fixtures
SELECT
plc.player_id,
plc.team_id,
tf.fixture_id,
tf.fixture_date,
0 AS is_new
FROM players_latest_club plc
JOIN today_fixture tf on plc.team_id = tf.away_team_id
GROUP BY 1
;

INSERT INTO players_next_fixtures
SELECT
pc.player_id,
pc.country_id,
tf.fixture_id,
tf.fixture_date,
is_new
FROM players_country pc
JOIN today_fixture tf on pc.country_id = tf.home_team_id
GROUP BY 1
;

INSERT INTO players_next_fixtures
SELECT
pc.player_id,
pc.country_id,
tf.fixture_id,
tf.fixture_date,
is_new
FROM players_country pc
JOIN today_fixture tf on pc.country_id = tf.away_team_id
GROUP BY 1
;

DROP TABLE IF EXISTS players_upcoming_fixture
;

CREATE TABLE players_upcoming_fixture
AS
SELECT
base.player_id,
base.team_id,
base.fixture_id,
base.fixture_date,
base.is_new
FROM
(SELECT
*,
ROW_NUMBER() over (partition by player_id order by fixture_date) AS prk
FROM players_next_fixtures) AS base
WHERE prk = 1
# GROUP BY player_id
;

DROP TABLE IF EXISTS players_last_5_data
;


CREATE TABLE players_last_5_data AS
SELECT
player_id,
GROUP_CONCAT(CASE WHEN is_substitute = 0 AND player_rnk_sub <= 5 THEN IFNULL(goals, 0) END ORDER BY fixture_date DESC SEPARATOR '') AS last5_start_goal,
GROUP_CONCAT(CASE WHEN is_substitute = 0 AND player_rnk_sub <= 5 THEN IFNULL(fouls_committed, 0) END ORDER BY fixture_date DESC SEPARATOR '') AS last5_start_foul,
GROUP_CONCAT(CASE WHEN is_substitute = 0 AND player_rnk_sub <= 5 THEN IFNULL(fouls_drawn, 0) END ORDER BY fixture_date DESC SEPARATOR '') AS last5_start_fouls_drawn,
REPLACE(
    SUBSTRING_INDEX(
        GROUP_CONCAT(
            CASE WHEN is_substitute = 1 AND (IFNULL(minutes_played,0) > 5 OR IFNULL(fouls_committed, 0) > 0) THEN IFNULL(fouls_committed, 0) END ORDER BY fixture_date DESC
        ),
        ',', 5
    ),
    ',',
    ''
) AS last5_sub_foul,
REPLACE(
    SUBSTRING_INDEX(
        GROUP_CONCAT(
            CASE WHEN is_substitute = 1 AND (IFNULL(minutes_played,0) > 5 OR IFNULL(fouls_committed, 0) > 0) AND LEFT(result, 1) = 'W' THEN IFNULL(fouls_committed, 0) END ORDER BY fixture_date DESC
        ),
        ',', 5
    ),
    ',',
    ''
) AS last5_win_sub_foul,
REPLACE(
    SUBSTRING_INDEX(
        GROUP_CONCAT(
            CASE WHEN is_substitute = 1 AND (IFNULL(minutes_played,0) > 5 OR IFNULL(fouls_committed, 0) > 0) AND LEFT(result, 1) = 'L' THEN IFNULL(fouls_committed, 0) END ORDER BY fixture_date DESC
        ),
        ',', 5
    ),
    ',',
    ''
) AS last5_loss_sub_foul,
REPLACE(
    SUBSTRING_INDEX(
        GROUP_CONCAT(
            CASE WHEN is_substitute = 1 AND (IFNULL(minutes_played,0) > 5 OR IFNULL(fouls_committed, 0) > 0) AND LEFT(result, 1) = 'D' THEN IFNULL(fouls_committed, 0) END ORDER BY fixture_date DESC
        ),
        ',', 5
    ),
    ',',
    ''
) AS last5_draw_sub_foul,
GROUP_CONCAT(CASE WHEN is_substitute = 0 AND player_rnk_sub <= 5 THEN IFNULL(minutes_played, 0) END ORDER BY fixture_date DESC SEPARATOR '|') AS last5_start_mins,
REPLACE(
    SUBSTRING_INDEX(
        GROUP_CONCAT(
            CASE WHEN is_substitute = 1 AND (IFNULL(minutes_played,0) > 5 OR IFNULL(fouls_committed, 0) > 0) THEN IFNULL(minutes_played, 0) END ORDER BY fixture_date DESC
        ),
        ',', 5
    ),
    ',',
    '|'
) AS last5_sub_mins,
GROUP_CONCAT(CASE WHEN is_substitute = 0 AND player_rnk_sub <= 5 THEN IFNULL(LEFT(result,1), 0) END ORDER BY fixture_date DESC SEPARATOR '|') AS last5_start_result,
        REPLACE(
    SUBSTRING_INDEX(
        GROUP_CONCAT(
            CASE WHEN is_substitute = 1 AND (IFNULL(minutes_played,0) > 5 OR IFNULL(fouls_committed, 0) > 0) THEN IFNULL(LEFT(result,1), 0) END ORDER BY fixture_date DESC
        ),
        ',', 5
    ),
    ',',
    '|'
) AS last5_sub_result,
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
REPLACE(
    SUBSTRING_INDEX(
        GROUP_CONCAT(CASE WHEN is_substitute = 1 AND (IFNULL(minutes_played,0) > 5 OR IFNULL(fouls_committed, 0) > 0) THEN
    CASE
        WHEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) > 1 THEN '1'
        ELSE CAST(IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) AS CHAR)
    END
END ORDER BY fixture_date DESC),
        ',', 5
    ),
    ',',
    ''
) AS last5_sub_yc,
GROUP_CONCAT(CASE WHEN player_rnk <= 5 THEN
CASE
    WHEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) > 1 THEN '1'
    ELSE CAST(IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) AS CHAR)
END
END ORDER BY fixture_date DESC SEPARATOR '') AS last5_yc,
GROUP_CONCAT(CASE WHEN player_rnk <= 5 THEN minutes_played END ORDER BY fixture_date DESC SEPARATOR '|') AS last5_mins,
GROUP_CONCAT(CASE WHEN player_rnk <= 5 THEN is_substitute END ORDER BY fixture_date DESC SEPARATOR '') AS last5_subs
FROM analytics.fixture_player_stats_compile
WHERE 1 = 1
AND player_rnk_sub <= 100
# AND player_id = 919
GROUP BY player_id
;


DROP TABLE IF EXISTS players_base_data
;


CREATE TABLE players_base_data AS
SELECT
fpsc.player_id,
fpsc.player_name,
fpsc.is_substitute,
tf.fixture_id,
tf.season_year AS tf_season,
puf.team_id AS tf_team,
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
COUNT(DISTINCT CASE WHEN IFNULL(fouls_drawn,0) > 0 THEN fpsc.fixture_id END) AS foul_drawn_matches,
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
LEFT JOIN players_upcoming_fixture puf
ON fpsc.player_id = puf.player_id
INNER JOIN today_fixture tf on puf.team_id = tf.home_team_id
WHERE 1 = 1
AND league_name IS NOT NULL
AND fpsc.player_id <> 0
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
HAVING matches > 1
;

INSERT INTO players_base_data
SELECT
fpsc.player_id,
fpsc.player_name,
fpsc.is_substitute,
tf.fixture_id,
tf.season_year AS tf_season,
puf.team_id AS tf_team,
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
COUNT(DISTINCT CASE WHEN IFNULL(fouls_drawn,0) > 0 THEN fpsc.fixture_id END) AS foul_drawn_matches,
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
LEFT JOIN players_upcoming_fixture puf
ON fpsc.player_id = puf.player_id
INNER JOIN today_fixture tf on puf.team_id = tf.away_team_id
WHERE 1 = 1
AND league_name IS NOT NULL
AND fpsc.player_id <> 0
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
HAVING matches > 1
;


INSERT INTO players_base_data
SELECT
fpsc.player_id,
fpsc.player_name,
fpsc.is_substitute,
0 AS fixture_id,
max_season AS tf_season,
puf.team_id AS tf_team,
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
COUNT(DISTINCT CASE WHEN IFNULL(fouls_drawn,0) > 0 THEN fpsc.fixture_id END) AS foul_drawn_matches,
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
LEFT JOIN players_upcoming_fixture puf
ON fpsc.player_id = puf.player_id
WHERE 1 = 1
AND league_name IS NOT NULL
AND fpsc.player_id <> 0
AND fpsc.player_id NOT IN (SELECT player_id FROM players_base_data)
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
HAVING matches > 1
;



DROP TABLE IF EXISTS players_data_agg
;


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
IFNULL(SUM(CASE WHEN is_substitute = 0 THEN foul_drawn_matches END) / SUM(CASE WHEN is_substitute = 0 THEN matches END), 0) AS foul_drawn_match_pct,
IFNULL(SUM(CASE WHEN is_substitute = 0 THEN fouls_drawn END) / SUM(CASE WHEN is_substitute = 0 THEN matches END), 0) AS avg_fouls_drawn_total,
IFNULL(SUM(CASE WHEN is_substitute = 0 THEN card END) / SUM(CASE WHEN is_substitute = 0 THEN matches END), 0) AS avg_yc_total,
IFNULL(SUM(CASE WHEN fouls > 0 AND is_substitute = 0 AND season_year = tf_season THEN fouled_matches END) / SUM(CASE WHEN is_substitute = 0 AND season_year = tf_season THEN matches END), 0) AS season_foul_match_pct,
IFNULL(SUM(CASE WHEN fouls > 0 AND is_substitute = 0 AND season_year = tf_season THEN fouls END) / SUM(CASE WHEN is_substitute = 0 AND season_year = tf_season THEN matches END), 0) AS season_avg_fouls,
IFNULL(SUM(CASE WHEN fouls > 0 AND is_substitute = 0 AND season_year = tf_season THEN foul_drawn_matches END) / SUM(CASE WHEN is_substitute = 0 AND season_year = tf_season THEN matches END), 0) AS season_foul_drawn_match_pct,
IFNULL(SUM(CASE WHEN fouls > 0 AND is_substitute = 0 AND season_year = tf_season THEN fouls_drawn END) / SUM(CASE WHEN is_substitute = 0 AND season_year = tf_season THEN matches END), 0) AS season_avg_fouls_drawn,
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
IFNULL(SUM(CASE WHEN tackles > 0 AND is_substitute = 0 AND season_year = tf_season THEN tackles END) / SUM(CASE WHEN is_substitute = 0 AND season_year = tf_season THEN matches END), 0) AS season_avg_tackles,

-- Cards Extra Metrics
IFNULL(SUM(IFNULL(argue_yc,0)) / SUM((IFNULL(argue_yc,0) + IFNULL(tw_yc,0) + IFNULL(foul_yc,0) + IFNULL(hand_yc,0))), 0) AS argue_yc_pct,
IFNULL(SUM(IFNULL(tw_yc,0)) / SUM((IFNULL(argue_yc,0) + IFNULL(tw_yc,0) + IFNULL(foul_yc,0) + IFNULL(hand_yc,0))), 0) AS tw_yc_pct,
IFNULL(SUM(IFNULL(`00-30`,0)) / SUM((IFNULL(`00-30`,0) + IFNULL(`31-45`,0) + IFNULL(`46-75`,0) + IFNULL(`76-90`,0))), 0) AS r_0_30_yc_pct,
IFNULL(SUM(IFNULL(`31-45`,0)) / SUM((IFNULL(`00-30`,0) + IFNULL(`31-45`,0) + IFNULL(`46-75`,0) + IFNULL(`76-90`,0))), 0) AS r_31_45_yc_pct,
IFNULL(SUM(IFNULL(`46-75`,0)) / SUM((IFNULL(`00-30`,0) + IFNULL(`31-45`,0) + IFNULL(`46-75`,0) + IFNULL(`76-90`,0))), 0) AS r_46_75_yc_pct,
IFNULL(SUM(IFNULL(`76-90`,0)) / SUM((IFNULL(`00-30`,0) + IFNULL(`31-45`,0) + IFNULL(`46-75`,0) + IFNULL(`76-90`,0))), 0) AS r_76_90_yc_pct


FROM players_base_data pbd
INNER JOIN players_last_5_data pl5d
ON pbd.player_id = pl5d.player_id
WHERE 1 = 1
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
;


DROP TABLE IF EXISTS master_players_view
;

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
1 - pda.season_foul_match_pct AS zero_season_foul_match_pct,
pda.avg_fouls_drawn_total,
pda.season_avg_fouls_drawn,
pl5d.last5_start_fouls_drawn,
1 - pda.foul_drawn_match_pct AS zero_foul_drawn_match_pct,
1 - pda.season_foul_drawn_match_pct AS zero_season_foul_drawn_match_pct,
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
pl5d.last5_start_result,
pl5d.last5_yc,
pl5d.last5_mins,
pl5d.last5_subs,
pda.argue_yc_pct,
pda.tw_yc_pct,
pda.r_0_30_yc_pct,
pda.r_31_45_yc_pct,
pda.r_46_75_yc_pct,
pda.r_76_90_yc_pct

FROM players_data_agg pda
JOIN players_last_5_data pl5d on pda.player_id = pl5d.player_id
;

-- Foulers

DROP TABLE IF EXISTS temp.legendary_sub_foulers;

CREATE TABLE temp.legendary_sub_foulers
AS
SELECT
player_id,
'Sub Fouler - Legend' AS type
FROM master_players_view
WHERE 1 = 1
AND LOWER(last5_sub_foul) NOT LIKE '%0%'
AND LENGTH(last5_sub_foul) > 3
GROUP BY 1
;

INSERT INTO temp.legendary_sub_foulers
SELECT
player_id,
'Sub Fouler - Miss_1' AS type
FROM master_players_view
WHERE 1 = 1
AND LOWER(last5_sub_foul) NOT LIKE '%00%'
AND LEFT(last5_sub_foul, 2) NOT LIKE '%0%'
AND LENGTH(last5_sub_foul) > 3
AND player_id NOT IN (SELECT player_id FROM temp.legendary_sub_foulers)
GROUP BY 1
;

INSERT INTO temp.legendary_sub_foulers
SELECT
player_id,
'Sub Fouler - Win' AS type
FROM master_players_view
WHERE 1 = 1
AND (
            LOWER(last5_win_sub_foul) NOT LIKE '%0%'
    )
AND LENGTH(last5_sub_foul) > 3
AND player_id NOT IN (SELECT player_id FROM temp.legendary_sub_foulers)
GROUP BY 1
;


INSERT INTO temp.legendary_sub_foulers
SELECT
player_id,
'Sub Fouler - Draw' AS type
FROM master_players_view
WHERE 1 = 1
AND (
            LOWER(last5_draw_sub_foul) NOT LIKE '%0%'
    )
AND LENGTH(last5_sub_foul) > 3
AND player_id NOT IN (SELECT player_id FROM temp.legendary_sub_foulers)
GROUP BY 1
;


INSERT INTO temp.legendary_sub_foulers
SELECT
player_id,
'Sub Fouler - Loss' AS type
FROM master_players_view
WHERE 1 = 1
AND (
            LOWER(last5_loss_sub_foul) NOT LIKE '%0%'
    )
AND LENGTH(last5_sub_foul) > 3
AND player_id NOT IN (SELECT player_id FROM temp.legendary_sub_foulers)
GROUP BY 1
;

DROP TABLE IF EXISTS temp.legendary_start_foulers;

CREATE TABLE temp.legendary_start_foulers
AS
SELECT
player_id,
'Start Fouler - Legend' AS type
FROM master_players_view
WHERE 1 = 1
AND LOWER(last5_start_foul) NOT LIKE '%0%'
AND LENGTH(last5_start_foul) > 3
AND (avg_fouls_total > 1 OR season_avg_fouls > 1)
GROUP BY 1
;

INSERT INTO temp.legendary_start_foulers
SELECT
player_id,
'Start Fouler - Miss_1' AS type
FROM master_players_view
WHERE 1 = 1
AND LOWER(last5_start_foul) NOT LIKE '%00%'
AND LEFT(last5_start_foul, 2) NOT LIKE '%0%'
AND (avg_fouls_total > 1 OR season_avg_fouls > 1)
AND LENGTH(last5_start_foul) > 3
AND player_id NOT IN (SELECT player_id FROM temp.legendary_start_foulers)
GROUP BY 1
;

-- Other Player level metrics

DROP TABLE IF EXISTS temp.player_last_start_date;

CREATE TABLE temp.player_last_start_date
AS
SELECT fpsc.player_id,
       max(fixture_date) AS last_start,
       COUNT(DISTINCT CASE WHEN is_substitute = 0 AND season_year = max_p.max_season THEN fixture_id END) AS season_matches
FROM analytics.fixture_player_stats_compile fpsc
    JOIN (SELECT player_id, MAX(season_year) AS max_season
          FROM analytics.fixture_player_stats_compile
          GROUP BY player_id) max_p
ON fpsc.player_id = max_p.player_id
WHERE 1 = 1
AND is_substitute = 0
AND fpsc.player_id <> 0
GROUP BY 1
;

DROP TABLE IF EXISTS temp.team_last_start_date;

CREATE TABLE temp.team_last_start_date
AS
SELECT team_id,
       max(fixture_date) AS last_start
FROM analytics.fixture_player_stats_compile
WHERE 1 = 1
AND is_substitute = 0
GROUP BY 1
;

DROP TABLE IF EXISTS temp.player_suspension;

CREATE TABLE temp.player_suspension
AS
SELECT fpsc.player_id,
       COUNT(DISTINCT CASE WHEN fpsc.league_id = f.league_id AND fpsc.season_year = f.season_year AND IFNULL(cards_yellow,0) THEN fpsc.fixture_id END) AS season_league_cards
FROM analytics.fixture_player_stats_compile fpsc
INNER JOIN master_players_view mpv on fpsc.player_id = mpv.player_id
JOIN fixtures f on mpv.fixture_id = f.fixture_id
WHERE 1 = 1
# AND is_substitute = 0
GROUP BY 1
;

DROP TABLE IF EXISTS temp.exp_fyc_model;

CREATE TABLE temp.exp_fyc_model AS
SELECT
fpsc.player_id,
COUNT(DISTINCT fpsc.fixture_id) AS total_matches,
COUNT(DISTINCT CASE WHEN fpsc.season_year = max_season THEN fpsc.fixture_id END) AS season_matches,
COUNT(DISTINCT CASE WHEN IFNULL(cards_yellow,0) + IFNULL(cards_red,0) > 0 THEN fpsc.fixture_id END) AS yc_matches,
COUNT(DISTINCT CASE WHEN IFNULL(cards_yellow,0) + IFNULL(cards_red,0) > 0 AND (LOWER(card_reason) NOT LIKE '%wasting%' AND LOWER(card_reason) NOT LIKE '%argu%') THEN fpsc.fixture_id END) AS yc_w_foul_matches,
COUNT(DISTINCT CASE WHEN IFNULL(fouls_committed,0) > 0 THEN fpsc.fixture_id END) AS foul_matches,
SUM(IFNULL(fouls_committed, 0)) AS fouls
FROM analytics.fixture_player_stats_compile fpsc
INNER JOIN (SELECT player_id, MAX(season_year) AS max_season FROM analytics.fixture_player_stats_compile GROUP BY 1) AS mx
ON fpsc.player_id = mx.player_id
WHERE 1 = 1
AND is_substitute = 0
# AND fpsc.player_id IN (SELECT player_id FROM master_players_view WHERE fixture_id IS NOT NULL AND fixture_id <> 0)
# AND (tf.country_name = 'England' OR tf2.country_name = 'England')
GROUP BY 1
;

DROP TABLE IF EXISTS temp.players_ht_fouls;

CREATE TABLE temp.players_ht_fouls
SELECT
fpsc.player_id,
SUM(CASE WHEN minutes_played IS NOT NULL THEN fixture_id END) AS total_fixt,
SUM(CASE WHEN minutes_played IS NOT NULL THEN IFNULL(fouls_committed, 0) END) AS total_fouls,
SUM(CASE WHEN minutes_played IS NOT NULL THEN IFNULL(fouls_drawn, 0) END) AS total_fouls_drawn,
SUM(CASE WHEN minutes_played IS NOT NULL THEN IFNULL(minutes_played, 0) END) AS total_mins,
SUM(CASE WHEN season_year = mx.mx_year AND minutes_played IS NOT NULL THEN fixture_id END) AS season_fixt,
SUM(CASE WHEN season_year = mx.mx_year AND minutes_played IS NOT NULL THEN IFNULL(fouls_committed, 0) END) AS season_fouls,
SUM(CASE WHEN season_year = mx.mx_year AND minutes_played IS NOT NULL THEN IFNULL(fouls_drawn, 0) END) AS season_fouls_drawn,
SUM(CASE WHEN season_year = mx.mx_year AND minutes_played IS NOT NULL THEN IFNULL(minutes_played, 0) END) AS season_mins
FROM analytics.fixture_player_stats_compile fpsc
INNER JOIN (SELECT player_id, MAX(season_year) AS mx_year
            FROM analytics.fixture_player_stats_compile
            WHERE 1 = 1
            AND season_year <= YEAR(curdate())
            GROUP BY 1
            )AS mx
ON fpsc.player_id = mx.player_id
WHERE 1 = 1
AND is_substitute = 0
AND season_year > 2020
GROUP BY 1;

DROP TABLE IF EXISTS temp.exp_ht_fouls;

CREATE TABLE temp.exp_ht_fouls
SELECT
phf.*,
SUM(total_fouls) * 40   / SUM(total_mins) AS total_exp_ht_fouls,
SUM(season_fouls) * 40 / SUM(season_mins) AS season_exp_ht_fouls,
SUM(total_fouls_drawn) * 40   / SUM(total_mins) AS total_exp_ht_fouls_drawn,
SUM(season_fouls_drawn) * 40 / SUM(season_mins) AS season_exp_ht_fouls_drawn
FROM temp.players_ht_fouls phf
# JOIN master_players_view mpv on phf.player_id = mpv.player_id
# WHERE LENGTH(mpv.fixture_id) > 4
GROUP BY 1
;

-- Shots FFH

DROP TABLE IF EXISTS temp.player_ht_shots;


CREATE TABLE temp.player_ht_shots AS (
    SELECT
        fpsc.player_id,
        SUM(CASE WHEN minutes_played IS NOT NULL THEN fixture_id END) AS total_fixt,
        SUM(CASE WHEN minutes_played IS NOT NULL THEN IFNULL(shots_total, 0) END) AS total_shots,
        SUM(CASE WHEN minutes_played IS NOT NULL THEN IFNULL(minutes_played, 0) END) AS total_mins,
        SUM(CASE WHEN season_year = mx.mx_year AND minutes_played IS NOT NULL THEN fixture_id END) AS season_fixt,
        SUM(CASE WHEN season_year = mx.mx_year AND minutes_played IS NOT NULL THEN IFNULL(shots_total, 0) END) AS season_shots,
        SUM(CASE WHEN season_year = mx.mx_year AND minutes_played IS NOT NULL THEN IFNULL(minutes_played, 0) END) AS season_mins
    FROM analytics.fixture_player_stats_compile fpsc
    INNER JOIN (
        SELECT player_id, MAX(season_year) AS mx_year
        FROM analytics.fixture_player_stats_compile
        WHERE 1 = 1
        AND season_year <= YEAR(curdate())
        GROUP BY 1
    ) AS mx
    ON fpsc.player_id = mx.player_id
    WHERE 1 = 1
    AND is_substitute = 0
    AND season_year > 2020
    GROUP BY 1
);

DROP TABLE IF EXISTS temp.exp_ht_shots;

CREATE TABLE temp.exp_ht_shots
 AS (
    SELECT
        player_id,
        SUM(total_shots) * 40 / SUM(total_mins) AS total_exp_ht_shots,
        SUM(season_shots) * 40 / SUM(season_mins) AS season_exp_ht_shots
    FROM temp.player_ht_shots
    GROUP BY 1
);
