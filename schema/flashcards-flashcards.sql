CREATE TABLE IF NOT EXISTS "flashcards" (
    "question" TEXT,
    "deck_name" TEXT,
    "last_access" REAL,
    "access_interval" REAL,
    "ease_factor" REAL,
    "next_access" REAL,
    "answer" TEXT
);
