-- Reference solution.
CREATE TABLE study_log (
    id          bigint      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    topic       text        NOT NULL,
    minutes     integer     NOT NULL CONSTRAINT study_log_minutes_range CHECK (minutes BETWEEN 1 AND 600),
    studied_on  date        NOT NULL DEFAULT CURRENT_DATE,
    mood        text        CONSTRAINT study_log_mood_values CHECK (mood IN ('great', 'ok', 'tired')),
    created_at  timestamptz NOT NULL DEFAULT now()
);

INSERT INTO study_log (topic, minutes, mood) VALUES
    ('Git fundamentals', 90, 'great'),
    ('Docker basics', 120, 'ok'),
    ('PostgreSQL setup', 60, NULL);
