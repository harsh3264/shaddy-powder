TRUNCATE temp.new_tele_fixtures;

INSERT INTO temp.new_tele_fixtures
SELECT fixture_id
FROM live_updates.live_fixtures
WHERE 1 = 1
AND status = 'NS'
AND fixture_id IN (SELECT fixture_id FROM temp.raw_ffh WHERE player_pos IS NOT NULL)
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
