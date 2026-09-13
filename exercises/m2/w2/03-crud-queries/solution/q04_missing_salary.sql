-- `= NULL` never matches; use IS NULL.
SELECT title
FROM job_listings
WHERE salary_max IS NULL
ORDER BY title;
