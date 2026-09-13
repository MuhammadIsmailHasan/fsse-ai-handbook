SELECT title, salary_max
FROM job_listings
WHERE salary_max BETWEEN 13000000 AND 21000000
ORDER BY salary_max DESC, title;
