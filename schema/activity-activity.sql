CREATE TABLE IF NOT EXISTS "activity" (
    start_time INTEGER NOT NULL,
    end_time INTEGER NOT NULL,
    app TEXT DEFAULT "" NOT NULL,
    info TEXT DEFAULT "" NOT NULL,
    process_name TEXT NOT NULL,
    url TEXT DEFAULT "" NOT NULL,
    domain TEXT DEFAULT "" NOT NULL,
    duration INTEGER GENERATED ALWAYS AS (
        end_time - start_time
    ) STORED NOT NULL,
    total REAL GENERATED ALWAYS AS (
        duration / 3600.0
    ) STORED NOT NULL
)
