-- Live Fouls Watch --
DROP TABLE IF EXISTS temp.live_fouls_watch;

CREATE TABLE temp.live_fouls_watch AS
SELECT
tf.fixt,
t.name,
p.name AS player_name,
CASE WHEN lfl.player_id IS NULL THEN 0 ELSE 1 END AS starting_xi,
IFNULL(lfps.fouls_committed, 0) AS fouls,
IFNULL(lfps.cards_yellow, 0) AS yc,
IFNULL(lfps.cards_red,0) AS rc,
ROUND(mpv.avg_yc_total, 2) AS avg_yc,
ROUND(mpv.season_avg_yc, 2) AS season_avg_yc,
ROUND(mpv.argue_yc_pct, 2) AS argue_yc,
ROUND(mpv.tw_yc_pct, 2) AS tw_yc
FROM
master_players_view mpv
LEFT JOIN players p ON mpv.player_id = p.player_id
LEFT JOIN today_fixture tf on mpv.fixture_id = tf.fixture_id
LEFT JOIN live_updates.live_fixtures lf ON tf.fixture_id = lf.fixture_id
LEFT JOIN live_updates.live_fixture_lineups lfl ON mpv.player_id = lfl.player_id
LEFT JOIN live_updates.live_fixture_player_stats lfps ON mpv.player_id = lfps.player_id
LEFT JOIN teams t ON mpv.team_id = t.team_id
LEFT JOIN live_updates.live_fixture_events lfe
ON mpv.player_id = lfe.player_id
AND LOWER(lfe.detail) LIKE '%substitution%'
LEFT JOIN live_updates.live_fixture_events lfe2
ON mpv.player_id = lfe2.assist_id
AND LOWER(lfe2.detail) LIKE '%substitution%'
LEFT JOIN temp.exp_fyc_model  efm
ON mpv.player_id = efm.player_id
LEFT JOIN temp.player_last_start_date plsd
ON mpv.player_id = plsd.player_id
LEFT JOIN temp.team_last_start_date tlsd
ON t.team_id = tlsd.team_id
WHERE 1 = 1
# AND tf.fixture_id IS NOT NULL
AND ((lfl.player_id Is NOT NULL AND lfe2.assist_id IS NULL) OR lfe.player_id IS NOT NULL)
# AND (zero_foul_match_pct < 0.2 OR zero_season_foul_match_pct < 0.2)
# AND last5_start_foul NOT LIKE '%00%'
# AND tf.league_id IN (135, 140)
# AND LEFT(last5_start_yc, 2) NOT LIKE '%1%'
# AND last5_start_yc LIKE '%1%'
# AND (avg_yc_total > 0.23 OR season_avg_yc > 0.23)
# AND plsd.last_start > '2023-10-10'
# AND tf.timestamp BETWEEN UNIX_TIMESTAMP(NOW() - INTERVAL 120 MINUTE) AND UNIX_TIMESTAMP(NOW() + INTERVAL 360 MINUTE)
ORDER BY tf.timestamp, tf.league_id, tf.fixt, fouls DESC, avg_yc_total DESC
;