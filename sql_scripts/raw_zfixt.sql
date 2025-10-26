-- Daily Important Fixtures

-- TRUNCATE temp.important_fixtures;

-- INSERT INTO temp.important_fixtures 
-- SELECT fixture_id
-- FROM today_fixture
-- WHERE 1 = 1
-- AND fixture_id IN (
-- 1345745,
-- 1345747,
-- 1345749,
-- 1345751,
-- 1208166 -- Update this on daily basis
-- )
-- ;

TRUNCATE temp.new_tele_fixtures;

INSERT INTO temp.new_tele_fixtures
SELECT fixture_id
FROM live_updates.live_fixtures
WHERE 1 = 1
AND status = 'NS'
AND LENGTH(COALESCE(referee, 'aa')) > 3
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
