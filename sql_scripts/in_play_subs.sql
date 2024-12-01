-- Subs Foul Telegram Automation

-- Identify new subs.

TRUNCATE temp.new_in_play_subs;

INSERT INTO temp.new_in_play_subs
SELECT
# lf.london_update_time,
mpv.player_id,
CONCAT(lf.total_home_goals,'-', lf.total_away_goals) AS score,
tf.fixt,
lf.status,
lf.elapsed,
t.name,
p.name AS player_name,
IFNULL(IFNULL(lsf2.type, lsf.type), 'Z') AS type_of_fouler,
# CASE WHEN lfe.player_id IS NOT NULL THEN 1 ELSE 0 END AS sub_on,
lfps.fouls_committed AS fouls_in_current_match,
CASE WHEN IFNULL(lfps.cards_red,0) + IFNULL(lfps.cards_yellow, 0) > 0 THEN 1 ELSE 0 END AS cards_in_current_match,
mpv.last5_sub_foul,
# mpv.last5_sub_result,
mpv.last5_sub_mins,
mpv.last5_sub_yc,
mpv.last5_win_sub_foul,
mpv.last5_loss_sub_foul,
mpv.last5_draw_sub_foul,
mpv.last5_start_foul,
mpv.last5_start_yc,
mpv.avg_fouls_total,
mpv.season_avg_fouls,
mpv.avg_yc_total,
mpv.season_avg_yc,
mpv.zero_foul_match_pct,
mpv.zero_season_foul_match_pct
# IFNULL(lsf2.type, 'Z') AS sub_fouler_type
FROM
master_players_view mpv
LEFT JOIN players p ON mpv.player_id = p.player_id
LEFT JOIN today_fixture tf on mpv.fixture_id = tf.fixture_id
LEFT JOIN live_updates.live_fixtures lf ON mpv.fixture_id = lf.fixture_id
LEFT JOIN live_updates.live_fixture_lineups lfl ON mpv.player_id = lfl.player_id
LEFT JOIN live_updates.live_fixture_player_stats lfps ON mpv.player_id = lfps.player_id
LEFT JOIN teams t ON mpv.team_id = t.team_id
LEFT JOIN temp.legendary_start_foulers lsf ON mpv.player_id = lsf.player_id
LEFT JOIN temp.legendary_sub_foulers lsf2 ON mpv.player_id = lsf2.player_id
LEFT JOIN live_updates.live_fixture_events lfe
ON mpv.player_id = lfe.player_id
AND LOWER(lfe.detail) LIKE '%substitution%'
LEFT JOIN live_updates.live_fixture_events lfe2
ON mpv.player_id = lfe2.assist_id
AND LOWER(lfe2.detail) LIKE '%substitution%'
WHERE 1 = 1
AND lf.fixture_id IS NOT NULL
AND mpv.player_id NOT IN (SELECT player_id FROM temp.in_play_subs_foul)
AND (lfe.player_id IS NOT NULL)
AND (lfl.player_id IS NULL)
AND (mpv.avg_fouls_total > 1.2 OR mpv.season_avg_fouls > 1.5)
AND (zero_foul_match_pct < 0.3 OR zero_season_foul_match_pct < 0.2)
AND (last5_sub_foul NOT LIKE '%00%' OR (last5_start_foul NOT LIKE '%00%' AND last5_sub_foul NOT LIKE '%000%'))
ORDER BY lf.timestamp, lf.league_id, lf.fixture_id, t.team_id, type_of_fouler, avg_fouls_total
;

-- Adds all the subs 

TRUNCATE temp.in_play_subs_foul;

INSERT INTO temp.in_play_subs_foul
SELECT
# lf.london_update_time,
mpv.player_id,
CONCAT(lf.total_home_goals,'-', lf.total_away_goals) AS score,
tf.fixt,
lf.status,
lf.elapsed,
t.name,
p.name AS player_name,
IFNULL(IFNULL(lsf2.type, lsf.type), 'Z') AS type_of_fouler,
# CASE WHEN lfe.player_id IS NOT NULL THEN 1 ELSE 0 END AS sub_on,
lfps.fouls_committed AS fouls_in_current_match,
CASE WHEN IFNULL(lfps.cards_red,0) + IFNULL(lfps.cards_yellow, 0) > 0 THEN 1 ELSE 0 END AS cards_in_current_match,
mpv.last5_sub_foul,
# mpv.last5_sub_result,
mpv.last5_sub_mins,
mpv.last5_sub_yc,
mpv.last5_win_sub_foul,
mpv.last5_loss_sub_foul,
mpv.last5_draw_sub_foul,
mpv.last5_start_foul,
mpv.last5_start_yc,
mpv.avg_fouls_total,
mpv.season_avg_fouls,
mpv.avg_yc_total,
mpv.season_avg_yc,
mpv.zero_foul_match_pct,
mpv.zero_season_foul_match_pct
# IFNULL(lsf2.type, 'Z') AS sub_fouler_type
FROM
master_players_view mpv
LEFT JOIN players p ON mpv.player_id = p.player_id
LEFT JOIN today_fixture tf on mpv.fixture_id = tf.fixture_id
LEFT JOIN live_updates.live_fixtures lf ON mpv.fixture_id = lf.fixture_id
LEFT JOIN live_updates.live_fixture_lineups lfl ON mpv.player_id = lfl.player_id
LEFT JOIN live_updates.live_fixture_player_stats lfps ON mpv.player_id = lfps.player_id
LEFT JOIN teams t ON mpv.team_id = t.team_id
LEFT JOIN temp.legendary_start_foulers lsf ON mpv.player_id = lsf.player_id
LEFT JOIN temp.legendary_sub_foulers lsf2 ON mpv.player_id = lsf2.player_id
LEFT JOIN live_updates.live_fixture_events lfe
ON mpv.player_id = lfe.player_id
AND LOWER(lfe.detail) LIKE '%substitution%'
LEFT JOIN live_updates.live_fixture_events lfe2
ON mpv.player_id = lfe2.assist_id
AND LOWER(lfe2.detail) LIKE '%substitution%'
WHERE 1 = 1
AND lf.fixture_id IS NOT NULL
AND (lfe.player_id IS NOT NULL)
AND (lfl.player_id IS NULL)
AND (zero_foul_match_pct < 0.3 OR zero_season_foul_match_pct < 0.2)
AND (last5_sub_foul NOT LIKE '%000%' OR (last5_start_foul NOT LIKE '%000%' AND last5_sub_foul NOT LIKE '%0000%'))
ORDER BY lf.timestamp, lf.league_id, lf.fixture_id, t.team_id, type_of_fouler, avg_fouls_total
;