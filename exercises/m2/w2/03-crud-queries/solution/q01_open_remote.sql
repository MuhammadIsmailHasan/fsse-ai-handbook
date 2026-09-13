SELECT title, company
FROM job_listings
WHERE status = 'open' AND is_remote
ORDER BY title;
