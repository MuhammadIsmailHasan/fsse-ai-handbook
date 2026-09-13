INSERT INTO job_listings (title, company, city, is_remote, salary_min, salary_max, posted_on)
VALUES ('Platform Engineer', 'Garuda Pay', 'Jakarta', false, 17000000, 26000000, '2026-09-13')
RETURNING id, title, status;
