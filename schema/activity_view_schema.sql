CREATE VIEW activity_view AS
SELECT *,
    strftime('%Y-%m-%d', start_time + (3600 * (SELECT value FROM settings WHERE label="gmt_offset")), 'unixepoch') as day
FROM activity
