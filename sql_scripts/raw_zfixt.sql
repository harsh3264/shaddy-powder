-- Daily Important Fixtures

-- TRUNCATE temp.important_fixtures;

-- INSERT INTO temp.important_fixtures 
-- SELECT fixture_id
-- FROM today_fixture
-- WHERE 1 = 1
-- AND fixture_id IN (
-- 1216059,
-- 1213868,
-- 1213865,
-- 1224084,
-- 1223739,
-- 1223735,
-- 1208631 -- Update this on daily basis
-- )
-- ;

TRUNCATE temp.new_tele_fixtures;

INSERT INTO temp.new_tele_fixtures
SELECT fixture_id
FROM live_updates.live_fixtures
WHERE 1 = 1
AND status = 'NS'
AND fixture_id IN (SELECT fixture_id FROM temp.raw_ffh WHERE player_pos IS NOT NULL)
AND fixture_id IN (SELECT fixture_id FROM temp.important_fixtures)
AND fixture_id NOT IN (SELECT fixture_id FROM temp.tele_fixtures WHERE 1 = 1)
GROUP BY 1
;

INSERT INTO temp.tele_fixtures
SELECT fixture_id
FROM live_updates.live_fixtures
WHERE 1 = 1
AND status = 'NS'
AND fixture_id IN (SELECT fixture_id FROM temp.raw_ffh WHERE player_pos IS NOT NULL)
GROUP BY 1
;
