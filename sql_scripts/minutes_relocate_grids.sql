
DROP TABLE IF EXISTS temp.base_lineups;

CREATE TABLE temp.base_lineups AS (
    SELECT
        ngm.fixture_id,
        ngm.team_id,
        p.name,
        ngm.player_id,
        new_grid,
        x_grid,
        y_grid,
        (61 - x_grid) AS inverse_x,
        (61 - y_grid) AS inverse_y,
        fl.grid,
        fl.player_pos
    FROM
        temp.new_grid_map ngm
        LEFT JOIN players p ON ngm.player_id = p.player_id
        LEFT JOIN fixture_lineups fl on ngm.player_id = fl.player_id AND ngm.fixture_id = fl.fixture_id
    WHERE
        1 = 1
    AND ngm.fixture_id IN (SELECT fixture_id FROM live_updates.live_fixture_lineups)
#     AND ngm.fixture_id IN (1035345)
#     AND ngm.team_id IN (52)
);

DROP TABLE IF EXISTS temp.DIST_MAP;

CREATE TABLE temp.DIST_MAP AS
SELECT
    t1.fixture_id,
    t1.team_id AS team_id_t1,
    t1.name AS player_name_t1,
    t1.player_id AS player_id_t1,
    t1.new_grid AS new_grid_t1,
    t1.x_grid AS x_grid_t1,
    t1.y_grid AS y_grid_t1,
    t2.team_id AS team_id_t2,
    t2.name AS player_name_t2,
    t2.player_id AS player_id_t2,
    t2.new_grid AS new_grid_t2,
    t2.x_grid AS x_grid_t2,
    t2.y_grid AS y_grid_t2,
    SQRT(POW(t1.inverse_x - t2.x_grid, 2) + POW(t1.inverse_y - t2.y_grid, 2)) AS distance
FROM
    temp.base_lineups t1
JOIN
    temp.base_lineups t2 ON t1.fixture_id = t2.fixture_id AND t1.team_id <> t2.team_id
ORDER BY
    t1.team_id, t1.x_grid, t1.y_grid, distance;

DROP TABLE IF EXISTS temp.DISTANCE_BASE_PLAYERS;

CREATE TABLE temp.DISTANCE_BASE_PLAYERS AS
SELECT
    t.fixture_id,
    t.team_id_t1,
    t2.name,
    t.player_name_t1,
    t.player_id_t1,
    t.team_id_t2,
    MAX(CASE WHEN tr = 1 THEN t.player_name_t2 END) AS nn1,
    MAX(CASE WHEN tr = 2 THEN t.player_name_t2 END) AS nn2,
    MAX(CASE WHEN tr = 1 THEN ROUND(t.distance, 2) END) AS dist_nn1,
    MAX(CASE WHEN tr = 2 THEN ROUND(t.distance, 2) END) AS dist_nn2,
    MAX(CASE WHEN tr = 1 THEN t.player_id_t2 END) AS pid_nn1,
    MAX(CASE WHEN tr = 2 THEN t.player_id_t2 END) AS pid_nn2
FROM
(SELECT dm.*,
       row_number() over (partition by player_id_t1 order by distance) AS tr
FROM temp.DIST_MAP dm
) t
JOIN teams t2 ON t.team_id_t1 = t2.team_id
WHERE tr < 3
GROUP BY 1, 2, 3, 4, 5, 6
ORDER BY fixture_id, team_id_t1, player_id_t1, distance
;

DROP TABLE IF EXISTS temp.FOUL_DRAWN_MAP;

CREATE TABLE temp.FOUL_DRAWN_MAP AS
SELECT
tt.fixture_id,
tt.team_id_t1,
tt.name,
tt.player_id_t1 AS player_id,
tt.player_name_t1 AS player_name,
tt.nn1,
tt.pid_nn1,
tt.dist_nn1,
MAX(ROUND(mpv1.total_exp_ht_fouls_drawn, 1)) AS nn1_fld,
MAX(ROUND(mpv1.season_exp_ht_fouls_drawn, 1)) AS nn1_fld_s,
tt.nn2,
tt.pid_nn2,
tt.dist_nn2,
MAX(ROUND(mpv2.total_exp_ht_fouls_drawn, 1)) AS nn2_fld,
MAX(ROUND(mpv2.season_exp_ht_fouls_drawn, 1)) AS nn2_fld_s
FROM temp.DISTANCE_BASE_PLAYERS tt
JOIN temp.exp_ht_fouls mpv1 on tt.pid_nn1 = mpv1.player_id
JOIN temp.exp_ht_fouls mpv2 on tt.pid_nn2 = mpv2.player_id
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13
ORDER BY fixture_id, tt.team_id_t1
;