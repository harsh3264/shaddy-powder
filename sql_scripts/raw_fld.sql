DROP TABLE IF EXISTS temp.raw_fld;

CREATE TABLE temp.raw_fld AS
    SELECT
    fixt,
       row_number() over (partition by fixt order by exp_ht_fouls_drawn DESC, avg_fouls_drawn_total DESC) AS rnk,
       team_name,
       player_name,
       new_pos AS position,
       exp_ht_fouls_drawn,
       last5_start_fouls_drawn,
       season_avg_fouls_drawn,
       avg_fouls_drawn_total,
       zero_season_foul_drawn_match_pct,
       zero_foul_drawn_match_pct,
       fixture_id,
       player_id
FROM
(SELECT
    tf.fixt,
    tf.fixture_id,
    t.name as team_name,
    p.name as player_name,
    new_pos,
    -- mpv.player_id,
    -- t.team_id,
    ROUND(
        CASE
            WHEN ehf.season_fixt > 5 AND ehf.season_exp_ht_fouls_drawn IS NOT NULL THEN (ehf.season_exp_ht_fouls_drawn * 0.67 + ehf.total_exp_ht_fouls_drawn * 0.33)
            WHEN ehf.season_exp_ht_fouls_drawn IS NOT NULL THEN (ehf.season_exp_ht_fouls_drawn * 0.2 + ehf.total_exp_ht_fouls_drawn * 0.8)
            ELSE ehf.total_exp_ht_fouls_drawn
        END, 2
    ) AS exp_ht_fouls_drawn,
    mpv.last5_start_fouls_drawn,
    mpv.season_avg_fouls_drawn,
    mpv.avg_fouls_drawn_total,
    mpv.zero_season_foul_drawn_match_pct,
    mpv.zero_foul_drawn_match_pct,
    mpv.player_id
FROM
    master_players_view mpv
    LEFT JOIN today_fixture tf ON mpv.fixture_id = tf.fixture_id
    LEFT JOIN teams t ON mpv.team_id = t.team_id
#     LEFT JOIN player_ht_fouls_drawn pht ON mpv.player_id = pht.player_id
    LEFT JOIN temp.exp_ht_fouls ehf ON mpv.player_id = ehf.player_id
    LEFT JOIN players p ON mpv.player_id = p.player_id
    LEFT JOIN live_updates.live_fixtures lf ON tf.fixture_id = lf.fixture_id
    LEFT JOIN live_updates.live_fixture_lineups lfl ON mpv.player_id = lfl.player_id
    LEFT JOIN live_updates.live_fixture_coach lfc ON lfc.team_id = lfl.team_id AND lfc.fixture_id = lfl.fixture_id
    LEFT JOIN temp.new_pos_mapper nps ON lfl.grid = nps.grid AND lfc.formation = nps.formation
WHERE 1 = 1
    AND lfl.player_id Is NOT NULL
    -- AND tf.fixture_id = 1035357
    -- AND COALESCE(player_pos, 'S') <> 'G'
ORDER BY tf.timestamp, tf.fixture_id, exp_ht_fouls_drawn DESC) AS base;

INSERT INTO temp.raw_fld
    SELECT
    fixt,
       row_number() over (partition by fixt order by exp_ht_fouls_drawn DESC, avg_fouls_drawn_total DESC) AS rnk,
       team_name,
       player_name,
       'NA' AS position,
       exp_ht_fouls_drawn,
       last5_start_fouls_drawn,
       season_avg_fouls_drawn,
       avg_fouls_drawn_total,
       zero_season_foul_drawn_match_pct,
       zero_foul_drawn_match_pct,
       fixture_id,
       player_id
FROM
(SELECT
    tf.fixt,
    tf.fixture_id,
    t.name as team_name,
    p.name as player_name,
#     new_pos,
    -- mpv.player_id,
    -- t.team_id,
    ROUND(
        CASE
            WHEN ehf.season_fixt > 5 AND ehf.season_exp_ht_fouls_drawn IS NOT NULL THEN (ehf.season_exp_ht_fouls_drawn * 0.67 + ehf.total_exp_ht_fouls_drawn * 0.33)
            WHEN ehf.season_exp_ht_fouls_drawn IS NOT NULL THEN (ehf.season_exp_ht_fouls_drawn * 0.2 + ehf.total_exp_ht_fouls_drawn * 0.8)
            ELSE ehf.total_exp_ht_fouls_drawn
        END, 2
    ) AS exp_ht_fouls_drawn,
    mpv.last5_start_fouls_drawn,
    mpv.season_avg_fouls_drawn,
    mpv.avg_fouls_drawn_total,
    mpv.zero_season_foul_drawn_match_pct,
    mpv.zero_foul_drawn_match_pct,
    mpv.player_id
FROM
    master_players_view mpv
    LEFT JOIN today_fixture tf ON mpv.fixture_id = tf.fixture_id
    LEFT JOIN teams t ON mpv.team_id = t.team_id
#     LEFT JOIN player_ht_fouls_drawn pht ON mpv.player_id = pht.player_id
    LEFT JOIN temp.exp_ht_fouls ehf ON mpv.player_id = ehf.player_id
    LEFT JOIN players p ON mpv.player_id = p.player_id
    LEFT JOIN temp.player_last_start_date plsd on mpv.player_id = plsd.player_id
    LEFT JOIN live_updates.live_fixtures lf ON tf.fixture_id = lf.fixture_id
    LEFT JOIN live_updates.live_fixture_lineups lfl ON mpv.player_id = lfl.player_id
    LEFT JOIN injuries i on mpv.player_id = i.player_id
    AND mpv.fixture_id = i.fixture_id
WHERE 1 = 1
    AND plsd.last_start > CURDATE() - INTERVAL 20 DAY
    AND COALESCE(i.type, 'A') <> 'Missing Fixture'
    AND tf.fixture_id NOT IN (SELECT fixture_id FROM temp.raw_fld WHERE LENGTH(fixture_id) > 3) 
    AND tf.timestamp BETWEEN UNIX_TIMESTAMP(NOW() - INTERVAL 10 MINUTE) AND UNIX_TIMESTAMP(NOW() + INTERVAL 1440 MINUTE)
    -- AND tf.fixture_id = 1035357
    -- AND COALESCE(player_pos, 'S') <> 'G'
ORDER BY tf.timestamp, tf.fixture_id, exp_ht_fouls_drawn DESC) AS base;