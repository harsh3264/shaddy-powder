
DROP TABLE IF EXISTS referee_base_data
;

CREATE TABLE referee_base_data AS
SELECT
    fpsc.cleaned_referee_name,
    tf.fixture_id,
    tf.fixt,
    COALESCE(tf.season_year, mx.max_season) AS tf_season,
    tf.match_time,
    tf.name AS tf_league,
    fpsc.league_name,
    fpsc.season_year,
    COUNT(DISTINCT fpsc.fixture_id) AS matches,
    SUM(fouls) AS fouls,
    0 AS '00-30',
    0 AS '31-45',
    0 AS '46-75',
    0 AS '76-90',
    SUM(IFNULL(yellow_cards , 0)) AS total_yc,
    COUNT(DISTINCT CASE WHEN IFNULL(yellow_cards, 0) + IFNULL(against_yellow_cards,0) + IFNULL(red_cards, 0) + IFNULL(red_cards,0) = 0 THEN fpsc.fixture_id END) AS 0_card_matches,
    SUM(IFNULL(red_cards , 0)) AS total_rc,
    0 AS 'foul_yc',
    0 AS 'argue_yc',
    0 AS 'tw_yc'
FROM analytics.fixture_stats_compile fpsc
LEFT JOIN today_fixture tf on fpsc.cleaned_referee_name = tf.cleaned_referee_name
LEFT JOIN (SELECT cleaned_referee_name, MAX(season_year) AS max_season
           FROM analytics.fixture_stats_compile GROUP BY 1) AS mx
ON fpsc.cleaned_referee_name = mx.cleaned_referee_name
WHERE 1 = 1
AND league_name IS NOT NULL
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
HAVING matches >= 1
;


DROP TABLE IF EXISTS referee_behaviour
;

CREATE TABLE referee_behaviour
AS
SELECT
    cr.cleaned_referee_name,
    season_year,
    league_name,
    SUM(CASE WHEN card_minute < 31 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '00-30',
    SUM(CASE WHEN card_minute BETWEEN 31 AND 45 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '31-45',
    SUM(CASE WHEN card_minute BETWEEN 46 AND 75 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '46-75',
    SUM(CASE WHEN card_minute BETWEEN 76 AND 90 THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS '76-90',
    SUM(CASE WHEN lower(card_reason) like '%foul%' OR lower(card_reason) like '%handball%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'foul_yc',
    SUM(CASE WHEN lower(card_reason) like '%argument%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'argue_yc',
    SUM(CASE WHEN lower(card_reason) like '%wasting%' THEN IFNULL(cards_yellow, 0) + IFNULL(cards_red, 0) END) AS 'tw_yc'
FROM analytics.fixture_player_stats_compile fpsc
LEFT JOIN cleaned_referees cr
ON fpsc.referee = cr.original_referee_name
GROUP BY 1, 2, 3
;

UPDATE referee_base_data AS rbd
JOIN referee_behaviour AS rb ON rbd.cleaned_referee_name = rb.cleaned_referee_name
AND rbd.season_year = rb.season_year AND rbd.league_name = rb.league_name
SET rbd.`00-30` = IFNULL(rb.`00-30`, 0),
    rbd.`31-45` = IFNULL(rb.`31-45`, 0),
    rbd.`46-75` = IFNULL(rb.`46-75`, 0),
    rbd.`76-90` = IFNULL(rb.`76-90`, 0),
    rbd.foul_yc = IFNULL(rb.foul_yc, 0),
    rbd.argue_yc = IFNULL(rb.argue_yc, 0),
    rbd.tw_yc = IFNULL(rb.tw_yc, 0)
WHERE 1 = 1;
;

DROP TABLE IF EXISTS referee_data_agg
;

CREATE TABLE referee_data_agg AS
SELECT
rbd.fixture_id,
rbd.cleaned_referee_name,
IFNULL(SUM(matches), 0) AS total_matches,
IFNULL(SUM(CASE WHEN fouls > 0 THEN fouls END) / SUM(CASE WHEN fouls > 0 THEN total_yc END), 0) AS fouls_per_yc,
IFNULL(SUM(CASE WHEN fouls > 0 THEN fouls END) / SUM(CASE WHEN fouls > 0 THEN matches END), 0) AS ref_avg_fouls,
IFNULL(SUM(argue_yc) / SUM(total_yc), 0) AS argue_yc_pct,
IFNULL(SUM(tw_yc) / SUM(matches), 0) AS tw_yc_pct,
IFNULL(SUM(total_yc) / SUM(matches), 0) AS avg_yc_total,
IFNULL(SUM(total_rc) / SUM(matches), 0) AS avg_rc_total,
IFNULL(SUM(CASE WHEN `00-30` + `31-45` + `46-75` + `76-90` > 0 THEN `00-30` END) / SUM(CASE WHEN `00-30` + `31-45` + `46-75` + `76-90` > 0 THEN `00-30` + `31-45` + `46-75` + `76-90` END), 0) AS r_0_30_total,
IFNULL(SUM(CASE WHEN `00-30` + `31-45` + `46-75` + `76-90` > 0 THEN `31-45` END) / SUM(CASE WHEN `00-30` + `31-45` + `46-75` + `76-90` > 0 THEN `00-30` + `31-45` + `46-75` + `76-90` END) , 0)  AS r_31_45_total,
IFNULL(SUM(CASE WHEN `00-30` + `31-45` + `46-75` + `76-90` > 0 THEN `46-75` END) / SUM(CASE WHEN `00-30` + `31-45` + `46-75` + `76-90` > 0 THEN `00-30` + `31-45` + `46-75` + `76-90` END), 0)  AS r_46_75_total,
IFNULL(SUM(CASE WHEN `00-30` + `31-45` + `46-75` + `76-90` > 0 THEN `76-90` END) / SUM(CASE WHEN `00-30` + `31-45` + `46-75` + `76-90` > 0 THEN `00-30` + `31-45` + `46-75` + `76-90` END), 0)  AS r_76_90_total,
IFNULL(SUM(CASE WHEN season_year = tf_season THEN total_yc END) / SUM(CASE WHEN season_year = tf_season THEN matches END), 0) AS season_avg_yc,
IFNULL(SUM(CASE WHEN league_name = tf_league THEN total_yc END) / SUM(CASE WHEN league_name = tf_league THEN matches END), 0) AS league_avg_yc,
IFNULL(SUM(0_card_matches) / SUM(matches), 0) AS 0_card_matches,
IFNULL(SUM(CASE WHEN rbd.season_year = tf_season THEN 0_card_matches END) / SUM(CASE WHEN rbd.season_year = tf_season THEN matches END), 0) AS season_0_card_matches
FROM referee_base_data rbd
WHERE 1 = 1
AND cleaned_referee_name IS NOT NULL
GROUP BY 1, 2
;


DROP TABLE IF EXISTS referee_last_5_data
;

CREATE TABLE referee_last_5_data AS
SELECT
    cleaned_referee_name,
    SUBSTRING_INDEX(GROUP_CONCAT(fouls_per_yc ORDER BY referee_r ASC SEPARATOR '|'), '|', 5) AS last5_fouls_per_yc,
    SUBSTRING_INDEX(GROUP_CONCAT(yellow_cards ORDER BY referee_r ASC SEPARATOR '|'), '|', 5) AS last5_yc,
    SUBSTRING_INDEX(GROUP_CONCAT(red_cards ORDER BY referee_r ASC SEPARATOR '|'), '|', 5) AS last5_rc,
    SUBSTRING_INDEX(GROUP_CONCAT(fouls ORDER BY referee_r ASC SEPARATOR '|'), '|', 5) AS last5_fouls
FROM
(
    SELECT
        cleaned_referee_name,
        referee_r,
        ROUND(SUM(IFNULL(fouls, 0)) / SUM(IFNULL(yellow_cards, 0)), 1) AS fouls_per_yc,
        SUM(IFNULL(yellow_cards, 0)) AS yellow_cards,
        SUM(IFNULL(red_cards, 0)) AS red_cards,
        SUM(IFNULL(fouls, 0)) AS fouls
    FROM analytics.fixture_stats_compile
    WHERE 1 = 1
    AND referee_r <= 5
    GROUP BY 1, 2
) AS ranked_data
WHERE 1 = 1
    AND referee_r <= 5
GROUP BY cleaned_referee_name
;

DROP TABLE IF EXISTS master_referee_view
;

CREATE TABLE master_referee_view AS
SELECT
DISTINCT
rda.fixture_id,
rda.cleaned_referee_name,
rda.total_matches,
rda.avg_yc_total,
rl5d.last5_yc,
rda.tw_yc_pct,
rda.argue_yc_pct,
rda.fouls_per_yc,
rda.ref_avg_fouls,
rl5d.last5_fouls_per_yc,
rda.0_card_matches,
rda.r_0_30_total,
rda.r_31_45_total,
rda.r_46_75_total,
rda.r_76_90_total,
rda.season_avg_yc,
rda.season_0_card_matches,
rda.league_avg_yc,
rda.avg_rc_total,
rl5d.last5_rc,
rl5d.last5_fouls AS ref_last5_fouls
FROM referee_data_agg rda
JOIN referee_last_5_data rl5d
ON rda.cleaned_referee_name = rl5d.cleaned_referee_name
WHERE 1 = 1
-- # AND LOWER(rda.cleaned_referee_name) LIKE '%king%'
;