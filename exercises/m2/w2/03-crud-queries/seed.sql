-- Fictional CareerPilot data for query practice. Loaded automatically by the tests.
CREATE TABLE job_listings (
    id           bigint      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title        text        NOT NULL,
    company      text        NOT NULL,
    city         text,
    is_remote    boolean     NOT NULL DEFAULT false,
    salary_min   bigint,
    salary_max   bigint,
    posted_on    date        NOT NULL,
    status       text        NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'closed')),
    created_at   timestamptz NOT NULL DEFAULT now()
);

INSERT INTO job_listings (title, company, city, is_remote, salary_min, salary_max, posted_on, status) VALUES
    ('Junior Backend Engineer',   'Nusantara Tech', 'Jakarta',    true,  9000000,  14000000, '2026-09-01', 'open'),
    ('Data Analyst',              'Kopi Data',      'Bandung',    false, 7000000,  10000000, '2026-08-28', 'open'),
    ('Frontend Developer',        'Batik Soft',     'Jakarta',    false, 8000000,  13000000, '2026-09-05', 'open'),
    ('ML Engineer',               'Lintas AI',      'Jakarta',    true,  15000000, 25000000, '2026-09-10', 'open'),
    ('QA Engineer',               'Awan Cloud',     'Surabaya',   false, NULL,     NULL,     '2026-08-15', 'closed'),
    ('Full-Stack Developer',      'Rempah Digital', 'Yogyakarta', true,  9000000,  15000000, '2026-08-30', 'open'),
    ('DevOps Engineer',           'Awan Cloud',     'Jakarta',    false, 14000000, 22000000, '2026-09-08', 'open'),
    ('Backend Engineer (Go)',     'Garuda Pay',     'Jakarta',    false, 13000000, 20000000, '2026-09-03', 'closed'),
    ('AI Engineer',               'Lintas AI',      'Bandung',    true,  14000000, 21000000, '2026-09-11', 'open'),
    ('Junior Data Engineer',      'Kopi Data',      'Jakarta',    false, 8000000,  11000000, '2026-08-30', 'open'),
    ('Mobile Developer',          'Sambal Apps',    'Surabaya',   false, 9000000,  14000000, '2026-08-20', 'open'),
    ('Frontend Engineer',         'Garuda Pay',     NULL,         true,  NULL,     NULL,     '2026-09-09', 'open'),
    ('Backend Developer',         'Rempah Digital', 'Yogyakarta', false, 7000000,  11000000, '2026-08-25', 'closed'),
    ('Site Reliability Engineer', 'Nusantara Tech', 'Jakarta',    false, 16000000, 24000000, '2026-09-07', 'open'),
    ('Junior Full-Stack Developer','Batik Soft',    'Bandung',    true,  6000000,  9000000,  '2026-09-04', 'open');
