UPDATE job_listings
SET status = 'closed'
WHERE status = 'open' AND posted_on < '2026-08-29'
RETURNING title;
