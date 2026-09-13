-- The four queries your indexes must speed up (the tests run these with EXPLAIN).

-- Q1: a user's latest applications (application list page)
SELECT id, status, created_at FROM applications WHERE user_id = 1234 ORDER BY created_at DESC LIMIT 20;

-- Q2: login by email, case-insensitive
SELECT id, full_name FROM users WHERE lower(email) = lower('user4321@mail.com');

-- Q3: follow-up reminders due today (only active applications have follow-ups)
SELECT id, user_id FROM applications WHERE status IN ('applied', 'interview') AND follow_up_on = DATE '2026-09-20';

-- Q4: applications for one company (company page)
SELECT COUNT(*) FROM applications WHERE company_id = 42;
