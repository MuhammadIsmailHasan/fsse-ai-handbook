SELECT city, COUNT(*) AS total
FROM job_listings
WHERE city IS NOT NULL
GROUP BY city
ORDER BY total DESC, city;
