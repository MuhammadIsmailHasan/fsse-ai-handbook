-- WHERE filters rows before grouping; HAVING filters the groups afterwards.
SELECT city, ROUND(AVG(salary_max)) AS avg_max
FROM job_listings
WHERE city IS NOT NULL AND salary_max IS NOT NULL
GROUP BY city
HAVING COUNT(*) >= 3
ORDER BY avg_max DESC;
