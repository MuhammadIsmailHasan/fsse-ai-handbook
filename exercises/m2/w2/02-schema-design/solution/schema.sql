-- Reference solution.
CREATE TABLE users (
    id          bigint      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email       text        NOT NULL,
    full_name   text        NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now()
);

-- Case-insensitive uniqueness: 'Ana@Mail.com' and 'ana@mail.com' collide.
CREATE UNIQUE INDEX users_email_lower_key ON users (lower(email));

CREATE TABLE companies (
    id          bigint      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        text        NOT NULL CONSTRAINT companies_name_key UNIQUE,
    website     text,
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE applications (
    id                  bigint      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id             bigint      NOT NULL REFERENCES users (id),
    company_id          bigint      NOT NULL REFERENCES companies (id),
    role_title          text        NOT NULL CONSTRAINT applications_role_title_not_blank CHECK (length(trim(role_title)) > 0),
    status              text        NOT NULL DEFAULT 'applied'
                        CONSTRAINT applications_status_valid
                        CHECK (status IN ('wishlist', 'applied', 'interview', 'offer', 'rejected', 'withdrawn')),
    applied_on          date,
    salary_expectation  bigint      CONSTRAINT applications_salary_non_negative CHECK (salary_expectation >= 0),
    notes               text,
    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT applications_unique_role_per_company UNIQUE (user_id, company_id, role_title)
);
