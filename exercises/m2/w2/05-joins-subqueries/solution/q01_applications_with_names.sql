SELECT u.full_name, c.name AS company, a.role_title
FROM applications a
JOIN users u ON u.id = a.user_id
JOIN companies c ON c.id = a.company_id
ORDER BY u.full_name, c.name;
