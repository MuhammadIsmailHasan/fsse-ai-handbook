-- Reference solution.

-- Q1: equality on user_id, then ordered by created_at → one composite index serves both,
-- and LIMIT 20 can stop after reading 20 index entries.
CREATE INDEX applications_user_created_idx ON applications (user_id, created_at DESC);

-- Q2: the query uses lower(email), so the index must be on the same EXPRESSION.
CREATE INDEX users_email_lower_idx ON users (lower(email));

-- Q3: partial index — only rows the query can ever match are indexed.
CREATE INDEX applications_follow_up_active_idx ON applications (follow_up_on)
    WHERE status IN ('applied', 'interview');

-- Q4: plain index on the foreign-key-like column; COUNT(*) can use an index-only scan.
CREATE INDEX applications_company_id_idx ON applications (company_id);
