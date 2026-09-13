-- Provided: the core tables from exercise 02. Loaded by the tests before your relationships.sql.
CREATE TABLE users (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email       text   NOT NULL,
    full_name   text   NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX users_email_lower_key ON users (lower(email));

CREATE TABLE companies (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        text   NOT NULL UNIQUE,
    created_at  timestamptz NOT NULL DEFAULT now()
);
