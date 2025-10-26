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
mrv.r_76_90_total,
mrv.ref_avg_fouls,
mrv.ref_last5_fouls
FROM today_fixture tf
LEFT JOIN master_referee_view mrv on mrv.cleaned_referee_name = tf.cleaned_referee_name
WHERE 1 = 1
# AND tf.cleaned_referee_name IS NOT NULL
# AND LOWER(mrv.cleaned_referee_name) LIKE '%king%'
ORDER BY tf.timestamp, tf.league_id
;

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
LEFT JOIN temp.fixture_cards_bookmakers_summary fcbs
ON rd.fixture_id = fcbs.fixture_id AND fcbs.team_id = 0
LEFT JOIN temp.top_high_voltage thv
ON rd.fixture_id = thv.fixture_id
LEFT JOIN today_fixture tf on rd.fixture_id = tf.fixture_id
WHERE 1 = 1
ORDER BY tf.fixture_date, tf.league_id, tf.timestamp, tf.fixture_id
-- AND league = 'UEFA Champions League'
;