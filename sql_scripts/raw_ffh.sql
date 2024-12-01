DROP TABLE IF EXISTS temp.foul_announce;

# SELECT * FROM temp.foul_announce LIMIT 40;

CREATE TABLE temp.foul_announce AS
(SELECT
DISTINCT
mpv.player_id,
lfl.grid,
lfc.formation,
#  tf.league_id,
# tf.fixture_id,
tf.fixt,
thc.avg_ht_fouls AS team_exp_ht_fls,
t.name AS team_name,
p.name AS player_name,
nps.new_pos AS player_pos,
CASE WHEN lsf.type = 'Start Fouler - Legend' THEN 'Pro'
     WHEN lsf.type = 'Start Fouler - Miss_1' THEN 'Semi-Pro'
     ELSE 'Occasional' END AS fouler_type,
ROUND(((CASE WHEN season_fixt > 5 AND season_exp_ht_fouls IS NOT NULL THEN (ehf.season_exp_ht_fouls * 0.67 + ehf.total_exp_ht_fouls * 0.33)
            WHEN season_exp_ht_fouls IS NOT NULL THEN (ehf.season_exp_ht_fouls * 0.2 + ehf.total_exp_ht_fouls * 0.8)
            ELSE ehf.total_exp_ht_fouls END) +
((fp.fhc / fp.c_mt) * (efm.fouls) / efm.total_matches))
/ 2, 2)
AS calc_ht_fls,
ROUND((((CASE WHEN season_fixt > 5 AND season_exp_ht_fouls IS NOT NULL THEN (ehf.season_exp_ht_fouls * 0.9 + ehf.total_exp_ht_fouls * 0.1)
            WHEN season_exp_ht_fouls IS NOT NULL THEN (ehf.season_exp_ht_fouls * 0.2 + ehf.total_exp_ht_fouls * 0.8)
            ELSE ehf.total_exp_ht_fouls END) * 0.75) +
(((fp.fhc / fp.c_mt) * (efm.fouls) / efm.total_matches) * 0.25)), 2)
AS pro_calc_ht_fls,
ROUND((((CASE WHEN season_fixt > 5 AND season_exp_ht_fouls IS NOT NULL THEN (ehf.season_exp_ht_fouls * 0.8 + ehf.total_exp_ht_fouls * 0.2)
            WHEN season_exp_ht_fouls IS NOT NULL THEN (ehf.season_exp_ht_fouls * 0.2 + ehf.total_exp_ht_fouls * 0.8)
            ELSE ehf.total_exp_ht_fouls END) * 0.66) +
(((fp.fhc / fp.c_mt) * (efm.fouls) / efm.total_matches) * 0.34)), 2)
AS spro_calc_ht_fls,
fdm.nn1 AS matchup_1,
fdm.nn2 AS matchup_2,
ROUND((
    ((((ROUND((100 - fdm.dist_nn1) * (fdm.nn1_fld) / 100, 3)) * 0.33) + ((ROUND((100 - fdm.dist_nn1) * (COALESCE(fdm.nn1_fld_s, fdm.nn1_fld)) / 100, 3)) * 0.67)) * 0.67) +
    ((((ROUND((100 - fdm.dist_nn2) * (fdm.nn2_fld) / 100, 3)) * 0.33) + ((ROUND((100 - fdm.dist_nn2) * (COALESCE(fdm.nn2_fld_s, fdm.nn2_fld)) / 100, 3)) * 0.67)) * 0.33)
    ), 1) AS m_ht_impact,
ROUND(nn1_fld, 1) AS m1_fld,
ROUND(nn2_fld, 1) AS m2_fld,
ROUND((100 - fdm.dist_nn1) * (fdm.nn1_fld) / 100, 2) AS matchup_1_fld,
ROUND((100 - fdm.dist_nn1) * (fdm.nn1_fld_s) / 100, 2) AS matchup_1_fld_s,
ROUND((100 - fdm.dist_nn2) * (fdm.nn2_fld) / 100, 2) AS matchup_2_fld,
ROUND((100 - fdm.dist_nn2) * (fdm.nn2_fld_s) / 100, 2) AS matchup_2_fld_s,
exp_ht_fls AS r_d_fls,
fp.ffh_pct,
ROUND(avg_fouls_total * fp.ffh_pct, 2) AS l1,
ROUND(season_avg_fouls * fp.ffh_pct, 2) AS l2,
ROUND(ehf.total_exp_ht_fouls, 2) AS ht_fouls_total,
ROUND(ehf.season_exp_ht_fouls, 2) AS ht_fouls_season,
ROUND(CASE WHEN season_fixt > 5 AND season_exp_ht_fouls IS NOT NULL THEN (ehf.season_exp_ht_fouls * 0.67 + ehf.total_exp_ht_fouls * 0.33)
            WHEN season_exp_ht_fouls IS NOT NULL THEN (ehf.season_exp_ht_fouls * 0.2 + ehf.total_exp_ht_fouls * 0.8)
            ELSE ehf.total_exp_ht_fouls END, 2) AS exp_ht_fouls,
ROUND(CASE WHEN season_fixt > 5 AND season_exp_ht_fouls IS NOT NULL THEN (ehf.season_exp_ht_fouls * 0.67 + ehf.total_exp_ht_fouls * 0.33) * 0.8
            WHEN season_exp_ht_fouls IS NOT NULL THEN (ehf.season_exp_ht_fouls * 0.2 + ehf.total_exp_ht_fouls * 0.8) * 0.8
            ELSE ehf.total_exp_ht_fouls * 0.8 END, 2) AS exp_ht_fouls_fn,
mpv.avg_fouls_total,
mpv.season_avg_fouls,
last5_start_foul,
ROUND(mpv.zero_foul_match_pct,2) AS zero_f,
ROUND(mpv.zero_season_foul_match_pct,2) AS zero_f_s,
avg_fouls_drawn_total,
season_avg_fouls_drawn,
last5_start_fouls_drawn,
ROUND(mpv.zero_foul_drawn_match_pct,2) AS zero_fd,
ROUND(mpv.zero_season_foul_drawn_match_pct,2) AS zero_fd_s,
last5_start_yc,
mpv.avg_tackles_total,
mpv.season_avg_tackles,
last5_tackles_total,
ROUND(mpv.zero_tackle_match_pct,2) AS zero_t,
ROUND(mpv.zero_season_tackle_match_pct,2) AS zero_t_s,
ROUND(efm.foul_matches / efm.yc_w_foul_matches, 2) AS fm_to_yc_ratio,
ROUND(efm.fouls / efm.yc_w_foul_matches, 2) AS f_to_yc_ratio,
mpv.avg_yc_total,
mpv.season_avg_yc,
mpv.argue_yc_pct,
mpv.tw_yc_pct,
tf.fixture_id,
i.type,
fp.fhc,
fp.c_mt,
fp.matches,
tf.timestamp,
tf.fixture_date,
tf.name AS league_name,
ROUND(ROUND(efm.fouls / efm.yc_w_foul_matches, 2) * fp.fhc / fp.matches, 2) AS ratio_f,
ROUND(ROUND(efm.fouls / efm.yc_w_foul_matches, 2) * fp.fhc * (1 - mpv.zero_foul_match_pct) / fp.matches, 2) AS ratio_f2
FROM
master_players_view mpv
LEFT JOIN players p ON mpv.player_id = p.player_id
LEFT JOIN live_updates.live_fixture_lineups lfl ON mpv.player_id = lfl.player_id
LEFT JOIN temp.FOUL_DRAWN_MAP fdm ON mpv.player_id = fdm.player_id
LEFT JOIN temp.player_last_start_date plsd on mpv.player_id = plsd.player_id
LEFT JOIN temp.team_last_start_date tlsd on lfl.team_id = tlsd.team_id
LEFT JOIN temp.live_players_fls_sum lpfs ON mpv.player_id = lpfs.player_id
LEFT JOIN today_fixture tf on lfl.fixture_id = tf.fixture_id
LEFT JOIN live_updates.live_fixtures lf ON lfl.fixture_id = lf.fixture_id
LEFT JOIN live_updates.live_fixture_coach lfc ON lfl.team_id = lfc.team_id AND lfl.fixture_id = lfc.fixture_id
LEFT JOIN temp.new_pos_mapper nps ON lfl.grid = nps.grid AND lfc.formation = nps.formation
LEFT JOIN teams t ON lfl.team_id = t.team_id
LEFT JOIN temp.legendary_start_foulers lsf ON mpv.player_id = lsf.player_id
LEFT JOIN temp.exp_fyc_model  efm
ON mpv.player_id = efm.player_id
LEFT JOIN temp.exp_ht_fouls ehf
ON mpv.player_id = ehf.player_id
LEFT JOIN injuries i on mpv.player_id = i.player_id
AND lfl.fixture_id = i.fixture_id
LEFT JOIN temp.team_ht_combo thc on lfl.fixture_id = thc.fixture_id
AND lfl.team_id = thc.main_team
LEFT JOIN temp.ffh_player fp on mpv.player_id = fp.player_id
WHERE 1 = 1
AND COALESCE(player_pos, 'S') <> 'G'
# AND mpv.player_id IN (46657, 46742)
AND lfl.player_id IS NOT NULL);


INSERT INTO temp.foul_announce
SELECT
DISTINCT
mpv.player_id,
lfl.grid,
lfc.formation,
#  tf.league_id,
# tf.fixture_id,
tf.fixt,
thc.avg_ht_fouls AS team_exp_ht_fls,
t.name AS team_name,
p.name AS player_name,
nps.new_pos AS player_pos,
CASE WHEN lsf.type = 'Start Fouler - Legend' THEN 'Pro'
     WHEN lsf.type = 'Start Fouler - Miss_1' THEN 'Semi-Pro'
     ELSE 'Occasional' END AS fouler_type,
ROUND(((CASE WHEN season_fixt > 5 AND season_exp_ht_fouls IS NOT NULL THEN (ehf.season_exp_ht_fouls * 0.67 + ehf.total_exp_ht_fouls * 0.33)
            WHEN season_exp_ht_fouls IS NOT NULL THEN (ehf.season_exp_ht_fouls * 0.2 + ehf.total_exp_ht_fouls * 0.8)
            ELSE ehf.total_exp_ht_fouls END) +
((fp.fhc / fp.c_mt) * (efm.fouls) / efm.total_matches))
/ 2, 2)
AS calc_ht_fls,
ROUND((((CASE WHEN season_fixt > 5 AND season_exp_ht_fouls IS NOT NULL THEN (ehf.season_exp_ht_fouls * 0.9 + ehf.total_exp_ht_fouls * 0.1)
            WHEN season_exp_ht_fouls IS NOT NULL THEN (ehf.season_exp_ht_fouls * 0.2 + ehf.total_exp_ht_fouls * 0.8)
            ELSE ehf.total_exp_ht_fouls END) * 0.75) +
(((fp.fhc / fp.c_mt) * (efm.fouls) / efm.total_matches) * 0.25)), 2)
AS pro_calc_ht_fls,
ROUND((((CASE WHEN season_fixt > 5 AND season_exp_ht_fouls IS NOT NULL THEN (ehf.season_exp_ht_fouls * 0.8 + ehf.total_exp_ht_fouls * 0.2)
            WHEN season_exp_ht_fouls IS NOT NULL THEN (ehf.season_exp_ht_fouls * 0.2 + ehf.total_exp_ht_fouls * 0.8)
            ELSE ehf.total_exp_ht_fouls END) * 0.66) +
(((fp.fhc / fp.c_mt) * (efm.fouls) / efm.total_matches) * 0.34)), 2)
AS spro_calc_ht_fls,
fdm.nn1 AS matchup_1,
fdm.nn2 AS matchup_2,
ROUND((
    ((((ROUND((100 - fdm.dist_nn1) * (fdm.nn1_fld) / 100, 3)) * 0.33) + ((ROUND((100 - fdm.dist_nn1) * (COALESCE(fdm.nn1_fld_s, fdm.nn1_fld)) / 100, 3)) * 0.67)) * 0.67) +
    ((((ROUND((100 - fdm.dist_nn2) * (fdm.nn2_fld) / 100, 3)) * 0.33) + ((ROUND((100 - fdm.dist_nn2) * (COALESCE(fdm.nn2_fld_s, fdm.nn2_fld)) / 100, 3)) * 0.67)) * 0.33)
    ), 1) AS m_ht_impact,
ROUND(nn1_fld, 1) AS m1_fld,
ROUND(nn2_fld, 1) AS m2_fld,
ROUND((100 - fdm.dist_nn1) * (fdm.nn1_fld) / 100, 2) AS matchup_1_fld,
ROUND((100 - fdm.dist_nn1) * (fdm.nn1_fld_s) / 100, 2) AS matchup_1_fld_s,
ROUND((100 - fdm.dist_nn2) * (fdm.nn2_fld) / 100, 2) AS matchup_2_fld,
ROUND((100 - fdm.dist_nn2) * (fdm.nn2_fld_s) / 100, 2) AS matchup_2_fld_s,
exp_ht_fls AS r_d_fls,
fp.ffh_pct,
ROUND(avg_fouls_total * fp.ffh_pct, 2) AS l1,
ROUND(season_avg_fouls * fp.ffh_pct, 2) AS l2,
ROUND(ehf.total_exp_ht_fouls, 2) AS ht_fouls_total,
ROUND(ehf.season_exp_ht_fouls, 2) AS ht_fouls_season,
ROUND(CASE WHEN season_fixt > 5 AND season_exp_ht_fouls IS NOT NULL THEN (ehf.season_exp_ht_fouls * 0.67 + ehf.total_exp_ht_fouls * 0.33)
            WHEN season_exp_ht_fouls IS NOT NULL THEN (ehf.season_exp_ht_fouls * 0.2 + ehf.total_exp_ht_fouls * 0.8)
            ELSE ehf.total_exp_ht_fouls END, 2) AS exp_ht_fouls,
ROUND(CASE WHEN season_fixt > 5 AND season_exp_ht_fouls IS NOT NULL THEN (ehf.season_exp_ht_fouls * 0.67 + ehf.total_exp_ht_fouls * 0.33) * 0.8
            WHEN season_exp_ht_fouls IS NOT NULL THEN (ehf.season_exp_ht_fouls * 0.2 + ehf.total_exp_ht_fouls * 0.8) * 0.8
            ELSE ehf.total_exp_ht_fouls * 0.8 END, 2) AS exp_ht_fouls_fn,
mpv.avg_fouls_total,
mpv.season_avg_fouls,
last5_start_foul,
ROUND(mpv.zero_foul_match_pct,2) AS zero_f,
ROUND(mpv.zero_season_foul_match_pct,2) AS zero_f_s,
avg_fouls_drawn_total,
season_avg_fouls_drawn,
last5_start_fouls_drawn,
ROUND(mpv.zero_foul_drawn_match_pct,2) AS zero_fd,
ROUND(mpv.zero_season_foul_drawn_match_pct,2) AS zero_fd_s,
last5_start_yc,
mpv.avg_tackles_total,
mpv.season_avg_tackles,
last5_tackles_total,
ROUND(mpv.zero_tackle_match_pct,2) AS zero_t,
ROUND(mpv.zero_season_tackle_match_pct,2) AS zero_t_s,
ROUND(efm.foul_matches / efm.yc_w_foul_matches, 2) AS fm_to_yc_ratio,
ROUND(efm.fouls / efm.yc_w_foul_matches, 2) AS f_to_yc_ratio,
mpv.avg_yc_total,
mpv.season_avg_yc,
mpv.argue_yc_pct,
mpv.tw_yc_pct,
tf.fixture_id,
i.type,
fp.fhc,
fp.c_mt,
fp.matches,
tf.timestamp,
tf.fixture_date,
tf.name AS league_name,
ROUND(ROUND(efm.fouls / efm.yc_w_foul_matches, 2) * fp.fhc / fp.matches, 2) AS ratio_f,
ROUND(ROUND(efm.fouls / efm.yc_w_foul_matches, 2) * fp.fhc * (1 - mpv.zero_foul_match_pct) / fp.matches, 2) AS ratio_f2
FROM
master_players_view mpv
LEFT JOIN players p ON mpv.player_id = p.player_id
LEFT JOIN temp.FOUL_DRAWN_MAP fdm ON mpv.player_id = fdm.player_id
LEFT JOIN temp.player_last_start_date plsd on mpv.player_id = plsd.player_id
LEFT JOIN temp.team_last_start_date tlsd on mpv.team_id = tlsd.team_id
LEFT JOIN temp.live_players_fls_sum lpfs ON mpv.player_id = lpfs.player_id
LEFT JOIN today_fixture tf on mpv.fixture_id = tf.fixture_id
LEFT JOIN live_updates.live_fixtures lf ON tf.fixture_id = lf.fixture_id
LEFT JOIN live_updates.live_fixture_lineups lfl ON mpv.player_id = lfl.player_id
LEFT JOIN live_updates.live_fixture_coach lfc ON lfl.team_id = lfc.team_id AND lfl.fixture_id = lfc.fixture_id
LEFT JOIN temp.new_pos_mapper nps ON lfl.grid = nps.grid AND lfc.formation = nps.formation
LEFT JOIN teams t ON mpv.team_id = t.team_id
LEFT JOIN temp.legendary_start_foulers lsf ON mpv.player_id = lsf.player_id
LEFT JOIN temp.exp_fyc_model  efm
ON mpv.player_id = efm.player_id
LEFT JOIN temp.exp_ht_fouls ehf
ON mpv.player_id = ehf.player_id
LEFT JOIN injuries i on mpv.player_id = i.player_id
AND mpv.fixture_id = i.fixture_id
LEFT JOIN temp.team_ht_combo thc on mpv.fixture_id = thc.fixture_id
AND mpv.team_id = thc.main_team
LEFT JOIN temp.ffh_player fp on mpv.player_id = fp.player_id
WHERE 1 = 1
AND plsd.last_start > CURDATE() - INTERVAL 20 DAY
AND COALESCE(i.type, 'A') <> 'Missing Fixture'
AND tf.fixture_id NOT IN (SELECT fixture_id FROM temp.foul_announce WHERE LENGTH(fixture_id) > 3)
AND tf.timestamp BETWEEN UNIX_TIMESTAMP(NOW() - INTERVAL 10 MINUTE) AND UNIX_TIMESTAMP(NOW() + INTERVAL 1440 MINUTE)
# AND COALESCE(player_pos, 'S') <> 'G'
;


DROP TABLE IF EXISTS temp.raw_ffh;

CREATE TABLE temp.raw_ffh AS
SELECT fixt,
        row_number() over (partition by fixt order by ffh DESC, new_logic DESC) AS rnk,
        player_name,
        team_name,
        fouler_type,
        ffh,
        player_pos,
        matchup_1,
        matchup_2,
        last5_start_foul,
        season_avg_fouls,
        avg_fouls_total,
        zero_f_s,
        zero_f,
        fixture_id,
        calc_ht_fls,
        pro_calc_ht_fls,
        spro_calc_ht_fls,
        ROUND(GREATEST(pro_calc_ht_fls, calc_ht_fls), 2) AS c_data,
        fixture_date,
        league_name,
        player_id
FROM
(SELECT
fixt,
fixture_id,
player_id,
grid,
team_exp_ht_fls,
team_name,
player_name,
player_pos,
fouler_type,
CASE
    WHEN m_ht_impact IS NOT NULL AND calc_ht_fls IS NOT NULL AND fouler_type = 'Pro' AND player_pos LIKE '%CB%' THEN ROUND(((GREATEST(pro_calc_ht_fls, calc_ht_fls) * 0.7) + (m_ht_impact * 0.3)) - 0.05, 2)
    WHEN m_ht_impact IS NOT NULL AND calc_ht_fls IS NOT NULL AND fouler_type = 'Semi-Pro' AND player_pos LIKE '%CB%' THEN ROUND(((GREATEST(spro_calc_ht_fls, calc_ht_fls) * 0.6) + (m_ht_impact * 0.4)) - 0.1, 2)
    WHEN m_ht_impact IS NOT NULL AND calc_ht_fls IS NOT NULL AND fouler_type = 'Occasional' AND player_pos LIKE '%CB%' THEN ROUND(((calc_ht_fls * 0.5) + (m_ht_impact * 0.5)) - 0.15, 2)
    WHEN m_ht_impact IS NOT NULL AND calc_ht_fls IS NOT NULL AND fouler_type = 'Pro' THEN ROUND(((GREATEST(pro_calc_ht_fls, calc_ht_fls) * 0.7) + (m_ht_impact * 0.3)) + 0.15, 2)
    WHEN m_ht_impact IS NOT NULL AND calc_ht_fls IS NOT NULL AND fouler_type = 'Semi-Pro' THEN ROUND(((GREATEST(spro_calc_ht_fls, calc_ht_fls) * 0.6) + (m_ht_impact * 0.4)) + 0.1, 2)
    WHEN m_ht_impact IS NOT NULL AND calc_ht_fls IS NOT NULL AND fouler_type = 'Occasional' THEN ROUND(((calc_ht_fls * 0.5) + (m_ht_impact * 0.5)), 2)
    WHEN m_ht_impact IS NULL AND calc_ht_fls IS NULL THEN ROUND(exp_ht_fouls, 2)
    WHEN m_ht_impact IS NULL AND calc_ht_fls IS NOT NULL THEN ROUND(calc_ht_fls, 2)
    WHEN m_ht_impact IS NOT NULL AND calc_ht_fls IS NULL THEN ROUND(m_ht_impact, 2)
    ELSE exp_ht_fouls END
    AS ffh,
# CASE WHEN exp_ht_fls IS NULL THEN ROUND((calc_ht_fls + m_ht_impact) / 2, 1)
#      ELSE ROUND((((calc_ht_fls + exp_ht_fls) / 2) + m_ht_impact) / 2, 2) END AS new_logic,
matchup_1,
matchup_2,
CASE
    WHEN m_ht_impact IS NOT NULL AND exp_ht_fouls IS NOT NULL THEN ROUND((exp_ht_fouls + m_ht_impact) / 2, 2)
    WHEN m_ht_impact IS NULL THEN ROUND(exp_ht_fouls, 2)
    WHEN exp_ht_fouls IS NULL THEN ROUND(m_ht_impact, 2)
    ELSE calc_ht_fls END
    AS new_logic,
m1_fld,
m2_fld,
calc_ht_fls,
m_ht_impact,
exp_ht_fouls,
last5_start_foul,
season_avg_fouls,
avg_fouls_total,
zero_f_s,
zero_f,
r_d_fls,
pro_calc_ht_fls,
spro_calc_ht_fls,
fixture_date,
league_name
FROM temp.foul_announce
WHERE 1 = 1
AND COALESCE(fixt, 'A') <> 'A'
# AND ((m_ht_impact > 0.5 AND calc_ht_fls > 0.5) OR
#      (m_ht_impact > 0.4 AND calc_ht_fls > 0.8) OR
#      (m_ht_impact > 0.3 AND calc_ht_fls > 1))
ORDER BY timestamp, fixture_id, ffh desc, calc_ht_fls DESC)base
ORDER BY fixt, rnk
;

DROP TABLE IF EXISTS temp.ffh_data_analytics;

CREATE TABLE temp.ffh_data_analytics AS
SELECT
rf.fixture_id,
rf.fixt,
rf.player_name,
rf.team_name,
rf.player_pos,
rf.matchup_1,
rf.matchup_2,
last5_ht_foul,
ht_foul_matches_pct,
ht_foul_matches,
last5_start_foul,
ROUND(season_avg_fouls, 2) AS season_avg_fouls,
ROUND(avg_fouls_total, 2) AS avg_fouls_total,
zero_f_s AS matches_with_0_fouls_season_pct
FROM temp.raw_ffh rf
JOIN temp.ht_player_analytics hpa
ON rf.player_id = hpa.player_id
WHERE 1 = 1
# AND rf.fixture_id = 1208147
ORDER BY rnk;

INSERT INTO analytics.total_ht_datapoint (
    fixture_id,
    player_id,
    ffh_rnk,
    ffh,
    sfh_rnk,
    sfh,
    yc_rnk,
    ycf,
    player_pos,
    fouler_type,
    last5_start_foul,
    foul_ht,
    foul_ft,
    shot_ht,
    shot_ft,
    yc_ht,
    yc_ft
)
SELECT
    rf.fixture_id,
    rf.player_id,
    rf.rnk,
    rf.ffh,
    COALESCE(rs.rnk, 0),
    COALESCE(rs.exp_ht_shots, 0),
    COALESCE(pq.rnk, 99),
    COALESCE(pq.calc_metric, 0.0),
    rf.player_pos,
    rf.fouler_type,
    rf.last5_start_foul,
    0 AS foul_ht,
    0 AS foul_ft,
    0 AS shot_ht,
    0 AS shot_ft,
    0 AS yc_ht,
    0 AS yc_ft
FROM temp.raw_ffh rf
LEFT JOIN temp.raw_sfh rs
ON rf.player_id = rs.player_id AND rf.fixture_id = rs.fixture_id
LEFT JOIN temp.player_q pq
ON rf.player_id = pq.player_id AND rf.fixture_id = pq.fixture_id
INNER JOIN live_updates.live_fixtures lf
    ON rf.fixture_id = lf.fixture_id
WHERE 1 = 1
AND lf.status = 'NS'
ON DUPLICATE KEY UPDATE
    ffh_rnk = VALUES(ffh_rnk),
    ffh = VALUES(ffh),
    sfh_rnk = VALUES(sfh_rnk),
    sfh = VALUES(sfh),
    yc_rnk = VALUES(yc_rnk),
    ycf = VALUES(ycf),
    player_pos = VALUES(player_pos),
    fouler_type = VALUES(fouler_type)
;

