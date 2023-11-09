DROP TABLE IF EXISTS top_leagues
;

CREATE TABLE top_leagues AS
SELECT league_id,
       COUNT(DISTINCT team_id) AS teams
FROM team_league_season
WHERE 1 = 1
AND ((team_id IN (SELECT home_team_id
                 FROM fixtures
                 WHERE league_id IN (2, 3)
                   AND season_year = 2023)
        OR
     team_id IN (SELECT home_team_id
                 FROM fixtures
                 WHERE league_id IN (1))
    )
         OR
     league_id IN (40, 41, 71, 188, 253))
AND season_year >= 2022
GROUP BY 1
HAVING teams > 2
ORDER BY 2 DESC
;

DROP TABLE IF EXISTS today_fixture
;

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
AND fixture_date BETWEEN CURDATE() AND CURDATE() + INTERVAL 1 DAY
GROUP BY 1
ORDER BY f.timestamp
;


UPDATE today_fixture AS tf
JOIN live_updates.live_fixtures AS lf ON tf.fixture_id = lf.fixture_id
SET tf.referee = lf.referee
WHERE tf.referee IS NULL
;


UPDATE today_fixture AS tf
JOIN cleaned_referees AS cr ON tf.referee = cr.original_referee_name
SET tf.cleaned_referee_name = cr.cleaned_referee_name
WHERE tf.cleaned_referee_name IS NULL
;


DROP TABLE IF EXISTS quicksight.referee_dashboard;


CREATE TABLE quicksight.referee_dashboard
AS
SELECT
tf.fixture_id,
tf.country_name,
tf.name AS league,
tf.fixture_date,
tf.match_time,
tf.fixt,
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
LEFT JOIN master_referee_view mrv on mrv.cleaned_referee_name = tf.cleaned_referee_name
WHERE 1 = 1
# AND tf.cleaned_referee_name IS NOT NULL
# AND LOWER(mrv.cleaned_referee_name) LIKE '%king%'
ORDER BY tf.timestamp, tf.league_id
;


DROP TABLE IF EXISTS quicksight.teams_yc_dashboard;
;


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


DROP TABLE IF EXISTS quicksight.teams_dashboard;
;


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


DROP TABLE IF EXISTS temp.bookmakers_prediction;

CREATE TABLE temp.bookmakers_prediction
AS
SELECT
tf.fixt,
tf.fixture_id,
CASE WHEN LOWER(bet_name) LIKE '%home%' THEN home_team_id
     WHEN LOWER(bet_name) LIKE '%away%' THEN away_team_id
     ELSE 0 END AS team_id,
CASE WHEN LOWER(bet_name) LIKE '%home%' THEN home_team
     WHEN LOWER(bet_name) LIKE '%away%' THEN away_team
     ELSE 'total'END AS team_name,
CASE WHEN LOWER(bet_name) LIKE '%home%' THEN 0
     WHEN LOWER(bet_name) LIKE '%away%' THEN 1
     ELSE 3 END AS is_home,
bet_name,
value_type,
bookmaker_name,
fo.bookmaker_id,
fo.bet_type_id,
odd
FROM fixture_odds fo
JOIN bookmakers b on fo.bookmaker_id = b.bookmaker_id
JOIN today_fixture tf on fo.fixture_id = tf.fixture_id
WHERE 1 = 1
# AND tf.fixture_id = 1035146
AND (bet_type_id IN (80, 82, 83, 150, 151, 153)
         OR (bet_type_id = 86 AND LOWER(value_type) = 'yes')
    )
# AND LOWER(value_type) = 'yes'
# AND fixture_date = CURDATE()
# AND fo.fixture_id =
ORDER BY league_id, match_time, fixt, is_home
;

# SELECT * FROM fixture_odds WHERE bet_type_id = 79;

DROP TABLE IF EXISTS temp.fixture_cards_bookmakers;

CREATE TABLE temp.fixture_cards_bookmakers
AS
SELECT
*,
DENSE_RANK() over (partition by fixture_id order by odd) AS fixture_rnk,
DENSE_RANK() over (partition by fixture_id, is_home order by odd) AS fixture_team_rnk,
DENSE_RANK() over (partition by fixture_id, is_home, bookmaker_name order by odd) AS fixture_team_bookie_rnk
FROM temp.bookmakers_prediction
WHERE 1 = 1
;

DROP TABLE IF EXISTS temp.fixture_cards_bookmakers_summary;

CREATE TABLE temp.fixture_cards_bookmakers_summary
AS
SELECT
fixture_id,
team_id,
fixt,
GROUP_CONCAT(CASE WHEN fixture_team_bookie_rnk = 1 AND bookmaker_name = 'Bet365' THEN CONCAT(value_type, ' (', odd, ')') END SEPARATOR ' | ') AS Bet365,
GROUP_CONCAT(CASE WHEN fixture_team_bookie_rnk = 1 AND bookmaker_name = 'Marathonbet' THEN CONCAT(value_type, ' (', odd, ')') END SEPARATOR  ' | ') AS Marathonbet,
GROUP_CONCAT(CASE WHEN fixture_team_bookie_rnk = 1 AND bookmaker_name = 'Pinnacle' THEN CONCAT(value_type, ' (', odd, ')') END SEPARATOR ' | ') AS Pinnacle
FROM temp.fixture_cards_bookmakers
WHERE 1 = 1
# AND fixture_id = 1035146
GROUP BY 1, 2
;

-- Fixture Q

DROP TABLE IF EXISTS temp.fixture_level_cards_odds;

CREATE TABLE temp.fixture_level_cards_odds
AS
SELECT
f.fixture_id,
f.fixt,
CASE WHEN f.team_id = 0 THEN 'Total' ELSE t.name END AS team,
Bet365,
Marathonbet,
Pinnacle,
CASE WHEN f.team_id = tf.home_team_id THEN 0
     WHEN f.team_id = tf.away_team_id THEN 1
     ELSE 2 END AS tnk
FROM temp.fixture_cards_bookmakers_summary f
JOIN teams t on t.team_id = f.team_id
JOIN today_fixture tf on f.fixture_id = tf.fixture_id
ORDER BY f.fixture_id, tnk
;

DROP TABLE IF EXISTS temp.top_high_voltage;

CREATE TABLE temp.top_high_voltage
AS
SELECT * FROM
(SELECT
DISTINCT fixture_id, fixt, Bet365, Marathonbet, Pinnacle
FROM temp.fixture_level_cards_odds
WHERE 1 = 1
AND team = 'Total' ) AS base
WHERE
1 = 1
AND
(
    (
    (LOWER(Bet365) LIKE '%over 4%' OR LOWER(Bet365) LIKE '%over 5%' OR LOWER(Bet365) LIKE '%over 6%' OR LOWER(Bet365) LIKE '%over 7%')
    OR
    (LOWER(Bet365) LIKE '%under 6%' OR LOWER(Bet365) LIKE '%under 7%' OR LOWER(Bet365) LIKE '%under 8%')
    )
    OR
    (
    (LOWER(Marathonbet) LIKE '%over 4%' OR LOWER(Marathonbet) LIKE '%over 5%' OR LOWER(Marathonbet) LIKE '%over 6%' OR LOWER(Marathonbet) LIKE '%over 7%')
    OR
    (LOWER(Marathonbet) LIKE '%under 6%' OR LOWER(Marathonbet) LIKE '%under 7%' OR LOWER(Marathonbet) LIKE '%under 8%')
    )
    OR
    (
    (LOWER(Pinnacle) LIKE '%over 4%' OR LOWER(Pinnacle) LIKE '%over 5%' OR LOWER(Pinnacle) LIKE '%over 6%' OR LOWER(Pinnacle) LIKE '%over 7%')
    OR
    (LOWER(Pinnacle) LIKE '%under 6%' OR LOWER(Pinnacle) LIKE '%under 7%' OR LOWER(Pinnacle) LIKE '%under 8%')
    )
)
AND (
    LOWER(IFNULL(Bet365, 'aa')) NOT LIKE '%under 3%'
        AND
    LOWER(IFNULL(Bet365, 'aa')) NOT LIKE '%under 4%'
        AND
    LOWER(IFNULL(Pinnacle, 'aa')) NOT LIKE '%under 4%'
        AND
    LOWER(IFNULL(Pinnacle, 'aa')) NOT LIKE '%under 4%'
    )
;

-- referee_q

DROP TABLE IF EXISTS temp.referee_q;

CREATE TABLE temp.referee_q
AS
SELECT
rd.*,
fcbs.Bet365,
fcbs.Marathonbet,
fcbs.Pinnacle,
CASE WHEN thv.fixture_id IS NOT NULL THEN 1 ELSE 0 END AS is_high_voltage
FROM quicksight.referee_dashboard rd
INNER JOIN temp.fixture_cards_bookmakers_summary fcbs
ON rd.fixture_id = fcbs.fixture_id AND fcbs.team_id = 0
LEFT JOIN temp.top_high_voltage thv
ON rd.fixture_id = thv.fixture_id
WHERE 1 = 1
-- AND league = 'UEFA Champions League'
;




-- team_q
DROP TABLE IF EXISTS temp.team_q;

CREATE TABLE temp.team_q
AS
SELECT
tyd.*,
fcbs.Bet365,
fcbs.Marathonbet
FROM
temp.fixture_cards_bookmakers_summary fcbs
JOIN quicksight.teams_dashboard tyd
ON tyd.fixture_id = fcbs.fixture_id AND tyd.team_id = fcbs.team_id;

-- player_q

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

DROP TABLE IF EXISTS temp.player_pre_view;

CREATE TABLE temp.player_pre_view AS
SELECT
DISTINCT
mpv.fixture_id,
tf.fixt,
mpv.player_id,
tf.league_id,
t.name AS team_name,
p.name AS player_name,
mpv.last5_start_foul,
mpv.last5_start_yc,
ps.season_league_cards,
season_avg_fouls,
season_avg_yc,
zero_season_foul_match_pct,
avg_fouls_total,
avg_yc_total,
zero_foul_match_pct,
argue_yc_pct,
tw_yc_pct,
plsd.season_matches,
CASE WHEN plsd.last_start = tlsd.last_start THEN 1 ELSE 0 END AS played_last_game,
plsd.last_start,
i.type,
CASE WHEN LEFT(last5_start_yc, 1) = '1' OR LEFT(last5_yc, 1) = '1' THEN 1 ELSE 0 END AS is_last_yellow
FROM master_players_view mpv
LEFT JOIN today_fixture tf on mpv.fixture_id = tf.fixture_id
JOIN teams t on mpv.team_id = t.team_id
JOIN players p on mpv.player_id = p.player_id
LEFT JOIN injuries i on mpv.player_id = i.player_id AND mpv.fixture_id = i.fixture_id
LEFT JOIN temp.player_last_start_date plsd on mpv.player_id = plsd.player_id
LEFT JOIN temp.team_last_start_date tlsd on mpv.team_id = tlsd.team_id
LEFT JOIN temp.player_suspension ps on mpv.player_id = ps.player_id
WHERE 1 = 1
# AND ((LOWER(last5_start_foul) NOT LIKE '%00%' AND (season_avg_fouls > 1.5 OR avg_yc_total > 0.2))
#            OR
#        (LOWER(last5_start_foul) NOT LIKE '%0%' AND season_avg_yc > 0.23))
AND LENGTH(last5_start_foul) > 4
AND (LOWER(i.type) NOT LIKE '%missing%' OR i.type IS NULL)
# AND LOWER(p.name) NOT LIKE '%can'
# AND i.type IS NULL
AND plsd.last_start > CURDATE() - INTERVAL 20 DAY
ORDER BY fixt, avg_yc_total DESC, zero_foul_match_pct, season_avg_fouls DESC
;

DROP TABLE IF EXISTS temp.player_rnk_view;

CREATE TABLE temp.player_rnk_view AS
SELECT
*,
dense_rank() over (partition by team_name, fixture_id order by argue_yc_pct DESC) AS argue_rnk,
dense_rank() over (partition by team_name, fixture_id order by tw_yc_pct DESC) AS tw_rnk,
dense_rank() over (partition by team_name, fixture_id order by avg_fouls_total DESC) AS fouler_rnk,
dense_rank() over (partition by team_name, fixture_id order by zero_season_foul_match_pct) AS zero_m_rnk,
dense_rank() over (partition by team_name, fixture_id order by avg_yc_total DESC) AS yc_rnk
FROM temp.player_pre_view;

DROP TABLE IF EXISTS temp.base_player_q;

CREATE TABLE temp.base_player_q
AS
SELECT base.*,
       row_number() over (partition by fixture_id order by calc_metric DESC) AS rnk
FROM
(SELECT
DISTINCT
tf.timestamp,
tf.league_id,
pfv.fixture_id,
pfv.fixt,
team_name,
# p_type,
pfv.player_id,
player_name,
last5_start_foul,
last5_start_yc,
argue_yc_pct,
avg_fouls_total,
season_avg_fouls,
zero_foul_match_pct,
zero_season_foul_match_pct,
avg_yc_total,
season_avg_yc,
last_start,
played_last_game,
season_matches,
CASE WHEN thv.fixture_id IS NOT NULL THEN 1 ELSE 0 END AS is_high_voltage,
CASE WHEN lfl.player_id IS NOT NULL THEN 1 ELSE 0 END AS starting_xi,
CASE WHEN lfl.fixture_id IS NOT NULL THEN 1 ELSE 0 END AS is_match_live,
season_league_cards,
CASE WHEN tf.league_id IN (848, 3, 2) AND season_league_cards = 2 THEN ROUND(((avg_yc_total)
                                                                                + (season_avg_yc)
                                                                                + ((avg_fouls_total) / 5)
                                                                                + ((season_avg_fouls) / 5)
                                                                                + (CASE WHEN is_last_yellow = 0 THEN ((season_avg_fouls) / 5) ELSE 0 END)) * (1- zero_foul_match_pct) / 7.5, 2)
     WHEN tf.league_id NOT IN (848, 3, 2) AND season_league_cards IN (4, 9) THEN ROUND(((avg_yc_total)
                                                                                        + (season_avg_yc)
                                                                                        + ((avg_fouls_total) / 5)
                                                                                        + ((season_avg_fouls) / 5)
                                                                                        + (CASE WHEN is_last_yellow = 0 THEN ((season_avg_fouls) / 5) ELSE 0 END)) * (1- zero_foul_match_pct) / 7.5, 2)
      WHEN season_matches > 5 THEN ROUND(((avg_yc_total)
                                            + (season_avg_yc)
                                            + ((avg_fouls_total) / 5)
                                            + ((season_avg_fouls) / 5)
                                            + (CASE WHEN is_last_yellow = 0 THEN ((season_avg_fouls) / 5) ELSE 0 END)) * (1- zero_foul_match_pct) / 5, 2)
     ELSE
        ROUND(((avg_yc_total)
            + ((avg_fouls_total) / 5)
            + (CASE WHEN is_last_yellow = 0 THEN ((avg_yc_total) / 5) ELSE 0 END)) * (1- zero_foul_match_pct) / 3, 2)
     END AS calc_metric
FROM temp.player_rnk_view pfv
LEFT JOIN injuries i on pfv.player_id = i.player_id
AND pfv.fixture_id = i.fixture_id
LEFT JOIN today_fixture tf on pfv.fixture_id = tf.fixture_id
LEFT JOIN temp.top_high_voltage thv on pfv.fixture_id = thv.fixture_id
LEFT JOIN live_updates.live_fixture_lineups lfl
    on pfv.fixture_id = lfl.fixture_id AND pfv.player_id = lfl.player_id
WHERE 1 = 1
AND last5_start_foul NOT LIKE '%00%'
# AND LEFT(last5_start_yc, 1) NOT LIKE '1'
AND (avg_fouls_total > 1.01 OR season_avg_fouls > 1.3)
AND (last_start > CURDATE() - INTERVAL 10 DAY OR i.type IS NULL)
# AND player_name = 'N. Amrabat'
)AS base
ORDER BY  league_id, fixture_id, rnk
;



DROP TABLE IF EXISTS temp.player_q;

CREATE TABLE temp.player_q
AS
SELECT
CONCAT(fixt,rnk) AS f_rnk,
player_name,
CONCAT(last5_start_foul,'-') AS last5_start_foul,
CONCAT(last5_start_yc, '-') AS last5_start_yc,
team_name,
calc_metric,
season_league_cards,
# p_type,
season_matches,
season_avg_fouls,
season_avg_yc,
avg_fouls_total,
avg_yc_total,
played_last_game,
last_start,
argue_yc_pct,
is_high_voltage,
is_match_live,
starting_xi,
fixture_id
FROM temp.base_player_q
WHERE 1 = 1
AND fixt IS NOT NULL
AND is_match_live = 1
AND is_high_voltage = 1
AND starting_xi = 1
AND rnk < 7
ORDER BY  timestamp, league_id, fixture_id, rnk
;

INSERT INTO temp.player_q
SELECT
CONCAT(fixt,rnk) AS f_rnk,
player_name,
CONCAT(last5_start_foul,'-') AS last5_start_foul,
CONCAT(last5_start_yc, '-') AS last5_start_yc,
team_name,
calc_metric,
season_league_cards,
# p_type,
season_matches,
season_avg_fouls,
season_avg_yc,
avg_fouls_total,
avg_yc_total,
played_last_game,
last_start,
argue_yc_pct,
is_high_voltage,
is_match_live,
starting_xi,
fixture_id
FROM temp.base_player_q
WHERE 1 = 1
AND fixt IS NOT NULL
AND is_match_live = 1
AND is_high_voltage = 0
AND starting_xi = 1
AND rnk < 7
AND calc_metric >= 0.15
AND fixture_id NOT IN (SELECT fixture_id FROM temp.player_q)
ORDER BY  timestamp, league_id, fixture_id, rnk
;

INSERT INTO temp.player_q
SELECT
CONCAT(fixt,rnk) AS f_rnk,
player_name,
CONCAT(last5_start_foul,'-') AS last5_start_foul,
CONCAT(last5_start_yc, '-') AS last5_start_yc,
team_name,
calc_metric,
season_league_cards,
# p_type,
season_matches,
season_avg_fouls,
season_avg_yc,
avg_fouls_total,
avg_yc_total,
played_last_game,
last_start,
argue_yc_pct,
is_high_voltage,
is_match_live,
starting_xi,
fixture_id
FROM temp.base_player_q
WHERE 1 = 1
AND fixt IS NOT NULL
AND is_match_live = 0
AND is_high_voltage = 1
# AND starting_xi = 1
AND rnk < 7
# AND calc_metric > 0.2
AND fixture_id NOT IN (SELECT fixture_id FROM temp.player_q)
ORDER BY  timestamp, league_id, fixture_id, rnk
;

INSERT INTO temp.player_q
SELECT
CONCAT(fixt,rnk) AS f_rnk,
player_name,
CONCAT(last5_start_foul,'-') AS last5_start_foul,
CONCAT(last5_start_yc, '-') AS last5_start_yc,
team_name,
calc_metric,
season_league_cards,
# p_type,
season_matches,
season_avg_fouls,
season_avg_yc,
avg_fouls_total,
avg_yc_total,
played_last_game,
last_start,
argue_yc_pct,
is_high_voltage,
is_match_live,
starting_xi,
fixture_id
FROM temp.base_player_q
WHERE 1 = 1
AND fixt IS NOT NULL
AND is_match_live = 0
AND is_high_voltage = 0
# AND starting_xi = 1
AND rnk < 7
AND calc_metric >= 0.15
AND fixture_id NOT IN (SELECT fixture_id FROM temp.player_q)
ORDER BY  timestamp, league_id, fixture_id, rnk
;