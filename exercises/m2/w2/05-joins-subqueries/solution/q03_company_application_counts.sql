-- COUNT(a.id) counts only matched rows, so companies with none get 0 (COUNT(*) would give 1).
SELECT c.name AS company, COUNT(a.id) AS applications
FROM companies c
LEFT JOIN applications a ON a.company_id = c.id
GROUP BY c.id, c.name
ORDER BY applications DESC, company;
