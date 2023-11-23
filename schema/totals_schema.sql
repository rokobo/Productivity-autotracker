CREATE VIEW totals AS
WITH RECURSIVE date_series (day) AS (
    SELECT date('now', (SELECT value FROM settings WHERE label="total_offset"), '-363 days') UNION ALL SELECT date(day, '+1 day')
    FROM date_series
    WHERE day < date('now', (SELECT value FROM settings WHERE label="total_offset"))
)
SELECT ds.day,
    COALESCE(SUM(CASE WHEN c.category = 'Neutral' AND c.process_name != "IDLE TIME" THEN c.total ELSE 0 END), 0) AS Neutral,
    COALESCE(SUM(CASE WHEN c.category = 'Personal' THEN c.total ELSE 0 END), 0) AS Personal,
    COALESCE(SUM(CASE WHEN c.category = 'Work' THEN c.total ELSE 0 END), 0) AS Work
FROM date_series ds LEFT JOIN categories c ON ds.day = c.day
GROUP BY ds.day
