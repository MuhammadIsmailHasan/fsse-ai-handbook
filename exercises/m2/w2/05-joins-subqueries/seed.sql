-- Fictional CareerPilot data for JOIN practice. Loaded automatically by the tests.
CREATE TABLE users (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name text NOT NULL,
    city text
);
CREATE TABLE companies (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL UNIQUE,
    industry text NOT NULL
);
CREATE TABLE applications (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id bigint NOT NULL REFERENCES users (id),
    company_id bigint NOT NULL REFERENCES companies (id),
    role_title text NOT NULL,
    status text NOT NULL CHECK (status IN ('applied', 'interview', 'offer', 'rejected')),
    applied_on date NOT NULL,
    salary_offer bigint
);
CREATE TABLE skills (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL UNIQUE
);
CREATE TABLE application_skills (
    application_id bigint NOT NULL REFERENCES applications (id),
    skill_id bigint NOT NULL REFERENCES skills (id),
    PRIMARY KEY (application_id, skill_id)
);

INSERT INTO users (full_name, city) VALUES
    ('Ana Putri', 'Jakarta'),       -- 1
    ('Budi Santoso', 'Bandung'),    -- 2
    ('Citra Lestari', 'Jakarta'),   -- 3
    ('Dewi Anggraini', NULL);       -- 4 (no applications)

INSERT INTO companies (name, industry) VALUES
    ('Nusantara Tech', 'Software'),  -- 1
    ('Kopi Data', 'Analytics'),      -- 2
    ('Lintas AI', 'AI'),             -- 3
    ('Garuda Pay', 'Fintech'),       -- 4
    ('Batik Soft', 'Software');      -- 5 (no applications)

INSERT INTO applications (user_id, company_id, role_title, status, applied_on, salary_offer) VALUES
    (1, 1, 'Backend Engineer',     'interview', '2026-08-20', NULL),      -- 1
    (1, 3, 'AI Engineer',          'offer',     '2026-08-10', 18000000),  -- 2
    (1, 2, 'Data Analyst',         'rejected',  '2026-08-01', NULL),      -- 3
    (2, 2, 'Data Analyst',         'applied',   '2026-09-01', NULL),      -- 4
    (2, 4, 'QA Engineer',          'interview', '2026-08-25', NULL),      -- 5
    (3, 3, 'ML Engineer',          'offer',     '2026-08-15', 21000000),  -- 6
    (3, 1, 'Frontend Developer',   'applied',   '2026-09-05', NULL),      -- 7
    (3, 4, 'Backend Engineer',     'rejected',  '2026-07-30', NULL),      -- 8
    (2, 3, 'AI Engineer',          'offer',     '2026-09-02', 16000000);  -- 9

INSERT INTO skills (name) VALUES ('python'), ('sql'), ('react'), ('docker'), ('llm'), ('go');

INSERT INTO application_skills (application_id, skill_id) VALUES
    (1, 1), (1, 2), (1, 4),
    (2, 1), (2, 5),
    (3, 2),
    (4, 2), (4, 1),
    (5, 1),
    (6, 1), (6, 5), (6, 4),
    (7, 3),
    (8, 1), (8, 2),
    (9, 1), (9, 5);
