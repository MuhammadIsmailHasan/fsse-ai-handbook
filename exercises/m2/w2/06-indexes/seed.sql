-- Generates enough data for the query planner to care about indexes (deterministic, no randomness).
CREATE TABLE users (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email      text   NOT NULL,
    full_name  text   NOT NULL
);

CREATE TABLE applications (
    id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id       bigint NOT NULL REFERENCES users (id),
    company_id    bigint NOT NULL,
    status        text   NOT NULL,
    follow_up_on  date,
    created_at    timestamptz NOT NULL
);

INSERT INTO users (email, full_name)
SELECT 'User' || g || '@Mail.com', 'User ' || g
FROM generate_series(1, 5000) AS g;

INSERT INTO applications (user_id, company_id, status, follow_up_on, created_at)
SELECT (g % 5000) + 1,
       (g % 300) + 1,
       (ARRAY['applied', 'interview', 'offer', 'rejected', 'rejected', 'rejected'])[(g % 6) + 1],
       CASE WHEN g % 6 < 2 THEN DATE '2026-09-01' + (g % 60) END,
       TIMESTAMPTZ '2026-01-01' + (g || ' minutes')::interval
FROM generate_series(1, 60000) AS g;
