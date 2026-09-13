SELECT title, posted_on
FROM job_listings
WHERE status = 'open'
ORDER BY posted_on DESC
LIMIT 3;
