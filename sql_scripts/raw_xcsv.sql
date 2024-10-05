DROP TABLE IF EXISTS temp.csv_upload;

CREATE TABLE temp.csv_upload AS
SELECT
    tf.fixt,
    COALESCE(MAX(CASE WHEN rf.rnk = 1 THEN rf.player_name END), 'NA') AS fp1,
    COALESCE(MAX(CASE WHEN rf.rnk = 2 THEN rf.player_name END), 'NA') AS fp2,
    COALESCE(MAX(CASE WHEN rf.rnk = 3 THEN rf.player_name END), 'NA') AS fp3,
    COALESCE(MAX(CASE WHEN rf.rnk = 4 THEN rf.player_name END), 'NA') AS fp4,
    COALESCE(MAX(CASE WHEN rf.rnk = 5 THEN rf.player_name END), 'NA') AS fp5,
    COALESCE(MAX(CASE WHEN rf.rnk = 1 THEN rf.team_name END), 'NA') AS ft1,
    COALESCE(MAX(CASE WHEN rf.rnk = 2 THEN rf.team_name END), 'NA') AS ft2,
    COALESCE(MAX(CASE WHEN rf.rnk = 3 THEN rf.team_name END), 'NA') AS ft3,
    COALESCE(MAX(CASE WHEN rf.rnk = 4 THEN rf.team_name END), 'NA') AS ft4,
    COALESCE(MAX(CASE WHEN rf.rnk = 5 THEN rf.team_name END), 'NA') AS ft5,
    COALESCE(MAX(CASE WHEN rf.rnk = 1 THEN rf.player_pos END), 'NA') AS fps1,
    COALESCE(MAX(CASE WHEN rf.rnk = 2 THEN rf.player_pos END), 'NA') AS fps2,
    COALESCE(MAX(CASE WHEN rf.rnk = 3 THEN rf.player_pos END), 'NA') AS fps3,
    COALESCE(MAX(CASE WHEN rf.rnk = 4 THEN rf.player_pos END), 'NA') AS fps4,
    COALESCE(MAX(CASE WHEN rf.rnk = 5 THEN rf.player_pos END), 'NA') AS fps5,
    COALESCE(MAX(CASE WHEN rs.rnk = 1 THEN rs.player_name END), 'NA') AS sp1,
    COALESCE(MAX(CASE WHEN rs.rnk = 2 THEN rs.player_name END), 'NA') AS sp2,
    COALESCE(MAX(CASE WHEN rs.rnk = 3 THEN rs.player_name END), 'NA') AS sp3,
    COALESCE(MAX(CASE WHEN rs.rnk = 4 THEN rs.player_name END), 'NA') AS sp4,
    COALESCE(MAX(CASE WHEN rs.rnk = 5 THEN rs.player_name END), 'NA') AS sp5,
    COALESCE(MAX(CASE WHEN rs.rnk = 1 THEN rs.team_name END), 'NA') AS st1,
    COALESCE(MAX(CASE WHEN rs.rnk = 2 THEN rs.team_name END), 'NA') AS st2,
    COALESCE(MAX(CASE WHEN rs.rnk = 3 THEN rs.team_name END), 'NA') AS st3,
    COALESCE(MAX(CASE WHEN rs.rnk = 4 THEN rs.team_name END), 'NA') AS st4,
    COALESCE(MAX(CASE WHEN rs.rnk = 5 THEN rs.team_name END), 'NA') AS st5,
    COALESCE(MAX(CASE WHEN rs.rnk = 1 THEN rs.position END), 'NA') AS sps1,
    COALESCE(MAX(CASE WHEN rs.rnk = 2 THEN rs.position END), 'NA') AS sps2,
    COALESCE(MAX(CASE WHEN rs.rnk = 3 THEN rs.position END), 'NA') AS sps3,
    COALESCE(MAX(CASE WHEN rs.rnk = 4 THEN rs.position END), 'NA') AS sps4,
    COALESCE(MAX(CASE WHEN rs.rnk = 5 THEN rs.position END), 'NA') AS sps5,
    COALESCE(MAX(CASE WHEN pq.rnk = 1 THEN pq.player_name END), 'NA') AS yp1,
    COALESCE(MAX(CASE WHEN pq.rnk = 2 THEN pq.player_name END), 'NA') AS yp2,
    COALESCE(MAX(CASE WHEN pq.rnk = 3 THEN pq.player_name END), 'NA') AS yp3,
    COALESCE(MAX(CASE WHEN pq.rnk = 1 THEN pq.team_name END), 'NA') AS yt1,
    COALESCE(MAX(CASE WHEN pq.rnk = 2 THEN pq.team_name END), 'NA') AS yt2,
    COALESCE(MAX(CASE WHEN pq.rnk = 3 THEN pq.team_name END), 'NA') AS yt3,
    COALESCE(MAX(CASE WHEN pq.rnk = 1 THEN rf2.player_pos END), 'NA') AS yps1,
    COALESCE(MAX(CASE WHEN pq.rnk = 2 THEN rf2.player_pos END), 'NA') AS yps2,
    COALESCE(MAX(CASE WHEN pq.rnk = 3 THEN rf2.player_pos END), 'NA') AS yps3
FROM today_fixture tf
INNER JOIN live_updates.live_fixtures lf
    ON tf.fixture_id = lf.fixture_id
LEFT JOIN temp.raw_ffh rf
    ON tf.fixture_id = rf.fixture_id
LEFT JOIN temp.raw_sfh rs
    ON tf.fixture_id = rs.fixture_id
LEFT JOIN temp.player_q pq
    ON tf.fixture_id = pq.fixture_id
LEFT JOIN temp.raw_ffh rf2
    ON pq.fixture_id = rf2.fixture_id
    AND pq.player_id = rf2.player_id
WHERE 1 = 1
    AND tf.fixture_date = CURRENT_DATE
    AND lf.status = 'NS'
GROUP BY 1
;