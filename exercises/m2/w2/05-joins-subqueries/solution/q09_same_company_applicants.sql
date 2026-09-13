-- Self-join: the applications table joined to itself.
SELECT DISTINCT c.name AS company, ua.full_name AS user_a, ub.full_name AS user_b
FROM applications a1
JOIN applications a2 ON a2.company_id = a1.company_id AND a2.user_id <> a1.user_id
JOIN users ua ON ua.id = a1.user_id
JOIN users ub ON ub.id = a2.user_id
JOIN companies c ON c.id = a1.company_id
WHERE ua.full_name < ub.full_name
ORDER BY company, user_a, user_b;
