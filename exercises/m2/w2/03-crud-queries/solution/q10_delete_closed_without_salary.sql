DELETE FROM job_listings
WHERE status = 'closed' AND salary_max IS NULL
RETURNING title;
