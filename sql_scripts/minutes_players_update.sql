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
    (is_match_live = 0 AND is_new = 0)
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
AND calc_metric >= 0.12
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
AND calc_metric >= 0.12
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
AND calc_metric >= 0.15
AND fixture_id NOT IN (SELECT fixture_id FROM temp.player_q)
ORDER BY  timestamp, league_id, fixture_id, rnk
;
