DROP TABLE IF EXISTS "settings";
CREATE TABLE IF NOT EXISTS "settings" (
    label TEXT NOT NULL,
    value NOT NULL,
    UNIQUE(label)
)
