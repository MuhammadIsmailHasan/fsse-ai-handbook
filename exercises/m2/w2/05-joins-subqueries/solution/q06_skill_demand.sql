SELECT s.name AS skill, COUNT(x.application_id) AS applications
FROM skills s
LEFT JOIN application_skills x ON x.skill_id = s.id
GROUP BY s.id, s.name
ORDER BY applications DESC, skill;
