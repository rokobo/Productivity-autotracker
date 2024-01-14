CREATE VIEW totals AS
WITH RECURSIVE date_series (day) AS (
    SELECT date('now', (SELECT value FROM settings WHERE label="total_offset"), '-363 days') UNION ALL SELECT date(day, '+1 day')
    FROM date_series
    WHERE day < date('now', (SELECT value FROM settings WHERE label="total_offset"))
)
SELECT ds.day,
    COALESCE(SUM(CASE WHEN c.category = 'Neutral' AND c.process_name != "IDLE TIME" THEN c.total ELSE 0 END), 0) AS Neutral,
    COALESCE(SUM(CASE WHEN c.category = 'Personal' THEN c.total ELSE 0 END), 0) AS Personal,
    COALESCE(SUM(CASE WHEN c.category = 'Work' THEN c.total ELSE 0 END), 0) AS Work,
    CAST(julianday('now') - julianday(ds.day) AS INTEGER) as days_since,
    CASE strftime('%w', ds.day)
        WHEN '0' THEN 'Sunday'
        WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday'
        WHEN '6' THEN 'Saturday'
    END AS weekday,
    strftime('%w', ds.day) AS weekday_num
FROM date_series ds
LEFT JOIN categories c ON ds.day = c.day
GROUP BY ds.day
