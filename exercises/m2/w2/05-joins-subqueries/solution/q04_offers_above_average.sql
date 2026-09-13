SELECT u.full_name, c.name AS company, a.salary_offer
FROM applications a
JOIN users u ON u.id = a.user_id
JOIN companies c ON c.id = a.company_id
WHERE a.salary_offer > (SELECT AVG(salary_offer) FROM applications WHERE status = 'offer')
ORDER BY a.salary_offer DESC;
