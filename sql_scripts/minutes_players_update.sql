UPDATE temp.pre_base_player_q pbpq
JOIN live_updates.live_fixture_lineups lfl
ON pbpq.fixture_id = lfl.fixture_id AND pbpq.player_id = lfl.player_id
SET pbpq.starting_xi = CASE WHEN lfl.player_id IS NOT NULL THEN 1 ELSE 0 END,
    pbpq.is_match_live = CASE WHEN lfl.fixture_id IS NOT NULL THEN 1 ELSE 0 END;


TRUNCATE temp.base_player_q;

INSERT INTO temp.base_player_q
SELECT pbpq.*,
       row_number() over (partition by fixture_id, starting_xi order by calc_metric DESC) AS rnk
FROM temp.pre_base_player_q pbpq
JOIN players_upcoming_fixture puf
    on pbpq.fixture_id = puf.fixture_id
    and pbpq.player_id = puf.player_id
WHERE 1 = 1
AND (
    (is_match_live = 0 AND is_new = 0 AND last_start > CURDATE() - INTERVAL 90 DAY)
OR  (is_match_live = 1 AND starting_xi = 1)
     )
;


TRUNCATE temp.player_q;

INSERT INTO temp.player_q
SELECT
CONCAT(fixt,rnk) AS f_rnk,
player_name,
CONCAT(last5_start_foul,'-') AS last5_start_foul,
CONCAT(last5_start_yc, '-') AS last5_start_yc,
team_name,
calc_metric,
season_league_cards,
last5_mins,
f_to_yc_ratio,
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
fixture_id,
player_id
FROM temp.base_player_q
WHERE 1 = 1
AND fixt IS NOT NULL
AND is_match_live = 1
AND is_high_voltage = 1
AND starting_xi = 1
AND calc_metric >= 0.05
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
last5_mins,
f_to_yc_ratio,
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
fixture_id,
player_id
FROM temp.base_player_q
WHERE 1 = 1
AND fixt IS NOT NULL
AND is_match_live = 1
AND is_high_voltage = 0
AND starting_xi = 1
AND rnk < 5
AND calc_metric >= 0.05
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
last5_mins,
f_to_yc_ratio,
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
fixture_id,
player_id
FROM temp.base_player_q
WHERE 1 = 1
AND fixt IS NOT NULL
AND is_match_live = 0
AND is_high_voltage = 1
# AND starting_xi = 1
AND rnk < 7
AND calc_metric >= 0.07
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
last5_mins,
f_to_yc_ratio,
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
fixture_id,
player_id
FROM temp.base_player_q
WHERE 1 = 1
AND fixt IS NOT NULL
AND is_match_live = 0
AND is_high_voltage = 0
# AND starting_xi = 1
AND rnk < 5
AND calc_metric >= 0.07
AND fixture_id NOT IN (SELECT fixture_id FROM temp.player_q)
ORDER BY  timestamp, league_id, fixture_id, rnk
;


DROP TABLE IF EXISTS temp.player_level_fls_pct;

CREATE TABLE temp.player_level_fls_pct AS
SELECT
mpv.player_id,
tf.fixture_id,
t.team_id,
thc.avg_ht_fouls,
ROUND(CASE WHEN season_fixt > 5 AND season_exp_ht_fouls IS NOT NULL THEN (ehf.season_exp_ht_fouls * 0.67 + ehf.total_exp_ht_fouls * 0.33)
            WHEN season_exp_ht_fouls IS NOT NULL THEN (ehf.season_exp_ht_fouls * 0.2 + ehf.total_exp_ht_fouls * 0.8)
            ELSE ehf.total_exp_ht_fouls END, 2) AS exp_ht_fouls
FROM
master_players_view mpv
LEFT JOIN today_fixture tf on mpv.fixture_id = tf.fixture_id
LEFT JOIN live_updates.live_fixtures lf ON tf.fixture_id = lf.fixture_id
LEFT JOIN live_updates.live_fixture_lineups lfl ON mpv.player_id = lfl.player_id
LEFT JOIN teams t ON mpv.team_id = t.team_id
LEFT JOIN temp.exp_fyc_model  efm
ON mpv.player_id = efm.player_id
LEFT JOIN temp.exp_ht_fouls ehf
ON mpv.player_id = ehf.player_id
LEFT JOIN temp.team_ht_combo thc on mpv.fixture_id = thc.fixture_id
AND mpv.team_id = thc.main_team
WHERE 1 = 1
AND COALESCE(player_pos, 'S') <> 'G'
AND lfl.player_id Is NOT NULL
# AND tf.timestamp BETWEEN UNIX_TIMESTAMP(NOW() - INTERVAL 1 MINUTE) AND UNIX_TIMESTAMP(NOW() + INTERVAL 90 MINUTE)
ORDER BY tf.timestamp, tf.fixture_id, exp_ht_fouls DESC
;

DROP TABLE IF EXISTS temp.live_team_fls_sum;

CREATE TABLE temp.live_team_fls_sum AS
SELECT
fixture_id,
team_id,
avg_ht_fouls,
SUM(exp_ht_fouls) as exp_team_fls
FROM
temp.player_level_fls_pct
GROUP BY 1, 2, 3;


DROP TABLE IF EXISTS temp.live_players_fls_sum;

CREATE TABLE temp.live_players_fls_sum AS
SELECT
plfp.player_id,
plfp.fixture_id,
plfp.team_id,
ROUND((exp_ht_fouls / exp_team_fls) * ltfs.avg_ht_fouls, 1) AS exp_ht_fls
FROM
temp.player_level_fls_pct plfp
JOIN temp.live_team_fls_sum ltfs
ON plfp.fixture_id = ltfs.fixture_id AND plfp.team_id = ltfs.team_id
GROUP BY 1, 2, 3;