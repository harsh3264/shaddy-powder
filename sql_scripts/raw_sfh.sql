DROP TABLE IF EXISTS temp.raw_sfh;

CREATE TABLE temp.raw_sfh AS
SELECT fixt,
       row_number() over (partition by fixt order by exp_ht_shots DESC, avg_shots_total DESC) AS rnk,
       team_name,
       player_name,
       new_pos AS position,
       exp_ht_shots,
       last5_shots_total,
       season_avg_shots,
       avg_shots_total,
       zero_season_shot_match_pct,
       zero_shot_match_pct,
       fixture_id,
       player_id
FROM
(SELECT
    fixt,
    tf.fixture_id,
    t.name as team_name,
    p.name as player_name,
    mpv.player_id,
    -- t.team_id,
    ROUND(
        CASE
            WHEN pht.season_fixt > 5 AND ehf.season_exp_ht_shots IS NOT NULL THEN (ehf.season_exp_ht_shots * 0.67 + ehf.total_exp_ht_shots * 0.33)
            WHEN ehf.season_exp_ht_shots IS NOT NULL THEN (ehf.season_exp_ht_shots * 0.2 + ehf.total_exp_ht_shots * 0.8)
            ELSE ehf.total_exp_ht_shots
        END, 2
    ) AS exp_ht_shots,
    mpv.last5_shots_total,
    mpv.season_avg_shots,
    mpv.avg_shots_total,
    mpv.zero_season_shot_match_pct,
    mpv.zero_shot_match_pct,
    nps.new_pos
FROM
    master_players_view mpv
    LEFT JOIN today_fixture tf ON mpv.fixture_id = tf.fixture_id
    LEFT JOIN teams t ON mpv.team_id = t.team_id
    LEFT JOIN temp.player_ht_shots pht ON mpv.player_id = pht.player_id
    LEFT JOIN temp.exp_ht_shots ehf ON mpv.player_id = ehf.player_id
    LEFT JOIN players p ON mpv.player_id = p.player_id
    LEFT JOIN live_updates.live_fixtures lf ON tf.fixture_id = lf.fixture_id
    LEFT JOIN live_updates.live_fixture_lineups lfl ON mpv.player_id = lfl.player_id
    LEFT JOIN live_updates.live_fixture_coach lfc ON lfc.team_id = lfl.team_id AND lfc.fixture_id = lfl.fixture_id
    LEFT JOIN temp.new_pos_mapper nps ON lfl.grid = nps.grid AND lfc.formation = nps.formation
WHERE 1 = 1
    AND tf.fixture_id <> 1035357
    AND lfl.player_id Is NOT NULL
    -- AND COALESCE(player_pos, 'S') <> 'G'
ORDER BY tf.timestamp, tf.fixture_id, exp_ht_shots DESC)AS base;

INSERT INTO temp.raw_sfh
SELECT fixt,
       row_number() over (partition by fixt order by exp_ht_shots DESC, avg_shots_total DESC) AS rnk,
       team_name,
       player_name,
       'NA' AS position,
       exp_ht_shots,
       last5_shots_total,
       season_avg_shots,
       avg_shots_total,
       zero_season_shot_match_pct,
       zero_shot_match_pct,
       fixture_id,
       player_id
FROM
(SELECT
    fixt,
    tf.fixture_id,
    t.name as team_name,
    p.name as player_name,
    mpv.player_id,
    -- t.team_id,
    ROUND(
        CASE
            WHEN pht.season_fixt > 5 AND ehf.season_exp_ht_shots IS NOT NULL THEN (ehf.season_exp_ht_shots * 0.67 + ehf.total_exp_ht_shots * 0.33)
            WHEN ehf.season_exp_ht_shots IS NOT NULL THEN (ehf.season_exp_ht_shots * 0.2 + ehf.total_exp_ht_shots * 0.8)
            ELSE ehf.total_exp_ht_shots
        END, 2
    ) AS exp_ht_shots,
    mpv.last5_shots_total,
    mpv.season_avg_shots,
    mpv.avg_shots_total,
    mpv.zero_season_shot_match_pct,
    mpv.zero_shot_match_pct
FROM
    master_players_view mpv
    LEFT JOIN today_fixture tf ON mpv.fixture_id = tf.fixture_id
    LEFT JOIN teams t ON mpv.team_id = t.team_id
    LEFT JOIN temp.player_ht_shots pht ON mpv.player_id = pht.player_id
    LEFT JOIN temp.exp_ht_shots ehf ON mpv.player_id = ehf.player_id
    LEFT JOIN players p ON mpv.player_id = p.player_id
    LEFT JOIN temp.player_last_start_date plsd on mpv.player_id = plsd.player_id
    LEFT JOIN live_updates.live_fixtures lf ON tf.fixture_id = lf.fixture_id
    LEFT JOIN live_updates.live_fixture_lineups lfl ON mpv.player_id = lfl.player_id
    LEFT JOIN injuries i on mpv.player_id = i.player_id
    AND mpv.fixture_id = i.fixture_id
WHERE 1 = 1
    -- AND tf.fixture_id = 1035357
#     AND lfl.player_id Is NOT NULL
    AND plsd.last_start > CURDATE() - INTERVAL 20 DAY
    AND COALESCE(i.type, 'A') <> 'Missing Fixture'
    AND tf.fixture_id NOT IN (SELECT fixture_id FROM temp.raw_sfh)
    AND tf.timestamp BETWEEN UNIX_TIMESTAMP(NOW() - INTERVAL 10 MINUTE) AND UNIX_TIMESTAMP(NOW() + INTERVAL 1440 MINUTE)
    AND COALESCE(player_pos, 'S') <> 'G'
ORDER BY tf.timestamp, tf.fixture_id, exp_ht_shots DESC)AS base;