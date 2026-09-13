-- Reference solution.

-- One-to-many: users → applications, companies → applications
CREATE TABLE applications (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id     bigint NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    company_id  bigint NOT NULL REFERENCES companies (id) ON DELETE RESTRICT,
    role_title  text   NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now()
);
-- PostgreSQL does NOT index foreign key columns automatically.
CREATE INDEX applications_user_id_idx ON applications (user_id);
CREATE INDEX applications_company_id_idx ON applications (company_id);

CREATE TABLE skills (
    id    bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name  text   NOT NULL UNIQUE
);

-- Many-to-many: a junction table with a composite primary key
CREATE TABLE application_skills (
    application_id  bigint NOT NULL REFERENCES applications (id) ON DELETE CASCADE,
    skill_id        bigint NOT NULL REFERENCES skills (id) ON DELETE RESTRICT,
    level           text   NOT NULL CHECK (level IN ('nice_to_have', 'required')),
    PRIMARY KEY (application_id, skill_id)
);
-- application_id is covered by the primary key index (first column); skill_id is not.
CREATE INDEX application_skills_skill_id_idx ON application_skills (skill_id);

CREATE TABLE interviews (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    application_id  bigint NOT NULL REFERENCES applications (id) ON DELETE CASCADE,
    scheduled_at    timestamptz NOT NULL
);
CREATE INDEX interviews_application_id_idx ON interviews (application_id);

-- One-to-one: the foreign key IS the primary key
CREATE TABLE user_profiles (
    user_id       bigint PRIMARY KEY REFERENCES users (id) ON DELETE CASCADE,
    headline      text,
    linkedin_url  text
);
