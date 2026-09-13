SELECT DISTINCT s.name AS skill
FROM users u
JOIN applications a ON a.user_id = u.id
JOIN application_skills x ON x.application_id = a.id
JOIN skills s ON s.id = x.skill_id
WHERE u.full_name = 'Ana Putri'
ORDER BY skill;
